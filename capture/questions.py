# Discover all question wrapper UUIDs from the DOM
from capture.dom import get_uuids

async def find_question_cards(page, browser):
  raw_uuids = await get_uuids(page)

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
  
  return uuids
