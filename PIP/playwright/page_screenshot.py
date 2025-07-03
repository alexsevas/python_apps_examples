# conda activate browseusep311 (установлено все: chromium, webkit, firefox; командой: playwright install)
# conda activate allpy310 (только chromium, установлен командой: playwright install chromium)

# Пример использования playwright с chromium
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("http://playwright.dev")
page.screenshot(path="data/example1.png")
browser.close()

playwright.stop()