function showLoading() {
    document.getElementById("loading-overlay").classList.remove("hidden");
}

function hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");
}

// =============================
// CCI：只从后端拿（后端返回 tooltip 所需全部字段）
// =============================
let latestCCI = null;

async function loadLatestCCI(calorific = 5500) {
    try {
        const res = await fetch(`/api/cci/latest?calorific=${calorific}`);
        const data = await res.json();

        if (!data.success) {
            latestCCI = null;
            return false;
        }

        latestCCI = data; // 直接存后端结构即可
        return true;
    } catch (e) {
        console.error("获取 CCI 失败", e);
        latestCCI = null;
        return false;
    }
}

function showCCITooltip(el) {
    const tooltip = el.querySelector(".cci-tooltip");
    if (tooltip) tooltip.classList.remove("hidden");
}

function hideCCITooltip(el) {
    const tooltip = el.querySelector(".cci-tooltip");
    if (tooltip) tooltip.classList.add("hidden");
}


// =============================
// 输入框自动选择内容（保留 UI 体验）+ 数值区间校验（UI兜底）
// =============================
function attachRangeValidator(inputId, min, max, message) {
    const input = document.getElementById(inputId);
    if (!input) return;

    let errorEl = document.createElement("div");
    errorEl.className = "text-red-600 text-sm mt-1 hidden";
    input.insertAdjacentElement("afterend", errorEl);

    input.addEventListener("input", () => {
        const v = parseFloat(input.value);

        if (input.value === "") {
            input.classList.remove("border-red-500");
            errorEl.classList.add("hidden");
            return;
        }

        if (isNaN(v) || v < min || v > max) {
            input.classList.add("border-red-500");
            errorEl.textContent = message;
            errorEl.classList.remove("hidden");
        } else {
            input.classList.remove("border-red-500");
            errorEl.classList.add("hidden");
        }
    });
}

function bindAutoSelect(containerSelector) {
    const inputs = document.querySelectorAll(
        `${containerSelector} input[type="text"],
         ${containerSelector} input[type="number"]`
    );

    inputs.forEach(input => {
        const handler = () => {
            if (!input.value) return;
            try {
                input.select();
            } catch {
            }
        };
        input.addEventListener('focus', handler);
        input.addEventListener('click', handler);
    });
}

function initAutoSelect() {
    bindAutoSelect("#coal-form");
    bindAutoSelect("#electric-form");
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAutoSelect);
} else {
    initAutoSelect();
}


// =============================
// 标签页切换（保持）
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
            const tableBody = document.getElementById('coal-table-body');
            if (tableBody) {
                tableBody.innerHTML = '';

                coals.forEach(coal => {
                    const row = document.createElement('tr');
                    row.setAttribute("data-id", coal.id);
                    row.classList.add("cursor-pointer", "hover:bg-blue-50");

                    const volatile = Number(coal.volatile ?? 0).toFixed(2);
                    const recovery = Number(coal.recovery ?? 0).toFixed(2);
                    const gValue = Number(coal.g_value ?? 0).toFixed(2);
                    const xValue = Number(coal.x_value ?? 0).toFixed(2);
                    const yValue = Number(coal.y_value ?? 0).toFixed(2);

                    row.innerHTML = `
                        <td class="py-2 px-4 border">${coal.name}</td>
                        <td class="py-2 px-4 border">${Number(coal.calorific ?? 0).toFixed(1)}</td>
                        <td class="py-2 px-4 border">${Number(coal.ash ?? 0).toFixed(2)}%</td>
                        <td class="py-2 px-4 border">${Number(coal.sulfur ?? 0).toFixed(2)}%</td>
                        <td class="py-2 px-4 border">${volatile}%</td>
                        <td class="py-2 px-4 border">${recovery}%</td>
                        <td class="py-2 px-4 border">${gValue}</td>
                        <td class="py-2 px-4 border">${xValue}</td>
                        <td class="py-2 px-4 border">${yValue}</td>
                        <td class="py-2 px-4 border">${Number(coal.price ?? 0).toFixed(1)}</td>
                        <td class="py-2 px-4 border">${Number(coal.short_transport ?? 0).toFixed(2)}</td>
                        <td class="py-2 px-4 border">${Number(coal.screening_fee ?? 0).toFixed(2)}</td>
                        <td class="py-2 px-4 border">${Number(coal.crushing_fee ?? 0).toFixed(2)}</td>
                        <td class="py-2 px-4 border text-center">
                            ${
                        coal.is_domestic
                            ? `<div class="flex justify-center items-center"><img src="/static/icons/china.svg" style="width:20px;height:20px;display:inline-block;"></div>`
                            : `<div class="flex justify-center items-center"><img src="/static/icons/global.svg" style="width:20px;height:20px;display:inline-block;"></div>`
                    }
                        </td>
                        <td class="py-2 px-4 border text-right">
                            ${Number(coal.stock ?? 0).toFixed(0)}
                        </td>
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

            loadCoalSelectionTable(coals);
        });
}

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
            <td class="py-2 px-3 border">${Number(coal.calorific ?? 0).toFixed(1)}</td>
            <td class="py-2 px-3 border">${Number(coal.price ?? 0).toFixed(1)}</td>
            <td class="border px-3 py-2 text-center">
                ${
            coal.is_domestic
                ? `<div class="flex justify-center items-center"><img src="/static/icons/china.svg" title="境内煤" style="width:20px;height:20px;display:inline-block;"></div>`
                : `<div class="flex justify-center items-center"><img src="/static/icons/global.svg" title="坑口煤" style="width:20px;height:20px;display:inline-block;"></div>`
        }
            </td>
        `;

        tableBody.appendChild(row);
    });
}


