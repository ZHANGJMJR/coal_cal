// =============================
// 输入框自动选择内容
// =============================
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type="number"], input[type="text"]').forEach(input => {
        input.addEventListener('focus', () => setTimeout(() => input.select(), 10));
        input.addEventListener('click', () => {
            if (document.activeElement === input)
                setTimeout(() => input.select(), 10);
        });
    });
});

// =============================
// 标签页切换
// =============================
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('border-blue-500', 'text-blue-600');
            b.classList.add('border-transparent', 'text-gray-500');
        });
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.add('hidden'));

        btn.classList.remove('border-transparent', 'text-gray-500');
        btn.classList.add('border-blue-500', 'text-blue-600');

        const panelId = btn.id.replace('tab-', 'panel-');
        document.getElementById(panelId).classList.remove('hidden');
    });
});

// =============================
// 全局变量
// =============================
let selectedCoalIds = [];
let selectedRow = null;
let editingId = null;
let ratioChart = null;

// =============================
// 加载原煤数据（列表 + 选择弹窗）
// =============================
function loadCoals() {
    fetch('/api/coals')
        .then(response => response.json())
        .then(coals => {
            // ---- 原煤列表 ----
            const tableBody = document.getElementById('coal-table-body');
            if (tableBody) {
                tableBody.innerHTML = '';

                coals.forEach(coal => {
                    const row = document.createElement('tr');
                    row.setAttribute("data-id", coal.id);
                    row.classList.add("cursor-pointer", "hover:bg-blue-50");

                    const volatile = coal.volatile ? coal.volatile.toFixed(2) : '0.00';
                    const recovery = coal.recovery ? coal.recovery.toFixed(2) : '0.00';
                    const gValue = coal.g_value ? coal.g_value.toFixed(2) : '0.00';
                    const xValue = coal.x_value ? coal.x_value.toFixed(2) : '0.00';
                    const yValue = coal.y_value ? coal.y_value.toFixed(2) : '0.00';

                    row.innerHTML = `
                        <td class="py-2 px-4 border">${coal.name}</td>
                        <td class="py-2 px-4 border">${coal.calorific}</td>
                        <td class="py-2 px-4 border">${coal.ash.toFixed(2)}%</td>
                        <td class="py-2 px-4 border">${coal.sulfur.toFixed(2)}%</td>
                        <td class="py-2 px-4 border">${volatile}%</td>
                        <td class="py-2 px-4 border">${recovery}%</td>
                        <td class="py-2 px-4 border">${gValue}</td>
                        <td class="py-2 px-4 border">${xValue}</td>
                        <td class="py-2 px-4 border">${yValue}</td>
                        <td class="py-2 px-4 border">${coal.price}</td>
                        <td class="py-2 px-4 border">${(coal.short_transport ?? 0).toFixed(2)}</td>
                        <td class="py-2 px-4 border">${(coal.screening_fee ?? 0).toFixed(2)}</td>
                        <td class="py-2 px-4 border">${(coal.crushing_fee ?? 0).toFixed(2)}</td>
                    `;

                    row.onclick = () => {
                        if (selectedRow) selectedRow.classList.remove("bg-blue-100");
                        row.classList.add("bg-blue-100");
                        selectedRow = row;
                        editCoal(coal);
                    };

                    tableBody.appendChild(row);
                });
            }

            // ---- 选择弹窗中的表格 ----
            loadCoalSelectionTable(coals);
        });
}

// 原煤选择表格
function loadCoalSelectionTable(coals) {
    const tableBody = document.getElementById('coal-select-table');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    coals.forEach(coal => {
        const row = document.createElement('tr');
        const isSelected = selectedCoalIds.length === 0 || selectedCoalIds.includes(coal.id);

        row.innerHTML = `
            <td class="py-2 px-3 border-b text-center">
                <input type="checkbox" class="coal-checkbox" data-id="${coal.id}" ${isSelected ? 'checked' : ''}>
            </td>
            <td class="py-2 px-3 border">${coal.name}</td>
            <td class="py-2 px-3 border">${coal.calorific}</td>
            <td class="py-2 px-3 border">${coal.price}</td>
        `;

        tableBody.appendChild(row);
    });
}

