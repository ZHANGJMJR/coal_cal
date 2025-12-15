import os
import pandas as pd
import pymysql
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import traceback

# ==================================================
# 基础配置
# ==================================================

# SXCOAL_USER = "18210325736"
# SXCOAL_PASS = "88888888"


SXCOAL_USER = "IMSGE2021"
SXCOAL_PASS = "NGB2021"

TARGET_URL = "https://www.sxcoal.com/data/detail/FW1001I"

DOWNLOAD_DIR = "./downloads"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootroot",
    "database": "coal_db",
    "charset": "utf8mb4"
}

# ==================================================
# 工具函数
# ==================================================

def get_last_week_range(today: datetime.date):
    """
    获取“当前日期之前的上一个自然周”
    周一 ~ 周日
    """
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday


def save_excel_to_mysql(excel_path: str):
    """
    解析 Excel → 写入 cci_detail + cci_sum（含 Blob）
    """

    # ---------- 1. 读取 Excel ----------
    df = pd.read_excel(
        excel_path,
        skiprows=8,
        header=None
    )

    # 只取前两列 A、B
    df = df.iloc[:, 0:2]
    df.columns = ["trade_date", "price_rmb"]

    # ---------- 2. 过滤非日期行 ----------
    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce"
    ).dt.date

    df = df.dropna(subset=["trade_date"])

    # 删除倒数第 1、2 行
    if len(df) > 2:
        df = df.iloc[:-2]

    print(f"有效数据行数：{len(df)}")

    # ---------- 3. 导入 cci_detail ----------
    import_date = datetime.today().date()
    df["import_date"] = import_date

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_detail_sql = """
    INSERT INTO cci_detail (trade_date, price_rmb, import_date)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        price_rmb=VALUES(price_rmb),
        import_date=VALUES(import_date)
    """

    for _, row in df.iterrows():
        cursor.execute(insert_detail_sql, tuple(row))

    conn.commit()

    # ---------- 4. 计算上一个自然周均价 ----------
    start_date, end_date = get_last_week_range(import_date)

    cursor.execute("""
        SELECT AVG(price_rmb)
        FROM cci_detail
        WHERE trade_date BETWEEN %s AND %s
    """, (start_date, end_date))

    price_avg = cursor.fetchone()[0]
    price_avg = price_avg if price_avg is not None else 0

    # ---------- 5. Excel 文件转 Blob ----------
    with open(excel_path, "rb") as f:
        file_blob = f.read()

    cursor.execute("""
        INSERT INTO cci_sum (priceavg, datafile)
        VALUES (%s, %s)
    """, (price_avg, file_blob))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ 入库完成 | 上周均价 = {price_avg}")


# ==================================================
# 主流程
# ==================================================

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # ---------- 登录 ----------
        page.goto("https://www.sxcoal.com/en", wait_until="networkidle")
        page.get_by_text("Sign in").click()
        page.wait_for_selector("input[placeholder*='Enter user']")
        page.get_by_placeholder("Enter user name / e-mail start").fill(SXCOAL_USER)
        page.get_by_placeholder("Password").fill(SXCOAL_PASS)
        page.get_by_role("button", name="Login").click()
        page.wait_for_timeout(3000)

        # ---------- 打开指标页面 ----------
        page.goto(TARGET_URL, wait_until="networkidle")

        # ---------- 捕获真实下载 ----------
        with page.expect_download(timeout=15000) as d:
            page.locator("button[title='下载数据表']").click()

        download = d.value
        filename = f"CCI_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        download.save_as(filepath)
        print("📥 下载完成：", filepath)

        browser.close()

    # ---------- Excel → MySQL ----------
    save_excel_to_mysql(filepath)

    # ---------- 删除本地文件 ----------
    os.remove(filepath)
    print("🧹 本地文件已删除")


def safe_job():
    try:
        main()
    except Exception:
        print("❌ 定时任务执行异常：")
        traceback.print_exc()


if __name__ == "__main__":
    main()
#
# if __name__ == "__main__":
#     # cron表达式：每天 08:00 执行（等价于 0 8 * * *）
#     scheduler = BlockingScheduler(timezone="Asia/Shanghai")  # 你需要也可改成 Asia/Singapore
#     scheduler.add_job(
#         safe_job,
#         CronTrigger.from_crontab("0 8 * * *"),
#         id="sxcoal_cci_job",
#         replace_existing=True,
#         max_instances=1,   # 防止重叠执行
#         coalesce=True      # 若错过时间点，合并补跑一次
#     )
#
#     print("✅ 定时任务已启动：每天 08:00 自动执行（cron=0 8 * * *）")
#     scheduler.start()