// =============================
// 原煤选择弹窗事件（保持）
// =============================
(function bindCoalSelectModal() {
    const btn = document.getElementById('coal-select-btn');
    const modal = document.getElementById('coal-select-modal');
    if (!btn || !modal) return;

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        modal.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!modal.contains(e.target) && !btn.contains(e.target)) {
            modal.classList.add('hidden');
        }
    });

    const btnAll = document.getElementById('select-all-coals');
    if (btnAll) {
        btnAll.addEventListener('click', () => {
            document.querySelectorAll('.coal-checkbox').forEach(cb => cb.checked = true);
        });
    }

    const btnClear = document.getElementById('clear-all-coals');
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            document.querySelectorAll('.coal-checkbox').forEach(cb => cb.checked = false);
        });
    }

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
// 原煤编辑 + 重置（保持）
// =============================
function editCoal(coal) {
    editingId = coal.id;

    const set = (id, value, digits) => {
        const el = document.getElementById(id);
        if (!el) return;

        if (typeof value === "string") {
            el.value = value;
            return;
        }
        if (value === undefined || value === null || value === "" || isNaN(Number(value))) {
            el.value = "";
        } else {
            el.value = (digits !== undefined) ? Number(value).toFixed(digits) : value;
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
    set('coal-stock', coal.stock, 0);

    const submitBtn = document.getElementById("coal-submit-btn");
    submitBtn.innerHTML = `<i class="fa fa-save mr-1"></i>保存修改`;
    submitBtn.classList.remove("bg-blue-600");
    submitBtn.classList.add("bg-green-600");

    document.getElementById("coal-delete-btn").classList.remove("hidden");
    document.getElementById("coal-cancel-btn").classList.remove("hidden");

    document.getElementById('coal-form').scrollIntoView({behavior: 'smooth'});
    document.getElementById("coal-is-domestic").value = coal.is_domestic ? 1 : 0;
}

function resetCoalFormState() {
    editingId = null;
    const form = document.getElementById('coal-form');
    if (form) form.reset();

    document.getElementById('coal-short-transport').value = 0;
    document.getElementById('coal-screening-fee').value = 0;
    document.getElementById('coal-crushing-fee').value = 0;
    document.getElementById("coal-is-domestic").value = 1;

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
if (coalCancelBtn) coalCancelBtn.addEventListener('click', resetCoalFormState);


// =============================
// 原煤表单提交（保持）
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
            crushing_fee: parseFloat(document.getElementById('coal-crushing-fee').value || 0),
            is_domestic: parseInt(document.getElementById("coal-is-domestic").value),
            stock: parseInt(document.getElementById('coal-stock').value || 0)
        };

        fetch('/api/coals', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(coal)
        })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    alert(data.message || "保存失败");
                    return;
                }
                alert(editingId ? '修改成功！' : '添加成功！');
                resetCoalFormState();
                loadCoals();
            });
    });
}