// =============================
// 原煤选择弹窗事件
// =============================
(function bindCoalSelectModal() {
    const btn = document.getElementById('coal-select-btn');
    const modal = document.getElementById('coal-select-modal');
    if (!btn || !modal) return;

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        modal.classList.toggle('hidden');
    });

    // 点击外部关闭
    document.addEventListener('click', (e) => {
        if (!modal.contains(e.target) && !btn.contains(e.target)) {
            modal.classList.add('hidden');
        }
    });

    // 全选
    const btnAll = document.getElementById('select-all-coals');
    if (btnAll) {
        btnAll.addEventListener('click', () => {
            document.querySelectorAll('.coal-checkbox').forEach(cb => cb.checked = true);
        });
    }

    // 清空
    const btnClear = document.getElementById('clear-all-coals');
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            document.querySelectorAll('.coal-checkbox').forEach(cb => cb.checked = false);
        });
    }

    // 确认
    const btnConfirm = document.getElementById('confirm-coal-selection');
    if (btnConfirm) {
        btnConfirm.addEventListener('click', () => {
            const checkboxes = document.querySelectorAll('.coal-checkbox:checked');
            selectedCoalIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));

            const textElement = document.getElementById('selected-coals-text');
            if (selectedCoalIds.length === 0) {
                textElement.textContent = '未选择原煤';
            } else if (document.querySelectorAll('.coal-checkbox').length === selectedCoalIds.length) {
                textElement.textContent = '全部原煤';
            } else {
                textElement.textContent = `${selectedCoalIds.length}种原煤`;
            }

            modal.classList.add('hidden');
        });
    }
})();

// =============================
// 原煤编辑 + 重置
// =============================
function editCoal(coal) {
    editingId = coal.id;

    const set = (id, value, digits) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (value === undefined || value === null || isNaN(value)) {
            el.value = '';
        } else {
            el.value = (digits !== undefined) ? value.toFixed(digits) : value;
        }
    };

    set('coal-name', coal.name);
    set('coal-calorific', coal.calorific, 1);
    set('coal-ash', coal.ash, 2);
    set('coal-sulfur', coal.sulfur, 2);
    set('coal-volatile', coal.volatile, 2);
    set('coal-recovery', coal.recovery, 2);
    set('coal-g_value', coal.g_value, 2);
    set('coal-x_value', coal.x_value, 2);
    set('coal-y_value', coal.y_value, 2);
    set('coal-price', coal.price, 1);
    set('coal-short-transport', coal.short_transport, 2);
    set('coal-screening-fee', coal.screening_fee, 2);
    set('coal-crushing-fee', coal.crushing_fee, 2);

    const submitBtn = document.getElementById("coal-submit-btn");
    submitBtn.innerHTML = `<i class="fa fa-save mr-1"></i>保存修改`;
    submitBtn.classList.remove("bg-blue-600");
    submitBtn.classList.add("bg-green-600");

    const delBtn = document.getElementById("coal-delete-btn");
    const cancelBtn = document.getElementById("coal-cancel-btn");
    delBtn.classList.remove("hidden");
    cancelBtn.classList.remove("hidden");

    document.getElementById('coal-form').scrollIntoView({behavior: 'smooth'});
}

function resetCoalFormState() {
    editingId = null;
    const form = document.getElementById('coal-form');
    if (form) form.reset();

    document.getElementById('coal-short-transport').value = 0;
    document.getElementById('coal-screening-fee').value = 0;
    document.getElementById('coal-crushing-fee').value = 0;

    const submitBtn = document.getElementById("coal-submit-btn");
    submitBtn.innerHTML = `<i class="fa fa-plus mr-1"></i>添加`;
    submitBtn.classList.add("bg-blue-600");
    submitBtn.classList.remove("bg-green-600");

    document.getElementById("coal-delete-btn").classList.add("hidden");
    document.getElementById("coal-cancel-btn").classList.add("hidden");

    if (selectedRow) {
        selectedRow.classList.remove("bg-blue-100");
        selectedRow = null;
    }

    if (document.activeElement) document.activeElement.blur();
}

