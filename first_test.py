import asyncio
import sys
from decouple import config
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout, Page


# ── Configuration (loaded from .env) ─────────────────────────────────────────
ENDPOINT_URL  = config("ENDPOINT_URL")
PROFILE_PATH  = config("PROFILE_PATH")
TARGET_URL    = config("TARGET_URL", default="")
WEBSITE_URL    = config("WEBSITE_URL", default="")
OUTPUT_DIR    = config("OUTPUT_DIR", default="")
MODAL_SETTLE_MS = config("MODAL_SETTLE_MS", cast=int, default=1200)

# UUID regex — matches bare question wrapper IDs (36-char hex, no suffix)
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


# ── Per-question capture ──────────────────────────────────────────────────────
async def capture_question_card(page: Page, uuid: str, index: int, output_dir: Path):
    """Screenshot one question card and its Mark Scheme modal."""

    q_num = f"{index:02d}"
    print(f"  [{q_num}] uuid={uuid[:8]}...", end="  ", flush=True)

    # Locate wrapper and inner card by their stable IDs
    question = page.locator(f'[id="{uuid}-question-content"]')
    card = question.locator('div.css-5nr4ri.css-1ma9zj9')

    q_path = output_dir / f"q{q_num}_question.png"
    await card.screenshot(path=str(q_path))

    # 1. Screenshot the question card
    print(f"question ✓", end="  ", flush=True)

    # 2. Click the Mark Scheme button scoped to this card
    mark_scheme_btn = question.locator('[data-analytics-name="clickMarkScheme"]')
    await mark_scheme_btn.click()
    
    await page.evaluate("""
    () => {
        // Remove old clone if exists
        const old = document.getElementById('__PW_CAPTURE_ROOT__');
        if (old) old.remove();

        // Original content
        const original = document.querySelector(
            'div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-6.css-106flku div.css-5nr4ri.css-1ma9zj9'
        );

        // Clone it
        const clone = original.cloneNode(true);

        // Wrapper
        const wrapper = document.createElement('div');
        wrapper.id = '__PW_CAPTURE_ROOT__';

        wrapper.style.position = 'absolute';
        wrapper.style.top = '0';
        wrapper.style.left = '0';
        wrapper.style.zIndex = '999999';

        wrapper.style.background = 'white';

        wrapper.style.width = original.offsetWidth + 'px';

        wrapper.style.height = 'auto';
        wrapper.style.maxHeight = 'none';
        wrapper.style.overflow = 'visible';

        wrapper.appendChild(clone);

        document.body.appendChild(wrapper);
    }
    """)
    
    capture = page.locator('#__PW_CAPTURE_ROOT__')

    await capture.wait_for(state="visible")

    a_path = output_dir / f"q{q_num}_answer.png"

    await capture.screenshot(
        path=str(a_path)
    )
    
    await page.evaluate("""
    () => {
        const el = document.getElementById('__PW_CAPTURE_ROOT__');
        if (el) el.remove();
    }
    """)   

    # 5. Close the modal before moving to the next question
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(400)


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    # OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        print("\n✨  Just a simple Python automation made with slop")
        print("\n🔗  Connecting to \033[0;33m Chromium-based browser's\033[0m debug session...")
        try:
            browser = await p.chromium.connect_over_cdp(ENDPOINT_URL)
        except Exception as e:
            print(
                f"\n❌  Could not connect to browser at {ENDPOINT_URL}\n"
                f"    Error: {e}\n"
                f"    Make sure your Chromium-based browser is running with --remote-debugging-port=9222\n"
            )
            sys.exit(1)

        default_context = browser.contexts[0]

        # Find the website's tab
        page = next(
            (pg for pg in default_context.pages if WEBSITE_URL in pg.url),
            None
        )
        if page is None:
            print("❌  No website tab found. Please open the exam page in Chromium first.")
            await browser.close()
            sys.exit(1)

        print(f"📄  Found tab: {page.url}")

        if TARGET_URL:
            print(f"📄  Navigating to: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="networkidle")

        print(
            "\n──────────────────────────────────────────────\n"
            "  Confirm the page shows the correct filtered\n"
            "  question list, then press ENTER to start.\n"
            "──────────────────────────────────────────────"
        )
        input()

        # Discover all question wrapper UUIDs from the DOM
        raw_uuids = await page.evaluate("""
        [...document.querySelectorAll('[id]')]
        .map(el => el.id)
        .filter(id => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id))
        """)

        # Deduplicate while preserving order, in case modal DOM injection adds duplicates
        seen = set()
        uuids = [u for u in raw_uuids if not (u in seen or seen.add(u))]

        if not uuids:
            print(
                "❌  No question wrappers found.\n"
                "    Make sure the page is fully loaded and questions are visible.\n"
            )
            await browser.close()
            return

        # Name a directory if not setup in .env file
        user_out_dir = Path(OUTPUT_DIR) if OUTPUT_DIR else Path(f"outputs/{input("\033[0;33m[system]\033[0m No directory configured. Enter folder name => outputs/")}")

        print(f"\n✅  Found {len(uuids)} question(s).\n")
        print(f"🛠️  Closing open modal if any...\n")
        await page.keyboard.press("Escape")
        
        # Remove header first
        await page.add_style_tag(content="header { display: none !important; }")

        for i, uuid in enumerate(uuids):
            try:
                print(uuid)
                await capture_question_card(page, uuid, i + 1, user_out_dir)
            except Exception as e:
                print(f"\n⚠️  Error on question {i + 1}: {e}")
                # Best-effort modal cleanup before continuing
                try:
                    close_btn = page.locator('[data-testid="CloseIcon"]').first
                    if await close_btn.is_visible():
                        await close_btn.click()
                        await page.wait_for_timeout(400)
                except Exception:
                    pass

        await page.add_style_tag(content="header { display: sticky !important; }")

        print(
            f"\n🎉  Done! {len(uuids)} question(s) captured.\n"
            f"    Files saved to: {user_out_dir.resolve()}\n"
        )
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())