// =============================
// 删除原煤（保持）
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
// 配煤计算（/api/blend）（保持原渲染方式）
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

                // 如果你未来启用结果 Tab，这里仍兼容
                const tabResult = document.getElementById('tab-result');
                if (tabResult) tabResult.click();

                const indicators = document.getElementById('result-indicators');
                const unitCost = parseFloat(result.指标.单位成本).toFixed(2);
                const taxCost = parseFloat(result.指标.单位成本含税 ?? (result.指标.单位成本 * 1.13)).toFixed(2);

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
                                    <td class="py-2 px-4 border-b">${Number(item.ratio).toFixed(1)}%</td>
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
                            data: result.ratio.map(item => item.ratio)
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
// 桶水位更新（UI）
// =============================
function updateWaterLevel(tankEl, ratio) {
    const fill = tankEl.querySelector(".coal-oil-fill");
    const waterTop = tankEl.querySelector(".coal-oil-water-top");

    const h = tankEl.clientHeight;
    const visualZone = h * 0.75;
    const offset = h * 0.10;
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
            .map(cb => parseFloat(cb.value));
        const stepSizes = selectedSteps.length > 0 ? selectedSteps : [10];

        const target = {
            calorific: parseFloat(document.getElementById('electric-calorific').value),
            selected_coal_ids: selectedCoalIds,
            step_sizes: stepSizes,
            // ⭐⭐⭐ 三项费用：显式传给后端 ⭐⭐⭐
            fee_ceke_miaoliang: parseFloat(
                document.getElementById('fee-ceke-miaoliang')?.value || 0
            ),
            fee_miaoliang_caofeidian: parseFloat(
                document.getElementById('fee-miaoliang-caofeidian')?.value || 0
            ),
            fee_misc: parseFloat(
                document.getElementById('fee-misc')?.value || 0
            )
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
                listDiv.innerHTML = `<div class="text-center py-4 text-red-500">${result.message || '动力煤配比计算失败'}</div>`;
                return;
            }

            // // 后端已经把每个 plan 的 CCI 信息都补齐了；这里仍保留全局兜底（可选）
            // if (!latestCCI) await loadLatestCCI();
            // 确保 CCI 已按目标热值加载
            await loadLatestCCI(target.calorific);

            renderElectricPlans(result.plans);
        } catch (error) {
            listDiv.innerHTML = `<div class="text-center py-4 text-red-500">计算失败：${error.message}</div>`;
        }
    });
}


// =============================
// 电煤方案渲染（前端只渲染；不再计算 tooltip / detail 表）
// =============================
function

