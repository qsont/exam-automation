import sys

async def connect_cdp(p, endpoint_url):
  print("\n✨  Just a simple Python automation made with slop")
  print("🔗  Connecting to \033[0;33m Chromium-based browser's\033[0m debug session...")
  try:
      browser = await p.chromium.connect_over_cdp(endpoint_url)
      return browser
  except Exception as e:
      print(
          f"\n❌  Could not connect to browser at {endpoint_url}\n"
          f"    Error: {e}\n"
          f"    Make sure your Chromium-based browser is running with --remote-debugging-port=9222\n"
      )
      sys.exit(1)