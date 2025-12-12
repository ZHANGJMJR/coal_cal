from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 1. 打开首页
    page.goto("https://www.sxcoal.com/en", wait_until="networkidle")

    # 2. 点击右上角 Sign in
    page.get_by_text("Sign in").click()

    # 3. 等待登录弹窗的输入框
    page.wait_for_selector("input[placeholder*='Enter user name']")

    # 4. 输入账号密码（使用 placeholder 精准定位）
    page.get_by_placeholder("Enter user name / e-mail start").fill("18210325736")
    page.get_by_placeholder("Password").fill("88888888")

    # 5. 点击 Login 按钮
    page.get_by_role("button", name="Login").click()

    # 等待登录成功
    page.wait_for_timeout(3000)

    # 6. 跳转到目标页面
    page.goto("https://www.sxcoal.com/data/detail/FW1001I", wait_until="networkidle")

    # 7. 点击下载按钮（只是点击，不处理文件）
    download_btn = page.locator("text=下载")
    if download_btn.count() > 0:
        print("找到‘下载’按钮 → 点击中")
        download_btn.first.click()
    else:
        print("❌ 没找到‘下载’按钮，请截图下载按钮的 HTML 给我")

    page.wait_for_timeout(500000)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)