const coalCancelBtn = document.getElementById('coal-cancel-btn');
if (coalCancelBtn) {
    coalCancelBtn.addEventListener('click', resetCoalFormState);
}

// =============================
// 原煤表单提交（新增 / 修改）
// =============================
const coalForm = document.getElementById('coal-form');
if (coalForm) {
    coalForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const coal = {
            id: editingId,
            name: document.getElementById('coal-name').value,
            calorific: parseFloat(document.getElementById('coal-calorific').value),
            ash: parseFloat(document.getElementById('coal-ash').value),
            sulfur: parseFloat(document.getElementById('coal-sulfur').value),
            volatile: parseFloat(document.getElementById('coal-volatile').value),
            recovery: parseFloat(document.getElementById('coal-recovery').value),
            g_value: parseFloat(document.getElementById('coal-g_value').value),
            x_value: parseFloat(document.getElementById('coal-x_value').value),
            y_value: parseFloat(document.getElementById('coal-y_value').value),
            price: parseFloat(document.getElementById('coal-price').value),
            short_transport: parseFloat(document.getElementById('coal-short-transport').value || 0),
            screening_fee: parseFloat(document.getElementById('coal-screening-fee').value || 0),
            crushing_fee: parseFloat(document.getElementById('coal-crushing-fee').value || 0)
        };

        fetch('/api/coals', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(coal)
        })
            .then(res => res.json())
            .then(() => {
                alert(editingId ? '修改成功！' : '添加成功！');
                resetCoalFormState();
                loadCoals();
            });
    });
}

// =============================
// 删除原煤
// =============================
const coalDeleteBtn = document.getElementById('coal-delete-btn');
if (coalDeleteBtn) {
    coalDeleteBtn.addEventListener('click', () => {
        if (!editingId) {
            alert('请先在原煤列表中点击选择一条要删除的原煤。');
            return;
        }

        if (!confirm('确定要删除该原煤吗？删除后不可恢复！')) return;

        fetch(`/api/coals/${editingId}`, {method: 'DELETE'})
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    alert(data.message || '删除失败');
                    return;
                }
                alert('删除成功！');
                resetCoalFormState();
                loadCoals();
            });
    });
}

// =============================
// 配煤计算（/api/blend）
// =============================
const blendForm = document.getElementById('blend-form');
if (blendForm) {
    blendForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const target = {
            min_calorific: parseFloat(document.getElementById('target-calorific').value),
            max_ash: parseFloat(document.getElementById('target-ash').value),
            max_sulfur: parseFloat(document.getElementById('target-sulfur').value)
        };

        fetch('/api/blend', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(target)
        })
            .then(response => response.json())
            .then(result => {
                if (!result.success) {
                    alert(result.message);
                    return;
                }

                // 切换到结果 Tab
                const tabResult = document.getElementById('tab-result');
                if (tabResult) tabResult.click();

                const indicators = document.getElementById('result-indicators');
                const unitCost = parseFloat(result.指标.单位成本).toFixed(2);
                const taxCost = (result.指标.单位成本 * 1.13).toFixed(2);

                indicators.innerHTML = `
                    <div>
                        <p class="text-gray-600">发热量</p>
                        <p class="text-2xl font-bold">${result.指标.发热量} 大卡</p>
                    </div>
                    <div>
                        <p class="text-gray-600">灰分</p>
                        <p class="text-2xl font-bold">${result.指标.灰分} %</p>
                    </div>
                    <div>
                        <p class="text-gray-600">硫分</p>
                        <p class="text-2xl font-bold">${result.指标.硫分} %</p>
                    </div>
                    <div>
                        <p class="text-gray-600">单位成本（不含税）</p>
                        <p class="text-2xl font-bold">${unitCost} 元/吨</p>
                    </div>
                    <div>
                        <p class="text-gray-600">单位成本（含13%增值税价）</p>
                        <p class="text-2xl font-bold text-red-600">${taxCost} 元/吨</p>
                    </div>
                `;

                const ratioTable = document.getElementById('ratio-table');
                ratioTable.innerHTML = `
                    <table class="min-w-full">
                        <thead>
                            <tr class="bg-gray-100">
                                <th class="py-2 px-4 border-b">原煤名称</th>
                                <th class="py-2 px-4 border-b">配煤比例</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${result.ratio.map(item => `
                                <tr>
                                    <td class="py-2 px-4 border-b">${item.name}</td>
                                    <td class="py-2 px-4 border-b">${Math.round(item.ratio)}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;

                const ctx = document.getElementById('ratio-chart').getContext('2d');
                if (ratioChart) ratioChart.destroy();
                ratioChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: result.ratio.map(item => item.name),
                        datasets: [{
                            data: result.ratio.map(item => item.ratio),
                            backgroundColor: [
                                '#3e95cd', '#8e5ea2', '#3cba9f',
                                '#e8c3b9', '#c45850', '#ffcc00'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {legend: {position: 'right'}}
                    }
                });
            });
    });
}

