from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scipy.optimize import linprog
import pymysql
import json
import datetime
import traceback
import logging
from werkzeug.exceptions import NotFound

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.ERROR)

# ---------- MySQL 配置 ----------
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,  # ← 必须是整型
    "user": "root",
    "password": "rootroot",
    "database": "coal_db"
}

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
            cursorclass=pymysql.cursors.DictCursor  # ← 返回 dict
        )
    except Exception as e:
        print(f"MySQL连接失败：{e}")
        return None


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

# ---------- 获取所有原煤 ----------
@app.route('/api/coals', methods=['GET'])
def get_coals():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_coals ORDER BY id ASC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "message": f"获取数据失败：{e}"}), 500


# ---------- 添加 / 修改原煤 ----------
@app.route('/api/coals', methods=['POST'])
def save_coal():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    if data.get("id"):  # UPDATE
        cursor.execute("""
            UPDATE raw_coals
            SET name=%s, calorific=%s, ash=%s, sulfur=%s, price=%s, short_transport=%s
            WHERE id=%s
        """, (data["name"], data["calorific"], data["ash"], data["sulfur"],
              data["price"], data["short_transport"], data["id"]))
    else:  # INSERT
        cursor.execute("""
            INSERT INTO raw_coals (name, calorific, ash, sulfur, price, short_transport)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data["name"], data["calorific"], data["ash"], data["sulfur"],
              data["price"], data["short_transport"]))

    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ---------- 删除原煤 ----------
@app.route('/api/coals/<int:coal_id>', methods=['DELETE'])
def delete_coal(coal_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw_coals WHERE id=%s", (coal_id,))
        conn.commit()
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
        cursor.execute("SELECT name, calorific, ash, sulfur, price, short_transport FROM raw_coals")
        coals = cursor.fetchall()
        cursor.close()
        conn.close()

        if not coals:
            return jsonify({"success": False, "message": "没有原煤数据"})

        n = len(coals)

        # 目标函数：成本（不含短倒费）
        costs = [c["price"] for c in coals]

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
        total_cost = sum(ratio[i] * coals[i]["price"] for i in range(n))

        result_json = {
            "success": True,
            "ratio": [
                {"name": coals[i]["name"], "ratio": round(ratio[i] * 100, 2)}
                for i in range(n)
            ],
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
# def electric_blend():
#     # 比枚举（暴力搜索）  慢
#     try:
#         target = request.json or {}
#         target_calorific = float(target.get("calorific", 0))
#
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT name, calorific, price, short_transport FROM raw_coals")
#         rows = cursor.fetchall()
#         cursor.close()
#         conn.close()
#
#         if not rows:
#             return jsonify({"success": False, "message": "没有原煤数据"})
#
#         coals = [
#             {
#                 "name": r["name"],
#                 "calorific": float(r["calorific"]),
#                 "price": float(r["price"]),
#                 "short_transport": float(r["short_transport"])
#             }
#             for r in rows
#         ]
#
#         from itertools import combinations, product
#
#         plans = []
#
#         # 只允许 1~3 种煤组合
#         for k in [1, 2, 3]:
#             for combo in combinations(coals, k):
#
#                 # 比例步进 5%
#                 steps = [i / 20 for i in range(21)]
#
#                 for ratios in product(steps, repeat=k):
#                     if abs(sum(ratios) - 1.0) > 0.01:
#                         continue
#
#                     mix_cal = sum(c["calorific"] * r for c, r in zip(combo, ratios))
#                     if mix_cal < target_calorific:
#                         continue
#
#                     mix_cost = sum(
#                         (c["price"] + c["short_transport"] + 1.8) * r
#                         for c, r in zip(combo, ratios)
#                     )
#
#                     plans.append({
#                         "mix_calorific": round(mix_cal, 2),
#                         "mix_cost": round(mix_cost, 2),
#                         "items": [
#                             {
#                                 "name": combo[i]["name"],
#                                 "ratio": round(ratios[i], 2),
#                                 "price": combo[i]["price"],
#                                 "short_transport": combo[i]["short_transport"]
#                             }
#                             for i in range(k)
#                         ]
#                     })
#
#         if not plans:
#             return jsonify({"success": False, "message": "没有满足热值的方案"})
#
#         plans.sort(key=lambda x: x["mix_cost"])
#
#         return jsonify({"success": True, "plans": plans[:3]})
#
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})


# ============================================================
#                      ★ 前端首页 ★
# ============================================================
def electric_blend():
    """
    电煤配比：满足热值 & 返回多种方案（最多 3 种）
    先 LP 找最重要煤，再用 5% 枚举产生多方案
    """
    try:
        target = request.json or {}
        target_calorific = float(target.get("calorific", 0))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, calorific, price, short_transport 
            FROM raw_coals
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify({"success": False, "message": "没有原煤数据"})

        # ---------------------------
        #  数据准备
        # ---------------------------
        n = len(rows)
        names = [r["name"] for r in rows]
        calorific = [float(r["calorific"]) for r in rows]
        price = [float(r["price"]) for r in rows]
        short = [float(r["short_transport"]) for r in rows]
        blending_fee = 1.8

        unit_cost = [price[i] + short[i] + blending_fee for i in range(n)]

        # ---------------------------
        #  第一次 LP：找到最优权重煤（用于缩小搜索范围）
        # ---------------------------
        A_ub = [
            [-c for c in calorific]
        ]
        b_ub = [-target_calorific]

        A_eq = [[1]*n]
        b_eq = [1]

        bounds = [(0, 1) for _ in range(n)]

        lp = linprog(unit_cost, A_ub=A_ub, b_ub=b_ub,
                     A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method="highs")

        if not lp.success:
            return jsonify({"success": False, "message": "没有可行方案"})

        x = lp.x
        # 按比例排序，取前 3 种
        top_idx = sorted(range(n), key=lambda i: x[i], reverse=True)[:3]

        # ---------------------------
        #  第二步：对最重要的煤 1~3 种执行 5% 枚举
        # ---------------------------
        coals2 = []
        for i in top_idx:
            coals2.append({
                "name": names[i],
                "calorific": calorific[i],
                "price": price[i],
                "short": short[i],
                "unit_cost": unit_cost[i]
            })

        k = len(coals2)

        from itertools import product

        steps = [i/20 for i in range(21)]  # 0%, 5%, ..., 100%

        plans = []

        for ratios in product(steps, repeat=k):
            if abs(sum(ratios) - 1.0) > 0.01:
                continue

            mix_cal = sum(coals2[i]["calorific"] * ratios[i] for i in range(k))
            if mix_cal < target_calorific:
                continue

            mix_cost = sum(coals2[i]["unit_cost"] * ratios[i] for i in range(k))

            items = []
            for i in range(k):
                items.append({
                    "name": coals2[i]["name"],
                    "ratio": round(ratios[i], 4),
                    "calorific": coals2[i]["calorific"],
                    "price": coals2[i]["price"],
                    "short_transport": coals2[i]["short"],
                    "blending_fee": blending_fee,
                    "unit_cost": coals2[i]["unit_cost"]
                })

            plans.append({
                "mix_calorific": round(mix_cal, 2),
                "mix_cost": round(mix_cost, 2),
                "items": items
            })

        if not plans:
            return jsonify({"success": False, "message": "没有满足热值的配比方案"})

        # 按成本排序
        plans.sort(key=lambda p: p["mix_cost"])

        # 只返回前 3 种
        return jsonify({
            "success": True,
            "plans": plans[:3]
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})
@app.route('/')
def index():
    return render_template('index.html')


# ============================================================
#                           ★ 启动 ★
# ============================================================

if __name__ == '__main__':
    print("🚀 配煤优化系统后端 (MySQL 8) 已启动：http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)