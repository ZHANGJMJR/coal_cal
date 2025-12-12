from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scipy.optimize import linprog
import pymysql
import json
import datetime
import traceback
import logging
from werkzeug.exceptions import NotFound
from decimal import Decimal  # 导入 Decimal 类型
from decimal import Decimal

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


# DB_CONFIG = {
#     "host": "127.0.0.1",
#     "port": 3309,
#     "user": "coal",
#     "password": "coal!@#$",
#     "database": "coal_db"
# }
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
    """递归将字典中的 Decimal 类型转换为 float"""
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: float(value) if isinstance(value, Decimal) else value
                for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    return data


# ---------- 全局异常处理 ----------
@app.errorhandler(NotFound)
def handle_404(e):
    return "", 204


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFound):
        return "", 204
    logging.error("🔥 捕获未处理异常：%s", e, exc_info=True)
    return jsonify({"success": False, "message": "服务器内部错误"}), 500


@app.route('/favicon.ico')
def favicon():
    return "", 204


# ============================================================
#                 ★       API：原煤管理      ★
# ============================================================

def json_safe(obj):
    """
    递归转换 JSON 不可序列化的类型：
    - Decimal → float
    - datetime → ISO 字符串
    - date → ISO 字符串
    """
    if isinstance(obj, list):
        return [json_safe(i) for i in obj]

    elif isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    elif isinstance(obj, Decimal):
        return float(obj)

    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    return obj


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


# ---------- 获取所有原煤 ----------
@app.route('/api/coals', methods=['GET'])
def get_coals():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # 查询包含新增的5个字段
        cursor.execute("SELECT * FROM raw_coals ORDER BY id ASC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        # 转换 Decimal 类型
        data = convert_decimal_to_float(data)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "message": f"获取数据失败：{e}"}), 500


# ---------- 添加 / 修改原煤 ----------
@app.route('/api/coals', methods=['POST'])
def save_coal():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    # 新增
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

        # ★ 日志：新增保存 new_data 完整记录
        log_coal_action(coal_id, "ADD", old_data=None, new_data=data, changes=None)

    else:
        # ------- UPDATE --------
        coal_id = data["id"]

        # 读取旧数据
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

        # ------- 日志：记录完整 old/new + 变化字段 -------
        changes = {}

        for key in data:
            if key in old:
                old_v = str(old[key])
                new_v = str(data[key])
                if old_v != new_v:
                    changes[key] = {"old": old_v, "new": new_v}

        log_coal_action(
            coal_id,
            "UPDATE",
            old_data=old,
            new_data=data,
            changes=changes
        )

    conn.commit()
    conn.close()
    return jsonify({"success": True})
@app.route('/api/coals/<int:coal_id>', methods=['DELETE'])
def delete_coal(coal_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 读取旧数据（删除后就没了）
        cursor.execute("SELECT * FROM raw_coals WHERE id=%s", (coal_id,))
        old = cursor.fetchone()

        # 删除
        cursor.execute("DELETE FROM raw_coals WHERE id=%s", (coal_id,))
        conn.commit()

        # 日志（old_data 保存被删内容）
        log_coal_action(
            coal_id,
            "DELETE",
            old_data=old,
            new_data=None,
            changes=None
        )

        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败：{e}"}), 500


# ============================================================
#                 ★       API：配煤优化      ★
# ============================================================

@app.route('/api/blend', methods=['POST'])
def calculate_blend():
    try:
        target = request.json or {}

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

        # 转换 Decimal 类型
        coals = convert_decimal_to_float(coals)
        n = len(coals)

        # 目标函数：成本（含短倒费+过筛费+破碎费）
        costs = [c["price"] + c["short_transport"] + c["screening_fee"] + c["crushing_fee"] for c in coals]

        A_eq = [[1] * n]
        b_eq = [1]
        A_ub = []
        b_ub = []

        if "min_calorific" in target:
            A_ub.append([-c["calorific"] for c in coals])
            b_ub.append(-target["min_calorific"])

        if "max_ash" in target:
            A_ub.append([c["ash"] for c in coals])
            b_ub.append(target["max_ash"])

        if "max_sulfur" in target:
            A_ub.append([c["sulfur"] for c in coals])
            b_ub.append(target["max_sulfur"])

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
        total_cost = sum(ratio[i] * (coals[i]["price"] + coals[i]["short_transport"] +
                                     coals[i]["screening_fee"] + coals[i]["crushing_fee"])
                         for i in range(n))

        # 过滤掉比例为0的煤种
        ratio_data = []
        for i in range(n):
            if ratio[i] > 0.001:  # 忽略小于0.1%的比例
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
                "单位成本": round(total_cost, 2)
            }
        }

        save_history(result_json)
        return jsonify(result_json)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================