// =============================
// 电煤步长（保持单选逻辑）
// =============================
document.querySelectorAll('.step-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function () {
        if (this.checked) {
            document.querySelectorAll('.step-checkbox').forEach(cb => {
                if (cb !== this) cb.checked = false;
            });
        }
    });
});

// =============================
// 桶水位更新：ratio 0~1
// =============================
function updateWaterLevel(tankEl, ratio) {
    const fill = tankEl.querySelector(".coal-oil-fill");
    const waterTop = tankEl.querySelector(".coal-oil-water-top");

    const h = tankEl.clientHeight;

    // ★ 修正：桶可视区高度 = 75%
    const visualZone = h * 0.75;

    // ★ 补偿：最低留 10% 空间避免太贴底部
    const offset = h * 0.10;

    // ★ 新水位算法
    const waterHeight = visualZone * ratio + offset;

    fill.style.height = waterHeight + "px";

    waterTop.style.bottom = (waterHeight - 8) + "px";
}

// =============================
// 电煤配比表单提交（/api/electric_blend）
// =============================
const electricForm = document.getElementById('electric-form');
if (electricForm) {
    electricForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const selectedSteps = Array.from(document.querySelectorAll('.step-checkbox:checked'))
            .map(cb => parseInt(cb.value));
        const stepSizes = selectedSteps.length > 0 ? selectedSteps : [10];

        const target = {
            calorific: parseFloat(document.getElementById('electric-calorific').value),
            selected_coal_ids: selectedCoalIds,
            step_sizes: stepSizes
        };

        const resultPanel = document.getElementById("electric-result");
        const listDiv = document.getElementById("electric-plan-list");
        listDiv.innerHTML = '<div class="text-center py-4">计算中...</div>';
        resultPanel.classList.remove("hidden");

        try {
            const response = await fetch('/api/electric_blend', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(target)
            });

            const result = await response.json();

            if (!result.success) {
                listDiv.innerHTML = `<div class="text-center py-4 text-red-500">${result.message || '电煤配比计算失败'}</div>`;
                return;
            }

            renderElectricPlans(result.plans);
        } catch (error) {
            listDiv.innerHTML = `<div class="text-center py-4 text-red-500">计算失败：${error.message}</div>`;
        }
    });
}

