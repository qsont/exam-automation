import asyncio
import sys

from browser.connection import connect_cdp
from capture.questions import find_question_cards
from capture.dom import get_card, get_question, get_mark_scheme, click_mark_scheme_btn, keypress_esc, clone_mark_scheme_element, remove_cloned_mark_scheme
from capture.screenshot import screenshot_question, screenshot_mark_scheme

from decouple import config
from pathlib import Path
from playwright.async_api import async_playwright, Page


# ── Configuration (loaded from .env) ─────────────────────────────────────────
ENDPOINT_URL  = config("ENDPOINT_URL")
PROFILE_PATH  = config("PROFILE_PATH")
TARGET_URL    = config("TARGET_URL", default="")
WEBSITE_URL    = config("WEBSITE_URL", default="")
OUTPUT_DIR    = config("OUTPUT_DIR", default="")
MODAL_SETTLE_MS = config("MODAL_SETTLE_MS", cast=int, default=1200)

# UUID regex — matches bare question wrapper IDs (36-char hex, no suffix)
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


# Per-question capture
async def capture_question_card(page: Page, uuid: str, index: int, output_dir: Path):
    """Screenshot one question card and its Mark Scheme modal."""

    q_num = f"{index:02d}"
    print(f"  [{q_num}] uuid={uuid[:8]}...", end="  ", flush=True)

    card = await get_card(page, uuid)
    question = await get_question(card)
    await screenshot_question(output_dir, q_num, question)

    await click_mark_scheme_btn(card)
    await clone_mark_scheme_element(page)
    mark_scheme = await get_mark_scheme(page)
    await screenshot_mark_scheme(output_dir, q_num, mark_scheme)
    await remove_cloned_mark_scheme(page)

    await keypress_esc(page)

# Main 
async def main():

    async with async_playwright() as p:
        
        browser = await connect_cdp(p, ENDPOINT_URL)
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

        uuids = await find_question_cards(page, browser)

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