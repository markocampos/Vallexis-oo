import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(record_video_dir="/home/jules/verification/")
        page = await context.new_page()

        # Load page
        await page.goto("http://127.0.0.1:8000")

        # Verify stylesheet is loaded
        color = await page.evaluate("window.getComputedStyle(document.querySelector('.brand-header h1')).color")
        print(f"H1 color: {color}")

        # Verify min-height on button
        btn_height = await page.evaluate("window.getComputedStyle(document.querySelector('.btn')).minHeight")
        print(f"Button min-height: {btn_height}")

        await page.screenshot(path="/home/jules/verification/screenshot.png")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