// =============================
// 电煤方案渲染（桶形 UI 核心）
// =============================
function renderElectricPlans(plans) {
    const list = document.getElementById("electric-plan-list");
    list.innerHTML = "";

    if (!plans || plans.length === 0) {
        list.innerHTML = `<div class="text-center py-4 text-gray-500">暂无满足条件的方案</div>`;
        return;
    }

    plans.forEach((plan, index) => {
        const cost = Math.round(plan.mix_cost);
        const taxCost = Math.round(plan.mix_cost * 1.13);
        const calorific = Math.round(plan.mix_calorific);
        const isBest = index === 0;

        const card = document.createElement("div");
        card.className =
            "bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition mb-6";

        // 中间桶列表
        const coalBlocks = plan.items.map(item => {
            const pct = Math.round(item.ratio * 100);
            return `
                <div class="coal-oil-tank-wrapper">
                    <div class="coal-oil-tank">
                        <div class="coal-oil-fill"></div>
                        <div class="coal-oil-water-top"></div>
                        <div class="coal-oil-content">
                            <div class="coal-oil-name">${item.name}</div>
                            <div class="coal-oil-pct">${pct}%</div>
                            <div class="coal-oil-calorific">${Math.round(item.calorific)} 大卡</div>
                        </div>
                    </div>
<!--                    <div class="coal-oil-calorific">${Math.round(item.calorific)} 大卡</div>-->
                </div>
            `;
        }).join("");

        card.innerHTML = `
            <div class="plan-grid">

                <!-- 左列：方案标题 -->
                <div class="flex items-center">
                    <span class="text-xl font-bold">电煤方案 ${index + 1}</span>
                    ${
            isBest
                ? `<span class="ml-2 px-2 py-1 bg-red-100 text-red-600 text-sm rounded">最低成本</span>`
                : ""
        }
                </div>

                <!-- 中列：桶形煤卡 -->
                <div class="flex flex-wrap gap-4 items-center" style="margin-left:4px;">
                    ${coalBlocks}
                </div>

                <!-- 右列：成本 + 按钮 -->
                <div class="flex items-center justify-end space-x-6">

                    <div class="text-gray-800 text-base font-bold leading-8 text-right" style="transform: translateX(-30px);">
                        <div class="flex justify-end whitespace-nowrap">
                            <span>成本（不含税）</span>
                            <span style="display:inline-block; width:16px; text-align:center;">：</span>
                            <span class="text-blue-600 " style="font-size: 18px;">${cost} 元/吨</span>
                        </div>
                        <div class="flex justify-end whitespace-nowrap">
                            <span>成本（含13%增值税）</span>
                            <span style="display:inline-block; width:16px; text-align:center;">：</span>
                            <span class="text-red-600 " style="font-size: 18px;">${taxCost} 元/吨</span>
                        </div>
                        <div class="flex justify-end whitespace-nowrap">
                            <span>热值</span>
                            <span style="display:inline-block; width:16px; text-align:center;">：</span>
                            <span style="font-size: 18px;">${calorific} kcal</span>
                        </div>
                    </div>

                    <button class="plan-confirm-btn">
                        <i class="fa fa-check"></i>
                        <span class="text-base">确定使用该方案</span>
                    </button>

                </div>
            </div>
        `;

        // 详情部分
        const detail = document.createElement("div");
        detail.className = "hidden bg-gray-50 border border-gray-200 rounded-lg p-4 mt-4";

        /**
         * 把 plan.items 里的真实配比，合并回 all_coals
         * - 有配比的煤：ratio > 0
         * - 没用到的煤：ratio = 0
         */
        const allCoalsEnriched = (plan.all_coals || []).map(c => {
            const used = (plan.items || []).find(it => it.name === c.name);
            const ratio = used ? used.ratio : 0;   // ★ 只用各自煤种的 ratio

            const blendingFee = c.blending_fee ?? 1.8;
            const unitCost =
                c.price +
                c.short_transport +
                c.screening_fee +
                c.crushing_fee +
                blendingFee;

            return {
                ...c,
                ratio,
                blending_fee: blendingFee,
                unit_cost: unitCost
            };
        });

        // 用新的 all_coals 调用详情表
        detail.innerHTML = buildDetailTable({
            ...plan,
            all_coals: allCoalsEnriched
        });

        const toggle = document.createElement("button");
        toggle.className = "detail-toggle-btn";

        // 初始（未展开）
        toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 展开详情';

        // 点击事件
        toggle.onclick = () => {
            const isHidden = detail.classList.contains("hidden");

            // 切换显示
            detail.classList.toggle("hidden");

            if (isHidden) {
                // 展开状态
                toggle.classList.add("expanded");
                toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 收起详情';
            } else {
                // 收起状态
                toggle.classList.remove("expanded");
                toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 展开详情';
            }
        };


        card.appendChild(toggle);
        card.appendChild(detail);

        list.appendChild(card);

        // ★ 在 card 已经插入 DOM 之后，设置桶水位
        const tanks = card.querySelectorAll(".coal-oil-tank");
        plan.items.forEach((item, i) => {
            updateWaterLevel(tanks[i], item.ratio);
        });
    });
}

