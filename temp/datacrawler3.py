from playwright.sync_api import sync_playwright
import os
from datetime import datetime

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # ---------- 登录 ----------
    page.goto("https://www.sxcoal.com/en", wait_until="networkidle")
    page.get_by_text("Sign in").click()
    page.wait_for_selector("input[placeholder*='Enter user']")
    page.get_by_placeholder("Enter user name / e-mail start").fill("18210325736")
    page.get_by_placeholder("Password").fill("88888888")
    page.get_by_role("button", name="Login").click()
    page.wait_for_timeout(3000)

    # ---------- 打开数据页面 ----------
    page.goto("https://www.sxcoal.com/data/detail/FW1001I", wait_until="networkidle")

    # ---------- 捕获真实下载 ----------
    with page.expect_download() as download_info:
        page.locator("button[title='下载数据表']").click()

    download = download_info.value

    # 原始文件名（UUID）
    original_name = download.suggested_filename
    print("原始文件名：", original_name)

    # 自定义文件名
    today = datetime.now().strftime("%Y%m%d")
    save_name = f"CCI5500_{today}.xlsx"
    save_path = os.path.join(os.getcwd(), save_name)

    download.save_as(save_path)
    print("已保存为：", save_path)

    browser.close()


with sync_playwright() as p:
    run(p)