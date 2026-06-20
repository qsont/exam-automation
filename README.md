# Exam Automation

This is a small Python automation for capturing a specific website's questions' and their answers' screenshots from a Chromium browser session.

## Setup

1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install the project dependencies:

   ```bash
   pip install playwright pillow python-decouple
   playwright install chromium
   ```

4. Copy `.env.example` to `.env` and set these values:
   - `ENDPOINT_URL=http://127.0.0.1:9222`
   - `EXECUTABLE_PATH` for your Brave or Chrome binary if you want to keep it documented in `.env`
   - `PROFILE_PATH` to your Chrome or Brave user data folder
   - `TARGET_URL` to the filtered exam page, or leave it blank and navigate manually
   - `WEBSITE_URL` is the website's URL. The website shall remain anonymous due to work reasons.
   - `OUTPUT_DIR` if you want a custom output folder; otherwise the script prompts for a folder under `outputs/`
   - `MODAL_SETTLE_MS` if the page needs extra time to render

5. Start Brave with remote debugging enabled.
   - On Windows, you can use `launch.bat`.
   - The script expects an open specific website tab.

## Run

```bash
python first_test.py
```

Press ENTER when the target page is ready. Screenshots will be written into the output folder configured in `.env`.
If `OUTPUT_DIR` is blank, the script will ask you for a folder name and save into `outputs/<name>`.