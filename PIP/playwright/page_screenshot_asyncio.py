# conda activate browseusep311 (установлено все: chromium, webkit, firefox; командой: playwright install)
# conda activate allpy310 (только chromium, установлен командой: playwright install chromium)


import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        for browser_type in [p.chromium, p.firefox, p.webkit]:
            browser = await browser_type.launch()
            page = await browser.new_page()
            await page.goto('http://playwright.dev')
            await page.screenshot(path=f'data/example-{browser_type.name}.png')
            await browser.close()

asyncio.run(main())