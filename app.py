from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from scipy.optimize import linprog
import pymysql
import json
import datetime
import traceback
import logging
from werkzeug.exceptions import NotFound
from decimal import Decimal
from itertools import product

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.ERROR)

# ---------- MySQL 配置 ----------
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "rootroot",
    "database": "coal_db"
}

BLENDING_FEE = 1.8
VAT_RATE = 0.13


# ---------- 创建 MySQL 连接 ----------
def get_connection():
    try:
        return pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"MySQL连接失败：{e}")
        return None


# ---------- 类型转换工具函数 ----------
def convert_decimal_to_float(data):
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: float(value) if isinstance(value, Decimal) else value
                for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    return data


def json_safe(obj):
    if isinstance(obj, list):
        return [json_safe(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return obj


# ---------- 全局异常处理 ----------
@app.errorhandler(NotFound)
def handle_404(e):
    # 保持你原来“静默”风格（避免浏览器反复报错）
    return "", 204


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFound):
        return "", 204
    logging.error("🔥 捕获未处理异常：%s", e, exc_info=True)
    return jsonify({"success": False, "message": "服务器内部错误"}), 500


# ---------- favicon：真正返回文件，解决你之前 204 导致 ico 不显示 ----------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# ============================================================
#                 ★       日志：原煤变更      ★
# ============================================================
def log_coal_action(coal_id, action, old_data, new_data, changes, userid="", username=""):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO coal_logs (coal_id, userid, username, action,
                                   old_data, new_data, changes, modified_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            coal_id,
            userid,
            username,
            action,
            json.dumps(json_safe(old_data), ensure_ascii=False),
            json.dumps(json_safe(new_data), ensure_ascii=False),
            json.dumps(json_safe(changes), ensure_ascii=False)
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("日志写入失败：", e)


# ============================================================
#                 ★       API：原煤管理      ★
# ============================================================

@app.route('/api/coals', methods=['GET'])
def get_coals():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_coals ORDER BY id ASC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        data = convert_decimal_to_float(data)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "message": f"获取数据失败：{e}"}), 500


def _validate_coal_payload(data: dict):
    # 你前端已有校验；这里后端再兜底，防止脏数据写库
    def rng(v, mn, mx, name):
        if v is None:
            raise ValueError(f"{name}不能为空")
        fv = float(v)
        if fv < mn or fv > mx:
            raise ValueError(f"{name}必须在 {mn}~{mx} 之间")
        return fv

    data["calorific"] = rng(data.get("calorific"), 1000, 9000, "发热量")
    data["ash"] = rng(data.get("ash"), 1, 50, "灰分")
    data["sulfur"] = rng(data.get("sulfur"), 0.1, 3, "硫分")
    data["volatile"] = rng(data.get("volatile"), 0, 50, "挥发份")
    data["recovery"] = rng(data.get("recovery"), 0, 100, "回收率")
    data["g_value"] = rng(data.get("g_value"), 0, 90, "G值")

    data["x_value"] = float(data.get("x_value") or 0)
    data["y_value"] = float(data.get("y_value") or 0)

    data["price"] = rng(data.get("price"), 0, 1000, "价格")
    data["short_transport"] = rng(data.get("short_transport", 0), 0, 30, "短倒费")
    data["screening_fee"] = rng(data.get("screening_fee", 0), 0, 20, "过筛费")
    data["crushing_fee"] = rng(data.get("crushing_fee", 0), 0, 10, "破碎费")

    data["is_domestic"] = int(data.get("is_domestic", 1))
    if data["is_domestic"] not in (0, 1):
        data["is_domestic"] = 1

    if not str(data.get("name", "")).strip():
        raise ValueError("原煤名称不能为空")