#               ★       API：电煤配比（枚举）     ★
# ============================================================

@app.route('/api/electric_blend', methods=['POST'])
def electric_blend():
    """
    电煤配比：支持 1 / 2 / 3 种煤组合
    步长枚举：1%、5%、10%
    返回给前端的数据保证字段完整，不出现 undefined / NaN
    —— 关键修复：全程用 id 关联，而不是 name
    """
    try:
        target = request.json or {}
        target_calorific = float(target.get("calorific", 0))
        selected_coal_ids = target.get("selected_coal_ids", [])

        # ---------------------------
        # 步长
        # ---------------------------
        step_sizes = target.get("step_sizes", [10])
        if not isinstance(step_sizes, list) or len(step_sizes) == 0:
            step_sizes = [10]

        step_size = float(step_sizes[0])
        if step_size not in [0.5, 1, 5, 10]:
            step_size = 10
        # if step_size == 1:
        #     step_size =0.5

        # ---------------------------
        # 从数据库读取原煤数据
        # ---------------------------
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

        # ---------------------------
        # 数据准备
        # ---------------------------
        n = len(rows)
        ids = [r["id"] for r in rows]
        names = [r["name"] for r in rows]
        calorific = [float(r["calorific"]) for r in rows]
        price = [float(r["price"]) for r in rows]
        short = [float(r["short_transport"]) for r in rows]
        screening = [float(r["screening_fee"]) for r in rows]
        crushing = [float(r["crushing_fee"]) for r in rows]
        blending_fee = 1.8

        unit_cost = [
            price[i] + short[i] + screening[i] + crushing[i] + blending_fee
            for i in range(n)
        ]

        # ---------------------------
        # 第一次 LP：用于排序，而不是筛选
        # ---------------------------
        A_ub = [[-c for c in calorific]]
        b_ub = [-target_calorific]
        A_eq = [[1] * n]
        b_eq = [1]
        bounds = [(0, 1) for _ in range(n)]

        lp = linprog(unit_cost, A_ub=A_ub, b_ub=b_ub,
                     A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method="highs")

        if not lp.success:
            return jsonify({"success": False, "message": "没有可行方案"})

        x = lp.x

        # ---------------------------
        # 按 LP 结果排序，选出参与枚举的 3 种煤
        # ---------------------------
        # sorted_idx = sorted(range(n), key=lambda i: x[i], reverse=True)
        # top_idx = sorted_idx[:3]
        # ---------------------------
        # 正确的 top-3 选择逻辑：按评分(热值/目标热值)/成本 排序
        # ---------------------------
        coal_scores = []
        for i in range(n):
            score = (calorific[i] / target_calorific) / unit_cost[i]
            coal_scores.append((i, score))

        sorted_idx = [i for i, s in sorted(coal_scores, key=lambda x: x[1], reverse=True)]
        top_idx = sorted_idx[:3]

        # 参与枚举的煤（带 id）
        coals2 = [{
            "id": ids[i],
            "name": names[i],
            "calorific": calorific[i],
            "price": price[i],
            "short": short[i],
            "screening": screening[i],
            "crushing": crushing[i],
            "unit_cost": unit_cost[i],
            "is_domestic": rows[i]["is_domestic"]
        } for i in top_idx]

        k = len(coals2)
        step_ratio = step_size / 100.0
        steps = [i * step_ratio for i in range(int(1 / step_ratio) + 1)]

        from itertools import product
        plans = []

        # ---------------------------
        # 1. 单煤种方案
        # ---------------------------
        for c in coals2:
            if c["calorific"] >= target_calorific:
                plans.append({
                    "type": "单煤种",
                    "coal_count": 1,
                    "mix_calorific": round(c["calorific"], 2),
                    "mix_cost": round(c["unit_cost"], 2),
                    "items": [{
                        "id": c["id"],
                        "name": c["name"],
                        "ratio": 1.0,
                        "calorific": c["calorific"],
                        "price": c["price"],
                        "short_transport": c["short"],
                        "screening_fee": c["screening"],
                        "crushing_fee": c["crushing"],
                        "blending_fee": blending_fee,
                        "unit_cost": c["unit_cost"],
                        "is_domestic": c["is_domestic"]
                    }]
                })

        # ---------------------------
        # 2. 双煤种组合
        # ---------------------------
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
                            items.append({
                                "id": c1["id"],
                                "name": c1["name"],
                                "ratio": round(r1, 4),
                                "calorific": c1["calorific"],
                                "price": c1["price"],
                                "short_transport": c1["short"],
                                "screening_fee": c1["screening"],
                                "crushing_fee": c1["crushing"],
                                "blending_fee": blending_fee,
                                "unit_cost": c1["unit_cost"],
                                "is_domestic": c1["is_domestic"]
                            })
                        if r2 > 0.001:
                            items.append({
                                "id": c2["id"],
                                "name": c2["name"],
                                "ratio": round(r2, 4),
                                "calorific": c2["calorific"],
                                "price": c2["price"],
                                "short_transport": c2["short"],
                                "screening_fee": c2["screening"],
                                "crushing_fee": c2["crushing"],
                                "blending_fee": blending_fee,
                                "unit_cost": c2["unit_cost"],
                                "is_domestic": c2["is_domestic"]
                            })

                        plans.append({
                            "type": "双煤种",
                            "coal_count": 2,
                            "mix_calorific": round(mix_cal, 2),
                            "mix_cost": round(mix_cost, 2),
                            "items": items
                        })

        # ---------------------------
        # 3. 三煤种组合
        # ---------------------------
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
                    c = coals2[i]
                    items.append({
                        "id": c["id"],
                        "name": c["name"],
                        "ratio": round(ratios[i], 4),
                        "calorific": c["calorific"],
                        "price": c["price"],
                        "short_transport": c["short"],
                        "screening_fee": c["screening"],
                        "crushing_fee": c["crushing"],
                        "blending_fee": blending_fee,
                        "unit_cost": c["unit_cost"],
                        "is_domestic": c["is_domestic"]
                    })

                # all_coals：所有煤，ratio 先给 0，后面再根据 id 写回
                all_coals_list = []
                for r in rows:
                    all_coals_list.append({
                        "id": r["id"],
                        "name": r["name"],
                        "calorific": float(r["calorific"]),
                        "price": float(r["price"]),
                        "short_transport": float(r["short_transport"]),
                        "screening_fee": float(r["screening_fee"]),
                        "crushing_fee": float(r["crushing_fee"]),
                        "ratio": 0.0,
                        "is_domestic": r["is_domestic"]
                    })

                ratio_map = {item["id"]: item["ratio"] for item in items}
                for c in all_coals_list:
                    if c["id"] in ratio_map:
                        c["ratio"] = ratio_map[c["id"]]

                plans.append({
                    "type": "三煤种",
                    "coal_count": 3,
                    "items": items,
                    "all_coals": all_coals_list,
                    "mix_calorific": round(mix_cal, 2),
                    "mix_cost": round(mix_cost, 2)
                })

        # ---------------------------
        # 所有方案补齐 all_coals（按 id 写回比例）
        # ---------------------------
        full_all_coals = [
            {
                "id": r["id"],
                "name": r["name"],
                "calorific": float(r["calorific"]),
                "price": float(r["price"]),
                "short_transport": float(r["short_transport"]),
                "screening_fee": float(r["screening_fee"]),
                "crushing_fee": float(r["crushing_fee"]),
                "ratio": 0.0,
                "is_domestic": r["is_domestic"]
            }
            for r in rows
        ]

        for p in plans:
            if "all_coals" not in p:
                # 复制一份基准列表
                p["all_coals"] = [c.copy() for c in full_all_coals]

            ratio_map = {item["id"]: item["ratio"] for item in p["items"]}
            for c in p["all_coals"]:
                c["ratio"] = float(ratio_map.get(c["id"], 0.0))

        # ---------------------------
        # 去重 + 取前 5 种成本最低方案
        # ---------------------------
        if not plans:
            return jsonify({"success": False, "message": "没有满足热值的配比方案"})

        seen = set()
        unique_plans = []
        for p in sorted(plans, key=lambda p: p["mix_cost"]):
            key = round(p["mix_cost"], 2)
            if key not in seen:
                seen.add(key)
                unique_plans.append(p)

        return jsonify({"success": True, "plans": unique_plans[:5]})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})



# ============================================================
#               ★ API：获取最新 CCI 数据 ★
# ============================================================

@app.route('/api/cci/latest', methods=['GET'])
def get_latest_cci():
    try:
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
            return jsonify({"success": False, "message": "暂无 CCI 数据"})

        return jsonify({
            "success": True,
            "cci_price": float(row["priceavg"]),
            "insert_time": row["curdate"].isoformat()
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

# ---------- 保存历史记录（需确保表结构存在） ----------
def save_history(result):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blend_history (result, create_time)
            VALUES (%s, %s)
        """, (json.dumps(result), datetime.datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass


@app.route('/')
def index():
    return render_template('index.html')


# ============================================================
#                           ★ 启动 ★
# ============================================================

if __name__ == '__main__':
    print("🚀 配煤优化系统后端 (MySQL 8) 已启动：http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)