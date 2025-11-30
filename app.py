from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scipy.optimize import linprog
import mysql.connector
from mysql.connector import Error
import json
import datetime
import traceback

app = Flask(__name__)
CORS(app)

# ---------- MySQL 连接配置 ----------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "rootroot",
    "database": "coal_db"
}


# ---------- 数据库连接 ----------
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"MySQL连接失败：{e}")
        return None


# ---------- 获取所有原煤 ----------
@app.route('/api/coals', methods=['GET'])
def get_coals():
    try:
        conn = get_connection()
        if not conn:
            return jsonify({"success": False, "message": "数据库连接失败"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM raw_coals ORDER BY id ASC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "message": f"获取数据失败：{e}"}), 500


# ---------- 添加原煤 ----------
@app.route('/api/coals', methods=['POST'])
def save_coal():
    data = request.json

    conn = get_connection()
    c = conn.cursor()

    if data.get("id"):  # UPDATE
        c.execute("""
            UPDATE raw_coals
            SET name=%s, calorific=%s, ash=%s, sulfur=%s, price=%s, short_transport=%s
            WHERE id=%s
        """, (data["name"], data["calorific"], data["ash"], data["sulfur"],
              data["price"], data["short_transport"], data["id"]))
    else:  # INSERT
        c.execute("""
            INSERT INTO raw_coals (name, calorific, ash, sulfur, price, short_transport)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data["name"], data["calorific"], data["ash"], data["sulfur"],
              data["price"], data["short_transport"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

# ---------- 修改原煤 ----------
@app.route('/api/coals/<int:coal_id>', methods=['PUT'])
def update_coal(coal_id):
    try:
        data = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE raw_coals SET name=%s, calorific=%s, ash=%s, sulfur=%s, price=%s WHERE id=%s",
            (data['name'], data['calorific'], data['ash'], data['sulfur'], data['price'], coal_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "更新成功"})
    except Exception as e:
        return jsonify({"success": False, "message": f"更新失败：{e}"}), 500


# ---------- 删除原煤 ----------
@app.route('/api/coals/<int:coal_id>', methods=['DELETE'])
def delete_coal(coal_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw_coals WHERE id = %s", (coal_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败：{e}"}), 500


# ---------- 配煤优化计算 ----------
@app.route('/api/blend', methods=['POST'])
def calculate_blend():
    try:
        target = request.json or {}
        conn = get_connection()
        cursor = conn.cursor()
        # cursor.execute("SELECT name, calorific, ash, sulfur, price FROM raw_coals")
        cursor.execute("SELECT name, calorific, ash, sulfur, price, short_transport FROM raw_coals")
        raw_coals = cursor.fetchall()
        cursor.close()
        conn.close()

        if not raw_coals:
            return jsonify({"success": False, "message": "没有原煤数据，请先添加"})

        n = len(raw_coals)
        costs = [coal[4] for coal in raw_coals]
        A_eq = [[1] * n]
        b_eq = [1]
        A_ub, b_ub = [], []

        # 约束条件
        if "min_calorific" in target:
            A_ub.append([-coal[1] for coal in raw_coals])
            b_ub.append(-target["min_calorific"])
        if "max_ash" in target:
            A_ub.append([coal[2] for coal in raw_coals])
            b_ub.append(target["max_ash"])
        if "max_sulfur" in target:
            A_ub.append([coal[3] for coal in raw_coals])
            b_ub.append(target["max_sulfur"])

        bounds = [(0, 1) for _ in range(n)]
        result = linprog(costs, A_ub=A_ub, b_ub=b_ub,
                         A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

        if not result.success:
            return jsonify({"success": False, "message": "无可行方案，请调整目标指标"})

        ratio = result.x
        total_calorific = sum(ratio[i] * raw_coals[i][1] for i in range(n))
        total_ash = sum(ratio[i] * raw_coals[i][2] for i in range(n))
        total_sulfur = sum(ratio[i] * raw_coals[i][3] for i in range(n))
        total_cost = sum(ratio[i] * raw_coals[i][4] for i in range(n))

        result_data = {
            "success": True,
            "ratio": [{"name": raw_coals[i][0], "ratio": round(ratio[i] * 100, 2)} for i in range(n)],
            "指标": {
                "发热量": round(total_calorific, 2),
                "灰分": round(total_ash, 2),
                "硫分": round(total_sulfur, 2),
                "单位成本": round(total_cost, 2)
            }
        }

        save_history(result_data)
        return jsonify(result_data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": f"计算错误：{e}"}), 500


# ---------- 保存配煤结果 ----------
def save_history(result_json):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blend_history (timestamp, result_json) VALUES (%s, %s)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(result_json, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"保存历史失败：{e}")


# ---------- 查询历史 ----------
@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, result_json FROM blend_history ORDER BY id DESC LIMIT 30")
        rows = [{"id": r[0], "timestamp": r[1], "result": json.loads(r[2])} for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败：{e}"}), 500


# ---------- 删除历史 ----------
@app.route('/api/history/<int:hid>', methods=['DELETE'])
def delete_history(hid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blend_history WHERE id = %s", (hid,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "记录已删除"})
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败：{e}"}), 500


@app.route('/api/electric_blend', methods=['POST'])
def electric_blend():
    try:
        target = request.json or {}
        target_calorific = float(target.get("calorific", 0))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, calorific, price, short_transport FROM raw_coals")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify({"success": False, "message": "没有原煤数据"})

        coals = []
        for r in rows:
            coals.append({
                "name": r[0],
                "calorific": float(r[1]),
                "price": float(r[2]),
                "short_transport": float(r[3]),
            })

        from itertools import combinations, product

        plans = []  # ⭐ 保存所有可行方案

        # 只允许 1~3 种煤组合
        for k in [1, 2, 3]:
            for combo in combinations(coals, k):

                # 每种煤的比例按 10% 步进
                steps = [i / 10 for i in range(11)]

                for ratios in product(steps, repeat=k):
                    if abs(sum(ratios) - 1.0) > 0.01:
                        continue

                    mix_cal = sum(c["calorific"] * r for c, r in zip(combo, ratios))
                    if mix_cal < target_calorific:
                        continue

                    # 成本 = 单价 + 短倒费 + 1.8 配煤费
                    mix_cost = sum(
                        (c["price"] + c["short_transport"] + 1.8) * r
                        for c, r in zip(combo, ratios)
                    )

                    # ⭐ 保存方案
                    plans.append({
                        "mix_calorific": round(mix_cal, 2),
                        "mix_cost": round(mix_cost, 2),
                        "items": [
                            {
                                "name": combo[i]["name"],
                                "ratio": round(ratios[i], 2),
                                "price": combo[i]["price"],
                                "short_transport": combo[i]["short_transport"],
                            }
                            for i in range(k)
                        ]
                    })

        # 若没有任何方案
        if not plans:
            return jsonify({"success": False, "message": "没有找到满足热值的配比"})

        # ⭐ 按成本升序
        plans.sort(key=lambda x: x["mix_cost"])

        # ⭐ 返回前 10 种方案（可修改为任意数量）
        return jsonify({
            "success": True,
            "plans": plans[:10]
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# ---------- 前端首页 ----------
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print("🚀 配煤优化系统后端 (MySQL 8) 已启动：http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)