@app.route('/api/coals', methods=['POST'])
def save_coal():
    data = request.json or {}
    try:
        _validate_coal_payload(data)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

    conn = get_connection()
    cursor = conn.cursor()

    if not data.get("id"):
        cursor.execute("""
            INSERT INTO raw_coals (name, calorific, ash, sulfur, volatile,
                                  recovery, g_value, x_value, y_value,
                                  price, short_transport, screening_fee, crushing_fee, is_domestic)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["name"], data["calorific"], data["ash"], data["sulfur"],
            data["volatile"], data["recovery"], data["g_value"],
            data["x_value"], data["y_value"], data["price"],
            data["short_transport"], data["screening_fee"],
            data["crushing_fee"], data["is_domestic"]
        ))
        coal_id = cursor.lastrowid
        log_coal_action(coal_id, "ADD", old_data=None, new_data=data, changes=None)
    else:
        coal_id = int(data["id"])
        cursor.execute("SELECT * FROM raw_coals WHERE id=%s", (coal_id,))
        old = cursor.fetchone()

        cursor.execute("""
            UPDATE raw_coals
            SET name=%s, calorific=%s, ash=%s, sulfur=%s, volatile=%s,
                recovery=%s, g_value=%s, x_value=%s, y_value=%s,
                price=%s, short_transport=%s, screening_fee=%s, crushing_fee=%s, is_domestic=%s
            WHERE id=%s
        """, (
            data["name"], data["calorific"], data["ash"], data["sulfur"],
            data["volatile"], data["recovery"], data["g_value"],
            data["x_value"], data["y_value"], data["price"],
            data["short_transport"], data["screening_fee"],
            data["crushing_fee"], data["is_domestic"], coal_id
        ))

        changes = {}
        if old:
            for key in data:
                if key in old:
                    old_v = str(old[key])
                    new_v = str(data[key])
                    if old_v != new_v:
                        changes[key] = {"old": old_v, "new": new_v}

        log_coal_action(coal_id, "UPDATE", old_data=old, new_data=data, changes=changes)

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/coals/<int:coal_id>', methods=['DELETE'])
def delete_coal(coal_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM raw_coals WHERE id=%s", (coal_id,))
        old = cursor.fetchone()

        cursor.execute("DELETE FROM raw_coals WHERE id=%s", (coal_id,))
        conn.commit()

        log_coal_action(coal_id, "DELETE", old_data=old, new_data=None, changes=None)

        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败：{e}"}), 500


# ============================================================
#                 ★       工具：CCI Tooltip 计算      ★
# ============================================================
def _format_datetime_cn(dt: datetime.datetime):
    return dt.strftime("%Y年%m月%d日 %H:%M:%S")



def _build_cci_tooltip(
    insert_time: datetime.datetime | None,
    cci_base_price: float | None = None
):
    """
    CCI Tooltip（只描述 CCI 数据本身，不做热值折算）
    - cci_base_price: 5500 基准价
    """

    if not insert_time:
        return {
            "cci_base_price": cci_base_price,
            "tip_text": "暂无 CCI 数据",
            "bg_style": "background-color:#f3f4f6;",
            "arrow_color": "#f3f4f6",
            "age_days": None
        }

    now = datetime.datetime.now()
    diff_days = (now - insert_time).total_seconds() / (60 * 60 * 24)

    if diff_days <= 1:
        bg = "background-color:#dcfce7;"
        arrow = "#dcfce7"
    else:
        bg = "background-color:#fce7f3;"
        arrow = "#fce7f3"

    # Tooltip 文本：把 5500 基准价明确展示
    if cci_base_price is not None:
        tip_text = (
            f"<div>CCI（5500）：{round(cci_base_price)} 元/吨</div>" 
            f"<div>数据获取时间：{_format_datetime_cn(insert_time)}</div>"
        )
    else:
        tip_text = f"数据获取时间：{_format_datetime_cn(insert_time)}"

    return {
        "cci_base_price": round(cci_base_price, 2) if cci_base_price is not None else None,
        "tip_text": tip_text,
        "bg_style": bg,
        "arrow_color": arrow,
        "age_days": round(diff_days, 4)
    }
def calc_cci_by_calorific(base_price: float, target_calorific: float) -> float:
    """
    CCI 基于 5500 kcal，按目标热值折算
    公式：CCI * (target / 5500)
    """
    if not base_price or not target_calorific:
        return base_price
    return base_price * target_calorific / 5500



# ============================================================
#                 ★       API：配煤优化（linprog）      ★
# ============================================================

def save_history(result):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blend_history (result, create_time)
            VALUES (%s, %s)
        """, (json.dumps(result, ensure_ascii=False), datetime.datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass


@app.route('/api/blend', methods=['POST'])
def calculate_blend():
    try:
        target = request.json or {}

        min_cal = float(target.get("min_calorific", 0) or 0)
        max_ash = float(target.get("max_ash", 999) or 999)
        max_sulfur = float(target.get("max_sulfur", 999) or 999)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, calorific, ash, sulfur, price, short_transport,
                screening_fee, crushing_fee
            FROM raw_coals
        """)
        coals = cursor.fetchall()
        cursor.close()
        conn.close()

        if not coals:
            return jsonify({"success": False, "message": "没有原煤数据"})

        coals = convert_decimal_to_float(coals)
        n = len(coals)

        costs = [
            c["price"] + c.get("short_transport", 0) + c.get("screening_fee", 0) + c.get("crushing_fee", 0)
            for c in coals
        ]

        A_eq = [[1] * n]
        b_eq = [1]
        A_ub = []
        b_ub = []

        if min_cal > 0:
            A_ub.append([-c["calorific"] for c in coals])
            b_ub.append(-min_cal)

        if max_ash < 999:
            A_ub.append([c["ash"] for c in coals])
            b_ub.append(max_ash)

        if max_sulfur < 999:
            A_ub.append([c["sulfur"] for c in coals])
            b_ub.append(max_sulfur)

        bounds = [(0, 1) for _ in range(n)]

        result = linprog(costs, A_ub=A_ub, b_ub=b_ub,
                         A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds, method="highs")

        if not result.success:
            return jsonify({"success": False, "message": "无可行方案"})

        ratio = result.x

        total_cal = sum(ratio[i] * coals[i]["calorific"] for i in range(n))
        total_ash = sum(ratio[i] * coals[i]["ash"] for i in range(n))
        total_sulfur = sum(ratio[i] * coals[i]["sulfur"] for i in range(n))
        total_cost = sum(ratio[i] * costs[i] for i in range(n))

        ratio_data = []
        for i in range(n):
            if ratio[i] > 0.001:
                ratio_data.append({
                    "name": coals[i]["name"],
                    "ratio": round(ratio[i] * 100, 2)
                })

        result_json = {
            "success": True,
            "ratio": ratio_data,
            "指标": {
                "发热量": round(total_cal, 2),
                "灰分": round(total_ash, 2),
                "硫分": round(total_sulfur, 2),
                "单位成本": round(total_cost, 2),
                "单位成本含税": round(total_cost * (1 + VAT_RATE), 2)
            }
        }

        save_history(result_json)
        return jsonify(result_json)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================
#               ★       详情表：后端生成 HTML     ★
# ============================================================
def build_detail_table_html(plan):
    blending_fee = BLENDING_FEE
    all_coals = plan.get("all_coals", []) or []

    # 参与比例映射（按 id）
    item_map = {int(it["id"]): it for it in (plan.get("items", []) or [])}

    enriched = []
    for c in all_coals:
        cid = int(c["id"])
        ratio = float(item_map.get(cid, {}).get("ratio", 0.0))

        price = float(c.get("price", 0))
        short_transport = float(c.get("short_transport", 0))
        screening_fee = float(c.get("screening_fee", 0))
        crushing_fee = float(c.get("crushing_fee", 0))

        unit_cost = price + short_transport + screening_fee + crushing_fee + blending_fee
        cost_contribution = unit_cost * ratio

        enriched.append({
            "id": cid,
            "name": c.get("name", ""),
            "calorific": float(c.get("calorific", 0)),
            "price": price,
            "short_transport": short_transport,
            "screening_fee": screening_fee,
            "crushing_fee": crushing_fee,
            "ratio": ratio,
            "unit_cost": unit_cost,
            "cost_contribution": cost_contribution,
            "is_domestic": int(c.get("is_domestic", 1))
        })

    # 你原 JS 最新排序：参与(>0)在前；参与内部比例小->大；0 在后
    enriched.sort(key=lambda x: (0 if x["ratio"] > 0 else 1, x["ratio"] if x["ratio"] > 0 else 9e9, x["name"]))

    total_cal = round(sum(c["calorific"] * c["ratio"] for c in enriched), 0)
    total_cost = sum(c["cost_contribution"] for c in enriched)

    # 公式字符串（完全照你原逻辑拼）
    used_parts = []
    for c in enriched:
        if c["ratio"] > 0.0001:
            parts = []
            if c["price"] != 0: parts.append(f"{c['price']:.2f}")
            if c["short_transport"] != 0: parts.append(f"{c['short_transport']:.2f}")
            if c["screening_fee"] != 0: parts.append(f"{c['screening_fee']:.2f}")
            if c["crushing_fee"] != 0: parts.append(f"{c['crushing_fee']:.2f}")
            parts.append(f"{blending_fee:.2f}")
            pct = f"{c['ratio'] * 100:.1f}%"
            used_parts.append(f"({ ' + '.join(parts) }) * {pct}")

    formula = " + ".join(used_parts) if used_parts else ""

    def icon_html(is_domestic: int):
        if is_domestic == 1:
            return '<img src="/static/icons/china.svg" title="境内煤" style="width:20px;height:20px;">'
        return '<img src="/static/icons/global.svg" title="坑口煤" style="width:20px;height:20px;">'

    rows_html = []
    for c in enriched:
        pct = f"{c['ratio']*100:.1f}%" if c["ratio"] > 0.0001 else "—"
        contribution = f"{c['cost_contribution']:.2f}" if c["ratio"] > 0.0001 else "0.00"
        row_class = "" if c["ratio"] > 0.0001 else "text-gray-400"

        rows_html.append(f"""
            <tr class="{row_class}">
                <td class="border px-3 py-2">{c['name']}</td>
                <td class="border px-3 py-2 text-right">{pct}</td>
                <td class="border px-3 py-2 text-right">{int(round(c['calorific']))}</td>
                <td class="border px-3 py-2 text-right">{c['price']:.2f}</td>
                <td class="border px-3 py-2 text-right">{c['short_transport']:.2f}</td>
                <td class="border px-3 py-2 text-right">{c['screening_fee']:.2f}</td>
                <td class="border px-3 py-2 text-right">{c['crushing_fee']:.2f}</td>
                <td class="border px-3 py-2 text-right">{blending_fee:.2f}</td>
                <td class="border px-3 py-2 text-right">{c['unit_cost']:.2f}</td>
                <td class="border px-3 py-2 text-right">{contribution}</td>
                <td class="border px-3 py-2 text-center">
                    <div class="flex justify-center items-center">
                        {icon_html(c['is_domestic'])}
                    </div>
                </td>
            </tr>
        """)

    return f"""
        <h3 class="font-semibold mb-2">配比详情</h3>
        <table class="min-w-full text-sm bg-white rounded shadow">
            <thead>
                <tr class="bg-gray-100">
                    <th class="border px-3 py-2 text-left">煤种</th>
                    <th class="border px-3 py-2 text-right">比例</th>
                    <th class="border px-3 py-2 text-right">热值</th>
                    <th class="border px-3 py-2 text-right">单价</th>
                    <th class="border px-3 py-2 text-right">短倒费</th>
                    <th class="border px-3 py-2 text-right">过筛费</th>
                    <th class="border px-3 py-2 text-right">破碎费</th>
                    <th class="border px-3 py-2 text-right">附加(1.8)</th>
                    <th class="border px-3 py-2 text-right">单位成本</th>
                    <th class="border px-3 py-2 text-right">配比成本</th>
                    <th class="border px-3 py-2 text-center">策克</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
            <tfoot class="bg-gray-100 font-bold">
                <tr>
                    <td class="border px-3 py-2">合计</td>
                    <td class="border px-3 py-2"></td>
                    <td class="border px-3 py-2 text-right">{int(total_cal)}</td>
                    <td class="border px-3 py-2 text-center text-xs md:text-sm" colspan="6">
                        {formula}
                        = <span class="text-blue-600 font-bold text-lg">{int(round(total_cost))}</span>
                        （含税：
                            <span class="text-red-600 font-bold text-lg">{int(round(total_cost * (1 + VAT_RATE)))}</span>
                        ）
                    </td>
                    <td class="border px-3 py-2 text-right text-blue-600 font-bold text-lg">
                        {int(round(total_cost))}
                    </td>
                    <td class="border px-3 py-2"></td>
                </tr>
            </tfoot>
        </table>
    """


# ============================================================
#               ★       API：电煤配比（后端完成全部计算）     ★
# ============================================================

def _normalize_step_size(step):
    try:
        s = float(step)
    except:
        return 10.0
    if s not in [0.5, 1, 5, 10]:
        return 10.0
    return s


def get_latest_cci_with_adjust(target_calorific: float):
    """
    统一的 CCI 获取 + 折算逻辑
    所有 API 都必须用它，避免逻辑漂移
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT priceavg, curdate
        FROM cci_sum
        ORDER BY curdate DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {
            "success": False,
            "cci_price": None,
            "cci_price_text": "—",
            "tooltip": _build_cci_tooltip(None)
        }

    base_price = float(row["priceavg"])   # 5500 基准
    cur = row["curdate"]

    if isinstance(cur, datetime.date) and not isinstance(cur, datetime.datetime):
        insert_time = datetime.datetime(cur.year, cur.month, cur.day, 0, 0, 0)
    else:
        insert_time = cur

    # ⭐ 唯一折算公式（全系统只此一处）
    adjusted_price = calc_cci_by_calorific(base_price, target_calorific)

    return {
        "success": True,

        "cci_base_price": round(base_price, 2),
        "cci_base_text": f"{round(base_price)}元/吨（5500）",

        "cci_price": round(adjusted_price, 2),
        "cci_price_text": f"{round(adjusted_price)}元/吨",

        "target_calorific": target_calorific,
        "insert_time": insert_time.isoformat(),
        "tooltip": _build_cci_tooltip(insert_time)
    }


def calc_cci_by_calorific(base_price: float, plan_calorific: float) -> float:
    """
    CCI 基于 5500 kcal，按【方案热值】折算
    公式：base_price * (plan_calorific / 5500)
    """
    if base_price is None:
        return None
    try:
        plan_calorific = float(plan_calorific)
    except:
        plan_calorific = 5500.0
    if plan_calorific <= 0:
        plan_calorific = 5500.0
    return float(base_price) * plan_calorific / 5500.0


def get_latest_cci_base():
    """
    只取 CCI 5500 基准价 + 时间 + tooltip，不做折算
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT priceavg, curdate
        FROM cci_sum
        ORDER BY curdate DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {
            "success": False,
            "cci_base_price": None,
            "cci_base_text": "—",
            "insert_time": None,
            "tooltip": _build_cci_tooltip(None)
        }

    base_price = float(row["priceavg"])
    cur = row["curdate"]
    if isinstance(cur, datetime.date) and not isinstance(cur, datetime.datetime):
        insert_time = datetime.datetime(cur.year, cur.month, cur.day, 0, 0, 0)
    else:
        insert_time = cur

    return {
        "success": True,
        "cci_base_price": round(base_price, 2),
        "cci_base_text": f"{round(base_price)}元/吨（5500）",
        "insert_time": insert_time.isoformat(),
        "tooltip": _build_cci_tooltip(insert_time,base_price)
    }

@app.route('/api/cci/latest', methods=['GET'])
def get_latest_cci():
    try:
        calorific = float(request.args.get("calorific", 5500))  # 注意：参数名改成 calorific 更直观
        base = get_latest_cci_base()
        if not base.get("success"):
            return jsonify({
                "success": False,
                "message": "暂无 CCI 数据",
                "cci_price": None,
                "cci_price_text": "—",
                "tooltip": base.get("tooltip")
            })

        base_price = float(base["cci_base_price"])
        adjusted = calc_cci_by_calorific(base_price, calorific)

        return jsonify({
            "success": True,
            "cci_base_price": base["cci_base_price"],
            "cci_base_text": base["cci_base_text"],

            "calorific": calorific,
            "cci_price": round(adjusted, 2),
            "cci_price_text": f"{round(adjusted)}元/吨",

            "insert_time": base["insert_time"],
            "tooltip": base["tooltip"]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/electric_blend', methods=['POST'])
def electric_blend():
    """
    后端输出：
    - plans: 已按成本排序、去重、截断 5 个
    - 每个 plan：
      - items: 已按 ratio 从小到大排序，并带 ratio_pct、weight
      - mix_cost_tax
      - detail_html：直接给前端 innerHTML（前端不再计算/拼详情表）
    """
    try:
        target = request.json or {}
        target_calorific = float(target.get("calorific", 0) or 0)
        selected_coal_ids = target.get("selected_coal_ids", [])

        fee_ceke =round(float(target.get("fee_ceke_miaoliang", 0) or 0)/1.09,2)
        fee_miaoliang = round(float(target.get("fee_miaoliang_caofeidian", 0) or 0)/1.09,2)
        fee_misc = round(float(target.get("fee_misc", 0) or 0)/1.06,2)

        reverse_extra_fee = fee_ceke + fee_miaoliang + fee_misc


        step_sizes = target.get("step_sizes", [10])
        if not isinstance(step_sizes, list) or len(step_sizes) == 0:
            step_sizes = [10]
        step_size = _normalize_step_size(step_sizes[0])

        if target_calorific <= 0:
            return jsonify({"success": False, "message": "目标发热量无效"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        if selected_coal_ids:
            placeholders = ', '.join(['%s'] * len(selected_coal_ids))
            cursor.execute(f"""
                SELECT id, name, calorific, price, short_transport,
                       screening_fee, crushing_fee, is_domestic
                FROM raw_coals
                WHERE id IN ({placeholders})
            """, tuple(selected_coal_ids))
        else:
            cursor.execute("""
                SELECT id, name, calorific, price, short_transport,
                       screening_fee, crushing_fee, is_domestic
                FROM raw_coals
            """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify({"success": False, "message": "没有原煤数据"})

        rows = convert_decimal_to_float(rows)

        n = len(rows)
        ids = [int(r["id"]) for r in rows]
        names = [r["name"] for r in rows]
        cal = [float(r["calorific"]) for r in rows]
        price = [float(r["price"]) for r in rows]
        short = [float(r.get("short_transport", 0)) for r in rows]
        screening = [float(r.get("screening_fee", 0)) for r in rows]
        crushing = [float(r.get("crushing_fee", 0)) for r in rows]
        is_domestic_list = [int(r.get("is_domestic", 1)) for r in rows]

        unit_cost = [
            price[i] + short[i] + screening[i] + crushing[i] + BLENDING_FEE
            for i in range(n)
        ]

        # --------- 选 top-3（保持你目前评分逻辑） ---------
        coal_scores = []
        for i in range(n):
            score = (cal[i] / target_calorific) / (unit_cost[i] if unit_cost[i] != 0 else 1e-9)
            coal_scores.append((i, score))

        sorted_idx = [i for i, _ in sorted(coal_scores, key=lambda x: x[1], reverse=True)]
        top_idx = sorted_idx[:3]

        coals2 = [{
            "id": ids[i],
            "name": names[i],
            "calorific": cal[i],
            "price": price[i],
            "short_transport": short[i],
            "screening_fee": screening[i],
            "crushing_fee": crushing[i],
            "unit_cost": unit_cost[i],
            "is_domestic": is_domestic_list[i]
        } for i in top_idx]

        k = len(coals2)
        step_ratio = step_size / 100.0
        steps = [i * step_ratio for i in range(int(1 / step_ratio) + 1)]

        plans = []

        # 1) 单煤
        for c in coals2:
            if c["calorific"] >= target_calorific:
                plans.append({
                    "type": "单煤种",
                    "coal_count": 1,
                    "mix_calorific": round(c["calorific"], 2),
                    "mix_cost": round(c["unit_cost"], 2),
                    "items": [{
                        **c,
                        "ratio": 1.0
                    }]
                })

        # 2) 双煤
        if k >= 2:
            for i in range(k):
                for j in range(i + 1, k):
                    c1, c2 = coals2[i], coals2[j]
                    for r1 in steps:
                        r2 = 1 - r1
                        if r2 < 0:
                            continue

                        mix_cal = c1["calorific"] * r1 + c2["calorific"] * r2
                        if mix_cal < target_calorific:
                            continue

                        mix_cost = c1["unit_cost"] * r1 + c2["unit_cost"] * r2

                        items = []
                        if r1 > 0.001:
                            items.append({**c1, "ratio": round(r1, 4)})
                        if r2 > 0.001:
                            items.append({**c2, "ratio": round(r2, 4)})

                        plans.append({
                            "type": "双煤种",
                            "coal_count": 2,
                            "mix_calorific": round(mix_cal, 2),
                            "mix_cost": round(mix_cost, 2),
                            "items": items
                        })

        # 3) 三煤
        if k >= 3:
            for ratios in product(steps, repeat=3):
                if abs(sum(ratios) - 1.0) > 0.001:
                    continue
                if sum(1 for r in ratios if r > 0.001) != 3:
                    continue

                mix_cal = sum(coals2[i]["calorific"] * ratios[i] for i in range(3))
                if mix_cal < target_calorific:
                    continue

                mix_cost = sum(coals2[i]["unit_cost"] * ratios[i] for i in range(3))

                items = []
                for i in range(3):
                    items.append({**coals2[i], "ratio": round(ratios[i], 4)})

                plans.append({
                    "type": "三煤种",
                    "coal_count": 3,
                    "mix_calorific": round(mix_cal, 2),
                    "mix_cost": round(mix_cost, 2),
                    "items": items
                })

        if not plans:
            return jsonify({"success": False, "message": "没有满足热值的配比方案"})

        # --------- 补齐 all_coals（所有煤都带，ratio 默认 0）---------
        full_all_coals = [{
            "id": int(r["id"]),
            "name": r["name"],
            "calorific": float(r["calorific"]),
            "price": float(r["price"]),
            "short_transport": float(r.get("short_transport", 0)),
            "screening_fee": float(r.get("screening_fee", 0)),
            "crushing_fee": float(r.get("crushing_fee", 0)),
            "ratio": 0.0,
            "is_domestic": int(r.get("is_domestic", 1))
        } for r in rows]

        for p in plans:
            p["all_coals"] = [c.copy() for c in full_all_coals]
            ratio_map = {int(it["id"]): float(it["ratio"]) for it in p["items"]}
            for c in p["all_coals"]:
                c["ratio"] = float(ratio_map.get(int(c["id"]), 0.0))

        # --------- 去重：按 mix_cost（保留你原逻辑）---------
        seen = set()
        unique_plans = []
        for p in sorted(plans, key=lambda x: x["mix_cost"]):
            key = round(float(p["mix_cost"]), 2)
            if key not in seen:
                seen.add(key)
                unique_plans.append(p)

        unique_plans = unique_plans[:5]

        # --------- CCI 信息：后端直接拿（前端不算 tooltip）---------
        cci_base = get_latest_cci_base()
        # --------- 最终输出：把所有“展示所需的计算字段”一次性补齐 ---------
        final_plans = []
        for p in unique_plans:
            items = p.get("items", []) or []
            # 桶卡显示：按比例从小到大（你 JS 原逻辑）
            items_sorted = sorted(items, key=lambda it: float(it.get("ratio", 0)))

            ratios_pos = [float(it.get("ratio", 0)) for it in items_sorted if float(it.get("ratio", 0)) > 0]
            min_ratio = min(ratios_pos) if ratios_pos else 0.0001

            for it in items_sorted:
                r = float(it.get("ratio", 0))
                it["ratio_pct"] = round(r * 100, 1)
                it["weight"] = int(round((r / min_ratio) if min_ratio > 0 else 1))
                # 保证字段完整（前端不会出现 undefined）
                it["calorific"] = float(it.get("calorific", 0))
                it["unit_cost"] = float(it.get("unit_cost", 0))
                it["short_transport"] = float(it.get("short_transport", 0))
                it["screening_fee"] = float(it.get("screening_fee", 0))
                it["crushing_fee"] = float(it.get("crushing_fee", 0))
                it["price"] = float(it.get("price", 0))
                it["is_domestic"] = int(it.get("is_domestic", 1))

            mix_cost = float(p.get("mix_cost", 0))
            mix_cal = float(p.get("mix_calorific", 0) or 0)


            if cci_base.get("success") and cci_base.get("cci_base_price") is not None:
                base_price = float(cci_base["cci_base_price"])
                adjusted = calc_cci_by_calorific(base_price, mix_cal)

                # ===== 倒推策克价格：CCI - 额外费用 =====
                if cci_base.get("success") and adjusted is not None:
                    reverse_ceke_price = round(adjusted - reverse_extra_fee - 21.77, 2)
                else:
                    reverse_ceke_price = None

                cci_for_plan = {
                    "success": True,
                    "cci_base_price": cci_base["cci_base_price"],
                    "cci_base_text": cci_base["cci_base_text"],

                    "calorific": mix_cal,  # ⭐ 方案热值
                    "cci_price": round(adjusted, 2),
                    "cci_price_text": f"{round(adjusted)}元/吨",

                    "insert_time": cci_base["insert_time"],
                    "tooltip": cci_base["tooltip"]
                }
            else:
                cci_for_plan = {
                    "success": False,
                    "cci_price_text": "—",
                    "tooltip": cci_base.get("tooltip") or _build_cci_tooltip(None)
                }
            p_out = {
                "type": p.get("type"),
                "coal_count": int(p.get("coal_count", 0)),
                "mix_calorific": float(p.get("mix_calorific", 0)),
                "mix_cost": mix_cost,
                "mix_cost_tax": round(mix_cost * (1 + VAT_RATE), 2),
                "items": items_sorted,
                "all_coals": p.get("all_coals", []),
                # 你页面里目前“倒推策克价格/预测销售毛利”是写死的样式，这里先保持默认值（后续你要算也放这里）
                # "reverse_ceke_price": 600,
                "reverse_ceke_price": int(reverse_ceke_price),
                "gross_profit": int(reverse_ceke_price - mix_cost),
                # CCI 展示信息：每个卡片直接可用
                "cci": cci_for_plan
            }

            # 详情表 HTML：后端生成
            p_out["detail_html"] = build_detail_table_html(p_out)

            final_plans.append(p_out)

        return jsonify({"success": True, "plans": final_plans})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})


# ============================================================
#                           ★ 页面 ★
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')


# ============================================================
#                           ★ 启动 ★
# ============================================================
if __name__ == '__main__':
    print("🚀 配煤优化系统后端 (MySQL 8) 已启动：http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