// =============================
// 配比详情表格
// =============================
// -------------------------------
// 方案详情表格（包含：所有煤种 + 合计公式）
// -------------------------------
function buildDetailTable(plan) {
    const blendingFee = 1.8;

    // 后端传来的所有煤种（含没参与配比的）
    const allCoals = plan.all_coals || [];

    // 把本方案里真正参与配比的 items 做一个 map（按 name）
    const itemMap = new Map(plan.items.map(it => [it.name, it]));

    // 把所有煤种都列出来，如果没参与配比，比例=0
    const enriched = allCoals.map(c => {
        const item = itemMap.get(c.name);
        const ratio = item ? item.ratio : 0; // 没配比的就是 0
        const unitCost =
            c.price +
            c.short_transport +
            c.screening_fee +
            c.crushing_fee +
            blendingFee;
        const costContribution = unitCost * ratio;

        return {
            name: c.name,
            calorific: c.calorific,
            price: c.price,
            short_transport: c.short_transport,
            screening_fee: c.screening_fee,
            crushing_fee: c.crushing_fee,
            ratio,
            unit_cost: unitCost,
            cost_contribution: costContribution,
        };
    });

    // ---- 各类合计 ----
    const totalCal = enriched
        .reduce((s, c) => s + c.calorific * c.ratio, 0)
        .toFixed(0);

    const totalCost = enriched.reduce(
        (s, c) => s + c.cost_contribution,
        0
    );

    const pricePart = enriched.reduce(
        (s, c) => s + c.price * c.ratio,
        0
    );
    const shortPart = enriched.reduce(
        (s, c) => s + c.short_transport * c.ratio,
        0
    );
    const screenPart = enriched.reduce(
        (s, c) => s + c.screening_fee * c.ratio,
        0
    );
    const crushPart = enriched.reduce(
        (s, c) => s + c.crushing_fee * c.ratio,
        0
    );
    const blendPart = enriched.some(c => c.ratio > 0) ? blendingFee : 0;

    const weightedUnitCost =
        pricePart + shortPart + screenPart + crushPart + blendPart;

    // ---- 合计行里的两条公式文本 ----
    // ① 单位成本拆分（单价 + 各项费用 = 单位成本）
    const unitFormula =
        `单位成本拆分：` +
        `${pricePart.toFixed(2)} + ` +
        `${shortPart.toFixed(2)} + ` +
        `${screenPart.toFixed(2)} + ` +
        `${crushPart.toFixed(2)} + ` +
        `${blendPart.toFixed(2)} = ` +
        `${weightedUnitCost.toFixed(2)}`;

    // ② 配比后成本（80%×172.80 + 20%×501.80 = 238.60）
    const ratioFormulaParts = enriched
        .filter(c => c.ratio > 0.0001)
        .map(
            c =>
                `${(c.ratio * 100).toFixed(0)}% × ${c.unit_cost.toFixed(2)}`
        );
    const ratioFormula =
        `配比后成本：` +
        `${ratioFormulaParts.join(" + ")} = ` +
        `${totalCost.toFixed(2)}`;

    // ---- 构造表格 HTML ----
    return `
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
                    <th class="border px-3 py-2 text-right">配比后成本</th>
                </tr>
            </thead>
            <tbody>
                ${enriched
                    .map(c => {
                        const pct =
                            c.ratio > 0.0001
                                ? `${Math.round(c.ratio * 100)}%`
                                : "—";
                        const contribution =
                            c.ratio > 0.0001
                                ? c.cost_contribution.toFixed(2)
                                : "0.00";

                        return `
                        <tr class="${c.ratio > 0.0001 ? "" : "text-gray-400"}">
                            <td class="border px-3 py-2">${c.name}</td>
                            <td class="border px-3 py-2 text-right">${pct}</td>
                            <td class="border px-3 py-2 text-right">${c.calorific}</td>
                            <td class="border px-3 py-2 text-right">${c.price.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${c.short_transport.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${c.screening_fee.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${c.crushing_fee.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${blendingFee.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${c.unit_cost.toFixed(2)}</td>
                            <td class="border px-3 py-2 text-right">${contribution}</td>
                        </tr>`;
                    })
                    .join("")}
            </tbody>
            <tfoot class="bg-gray-100 font-bold">
                <tr>
                    <td class="border px-3 py-2">合计</td>
                    <td class="border px-3 py-2 text-right"></td>
                    <td class="border px-3 py-2 text-right">${totalCal}</td>
            
                    <!-- 合并 6 列，显示计算公式 -->
                    <td class="border px-3 py-2 text-center text-xs md:text-sm" colspan="6">
            
                        <!-- 组合公式（无0项） -->
                        ${
                            enriched
                            .filter(c => c.ratio > 0.0001)
                            .map(c => {
            
                                const parts = [];
            
                                if (c.price !== 0) parts.push(c.price.toFixed(2));
                                if (c.short_transport !== 0) parts.push(c.short_transport.toFixed(2));
                                if (c.screening_fee !== 0) parts.push(c.screening_fee.toFixed(2));
                                if (c.crushing_fee !== 0) parts.push(c.crushing_fee.toFixed(2));
                                if (blendingFee !== 0) parts.push(blendingFee.toFixed(2));
            
                                if (parts.length === 0) parts.push(c.price.toFixed(2));
            
                                const pct = (c.ratio * 100).toFixed(0) + "%";
            
                                return `(${parts.join(" + ")})*${pct}`;
                            })
                            .join(" + ")
                        }
            
                        <!-- 不含税蓝色 + 含税红色 -->
                        = <span class="text-blue-600 font-bold text-lg">${Math.round(totalCost)}</span>
                        （含13%增值税：
                            <span class="text-red-600 font-bold text-lg">${Math.round((totalCost * 1.13))}</span>
                        ）
                    </td>
            
                    <td class="border px-3 py-2 text-right text-blue-600 font-bold text-lg">
                        ${Math.round(totalCost)}
                    </td>
                </tr>
            </tfoot>       
        </table>
    `;
}

// function buildDetailTable(plan) {
//     return `
//         <h3 class="font-semibold mb-2">配比详情</h3>
//         <table class="min-w-full text-sm bg-white rounded shadow">
//             <thead>
//                 <tr class="bg-gray-100">
//                     <th class="border px-3 py-2 text-left">煤种</th>
//                     <th class="border px-3 py-2 text-right">比例</th>
//                     <th class="border px-3 py-2 text-right">热值贡献</th>
//                     <th class="border px-3 py-2 text-right">成本贡献</th>
//                 </tr>
//             </thead>
//             <tbody>
//                 ${plan.items.map(item => {
//         const pct = Math.round(item.ratio * 100);
//         const heat = Math.round(item.calorific * item.ratio);
//         const cost = Math.round(
//             (item.price + item.short_transport + item.screening_fee + item.crushing_fee + 1.8) * item.ratio
//         );
//         return `
//                         <tr>
//                             <td class="border px-3 py-2">${item.name}</td>
//                             <td class="border px-3 py-2 text-right">${pct}%</td>
//                             <td class="border px-3 py-2 text-right">${heat}</td>
//                             <td class="border px-3 py-2 text-right">${cost}</td>
//                         </tr>`;
//     }).join("")}
//             </tbody>
//         </table>
//     `;
// }

// =============================
// 初始化
// =============================
window.onload = () => {
    loadCoals();
};