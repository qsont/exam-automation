async def screenshot_question(output_dir, num, element):
  path = output_dir / f"q{num}_question.png"
  await element.screenshot(path=str(path))
  
# This logic will be changed, hence separated from function above
async def screenshot_mark_scheme(output_dir, num, element):
  path = output_dir / f"q{num}_answer.png"
  await element.screenshot(path=str(path))