from playwright.async_api import Page, Locator

# DOM-related operations


async def get_uuids(page):
  return await page.evaluate("""
  [...document.querySelectorAll('[id]')]
  .map(el => el.id)
  .filter(id => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id))
  """)

async def get_card(page, uuid) -> Locator:
  # Locate wrapper and inner card by their stable IDs
  return page.locator(f'[id="{uuid}-question-content"]')

async def get_question(card):
  return card.locator('div.css-5nr4ri.css-1ma9zj9')

async def get_mark_scheme(page: Page) -> Locator:
  capture = page.locator('#__PW_CAPTURE_ROOT__')
  await capture.wait_for(state="visible")
  return capture

async def click_mark_scheme_btn(question):
  mark_scheme_btn = question.locator('[data-analytics-name="clickMarkScheme"]')
  await mark_scheme_btn.click()

async def keypress_esc(page: Page):
  await page.keyboard.press("Escape")
  await page.wait_for_timeout(400)

async def clone_mark_scheme_element(page: Page):
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
  
async def remove_cloned_mark_scheme(page: Page):
  await page.evaluate("""
  () => {
      const el = document.getElementById('__PW_CAPTURE_ROOT__');
      if (el) el.remove();
  }
  """)   