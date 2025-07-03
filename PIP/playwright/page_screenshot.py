# conda activate allpy310

from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("https://ya.ru/")
page.screenshot(path="data/example1.png")
browser.close()

playwright.stop()