renderElectricPlans(plans) {
    const list = document.getElementById("electric-plan-list");
    list.innerHTML = "";

    if (!plans || plans.length === 0) {
        list.innerHTML = `<div class="text-center py-4 text-gray-500">暂无满足条件的方案</div>`;
        return;
    }

    plans.forEach((plan, index) => {
        const cost = Math.round(plan.mix_cost);
        const taxCost = Math.round(plan.mix_cost_tax ?? (plan.mix_cost * 1.13));
        const calorific = Math.round(plan.mix_calorific);
        const isBest = index === 0;

        // CCI：优先用 plan.cci（后端已算），没有再用 latestCCI
        const cciObj = plan.cci || latestCCI || null;
        const cciPriceText = (cciObj && cciObj.cci_price_text) ? cciObj.cci_price_text : "—";

        // const cciObj = plan.cci || latestCCI;
        // const cciPriceText = cciObj?.cci_price_text ?? "—";
        const cciTooltip = (cciObj && cciObj.tooltip) ? cciObj.tooltip : {
            bg_style: "background-color:#f3f4f6;",
            arrow_color: "#f3f4f6",
            tip_text: "暂无 CCI 数据"
        };

        // 后端已按 ratio 从小到大排序，并提供 weight/ratio_pct
        const sortedItems = plan.items || [];

        const coalBlocks = sortedItems.map(item => {
            const pct = (item.ratio_pct ?? (item.ratio * 100)).toFixed ? (item.ratio_pct).toFixed(1) : (item.ratio * 100).toFixed(1);
            const weight = item.weight ?? 1;

            return `
                <div class="coal-oil-tank-wrapper">
                    <div class="coal-oil-tank">
                        <div class="coal-oil-fill"></div>
                        <div class="coal-oil-water-top"></div>
                        <div class="coal-oil-content">
                            <div class="coal-oil-name">${item.name}</div>
                            <div class="coal-oil-pct">${pct}%</div>
                            <div class="coal-oil-calorific">${Math.round(item.calorific)} 大卡</div>
                            <div class="coal-oil-pct">${Math.round(weight)}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        const card = document.createElement("div");
        card.className = "bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition mb-6 overflow-visible";

        card.innerHTML = `
            <div class="plan-grid overflow-visible">
                <div class="flex flex-col">
                    <div class="flex items-center">
                        <span class="text-xl font-bold">配煤方案 ${index + 1}</span>
                        ${isBest ? `<span class="ml-2 px-2 py-1 bg-red-100 text-red-600 text-sm rounded">最低成本</span>` : ""}
                    </div>
                    <div class="text-gray-700 text-xl mt-1 pl-1">
                        热值：<span class="font-semibold">${calorific} kcal</span>
                    </div>
                </div>

                <div class="flex flex-wrap gap-4 items-center" style="margin-left:4px;">
                    ${coalBlocks}
                </div>

                <div class="flex items-center justify-end space-x-6 overflow-visible">
                    <div class="text-gray-800 text-base font-bold leading-8 text-right mr-8">

                        <div class="flex justify-end whitespace-nowrap overflow-visible">
                            <span class="inline-flex items-center font-semibold"
                                  onmouseenter="showCCITooltip(this)"
                                  onmouseleave="hideCCITooltip(this)">
                                热值${calorific}卡港口销售价（含税）：
                                <span class="relative inline-block cursor-help text-lg font-bold ml-1">
                                    ${cciPriceText}

                                    <div
                                        class="
                                            cci-tooltip
                                            absolute
                                            left-1/2
                                            -translate-x-1/2
                                            bottom-full
                                            mb-3
                                            hidden
                                            text-sm font-semibold
                                            text-gray-800
                                            rounded-xl
                                            shadow-2xl
                                            px-4
                                            py-3
                                            whitespace-nowrap
                                        "
                                        style="${cciTooltip.bg_style}; z-index: 999999;"
                                    >
                                        <span
                                            class="
                                                absolute
                                                top-full
                                                left-1/2
                                                -translate-x-1/2
                                                w-0 h-0
                                                border-l-[7px]
                                                border-r-[7px]
                                                border-t-[7px]
                                                border-l-transparent
                                                border-r-transparent
                                            "
                                            style="margin-top:-1px; border-top-color:${cciTooltip.arrow_color};"
                                        ></span>
                                       <span class="text-left block"> ${cciTooltip.tip_text}</span>
                                    </div>
                                </span>
                            </span>
                        </div>

                        <div class="flex justify-end whitespace-nowrap">
                            <span>倒推至策克价格（含税）：</span>
                            <span style="font-size: 18px;">${plan.reverse_ceke_price ?? 400}元/吨</span>
                        </div>

                        <div class="flex justify-end whitespace-nowrap">
                            <span>策克成本（含税）</span>
                            <span style="display:inline-block; width:16px; text-align:center;">：</span>
                            <span class="text-red-600" style="font-size: 18px;">${taxCost}元/吨</span>
                        </div>

                        <div class="flex justify-end whitespace-nowrap">
                            <span>预测销售毛利</span>
                            <span style="display:inline-block; width:16px; text-align:center;">：</span>
                            <span style="font-size: 18px;" class=" text-blue-600">${plan.gross_profit ?? 100}元/吨</span>
                        </div>
                    </div>

                    <button class="plan-confirm-btn" data-plan-index="${index}">
                        <i class="fa fa-check"></i>
                        <span class="text-base">确定使用该方案</span>
                    </button>
                </div>
            </div>
        `;
        // 确定使用该方案绑定事件
        const confirmBtn = card.querySelector(".plan-confirm-btn");
        confirmBtn.onclick = () => handleConfirmPlan(confirmBtn, plan);

        // 详情区域：直接用后端返回的 HTML
        const detail = document.createElement("div");
        detail.className = "hidden bg-gray-50 border border-gray-200 rounded-lg p-4 mt-4";
        detail.innerHTML = plan.detail_html || `<div class="text-gray-500 text-sm">暂无详情</div>`;

        const toggle = document.createElement("button");
        toggle.className = "detail-toggle-btn";
        toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 展开详情';

        toggle.onclick = () => {
            const isHidden = detail.classList.contains("hidden");
            detail.classList.toggle("hidden");

            if (isHidden) {
                toggle.classList.add("expanded");
                toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 收起详情';
            } else {
                toggle.classList.remove("expanded");
                toggle.innerHTML = '<i class="fa fa-chevron-down"></i> 展开详情';
            }
        };

        card.appendChild(toggle);
        card.appendChild(detail);
        list.appendChild(card);

        // 桶水位：仍由前端做纯 UI
        const tanks = card.querySelectorAll(".coal-oil-tank");
        sortedItems.forEach((item, i) => {
            updateWaterLevel(tanks[i], item.ratio);
        });
    });
}


//========"确定使用该方案" 处理函数 start
// ======== 确定使用该方案（最终稳定版）========
async function handleConfirmPlan(button, planData) {
    try {
        showLoading();   // ⭐ 显示转圈
        const card = button.closest(".bg-white");
        const detail = card.querySelector(".detail-toggle-btn + div");
        const toggleBtn = card.querySelector(".detail-toggle-btn");

        // 1️⃣ 强制展开详情
        if (detail && detail.classList.contains("hidden")) {
            toggleBtn.click();
            await new Promise(r => setTimeout(r, 400));
        }

        // 2️⃣ 使用截图专用容器
        const wrapper = document.getElementById("screenshot-wrapper");
        wrapper.innerHTML = "";

        // 3️⃣ 深拷贝整个方案卡片
        const clone = card.cloneNode(true);
        // ⭐⭐⭐ 关键修复：截图时解除桶的裁剪coal-oil-pct coal-oil-tank
        // clone.querySelectorAll('.coal-oil-pct').forEach(tank => {
        //     tank.style.overflow = 'visible';
        // });
        // ⭐ 仅截图时：整体上移桶内内容
        clone.querySelectorAll('.coal-oil-content').forEach(el => {
            el.style.top = '-0.5px';
        });

        // 4️⃣ 移除 absolute / fixed（关键）
        clone.querySelectorAll("*").forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.position === "absolute" || style.position === "fixed") {
                el.style.position = "static";
            }
        });

        wrapper.appendChild(clone);

        // 5️⃣ 等 DOM 稳定
        await new Promise(r => setTimeout(r, 300));

        // 6️⃣ 截图（重点参数）
        const canvas = await html2canvas(wrapper, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',

            width: wrapper.scrollWidth,
            height: wrapper.scrollHeight,
            windowWidth: wrapper.scrollWidth,
            windowHeight: wrapper.scrollHeight   // ⭐⭐⭐ 关键在这一行
        });

        const imageBase64 = canvas.toDataURL("image/png", 1.0);

        // 7️⃣ 发给后端
        const res = await fetch("/api/confirm_plan", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                plan: planData,
                screenshot: imageBase64
            })
        });

        const result = await res.json();
        if (result.success) {
            alert(`该方案已成功发送邮件给：\n${result.recipients }`);
        } else {
            alert("发送失败：" + result.message);
        }
    } catch (e) {
        alert("发送失败：" + e.message);
    } finally {
        hideLoading();   // ⭐ 一定要关
    }
}

//=========end

// =============================
// 初始化（加载数据 + 绑定校验）
// =============================
window.onload = () => {
    loadCoals();
    loadLatestCCI();

    attachRangeValidator("coal-calorific", 1000, 9000, "发热量必须在 1000~9000 之间");
    attachRangeValidator("electric-calorific", 1000, 9000, "发热量必须在 1000~9000 之间");
    attachRangeValidator("target-calorific", 1000, 9000, "发热量必须在 1000~9000 之间");

    attachRangeValidator("coal-ash", 1, 50, "灰分必须在 1~50 之间");
    attachRangeValidator("coal-sulfur", 0.1, 3, "硫分必须在 0.1~3 之间");
    attachRangeValidator("coal-volatile", 0, 50, "挥发分必须在 0~50 之间");
    attachRangeValidator("coal-recovery", 0, 100, "回收率必须在 0~100 之间");
    attachRangeValidator("coal-g_value", 0, 90, "G 值必须在 0~90 之间");
    attachRangeValidator("coal-screening-fee", 0, 20, "过筛费必须在 0~20 之间");
    attachRangeValidator("coal-crushing-fee", 0, 10, "破碎费必须在 0~10 之间");
    attachRangeValidator("coal-short-transport", 0, 30, "短倒费必须在 0~30 之间");
    attachRangeValidator("coal-price", 0, 1000, "价格必须在 0~1000 之间");
};

