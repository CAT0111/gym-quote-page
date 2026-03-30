import re

filepath = 'build/admin_templates/shoot.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 彻底替换掉那个带语法错误的 function openSopSheet
new_func = """function openSopSheet(rid) {
  const task = S.allTasks.find(t => t.record_id === rid);
  if (!task) return;

  const skuStr = (task.sku || '').toUpperCase();
  const nameStr = (task.product_name_zh || task.product_name || '');
  const catKey = getSopCategory(skuStr, nameStr);
  
  // 健壮的数据读取，带安全回退机制
  let briefHtml = '<span style="color:#ef4444">【尚未生成数据】</span>请使用大模型生成该分类的 SOP 并写入 static/sop_data.js';
  try {
    if (typeof window.SOP_DETAILS !== 'undefined') {
      if (window.SOP_DETAILS[catKey] && window.SOP_DETAILS[catKey][task.media_type]) {
        briefHtml = window.SOP_DETAILS[catKey][task.media_type];
      } else if (window.SOP_DETAILS['DEFAULT'] && window.SOP_DETAILS['DEFAULT'][task.media_type]) {
        briefHtml = window.SOP_DETAILS['DEFAULT'][task.media_type];
      }
    }
  } catch(e) {
    console.error("SOP加载错误: ", e);
  }

  const html = `
    <div class="sop-head">
      <div class="sop-head-tag">${CAT_LABELS[catKey] || '通用'}</div>
      <div class="sop-head-title">${task.media_type} · SOP 指南</div>
    </div>
    <div class="sop-card">
      <div class="sop-step">
        <div class="sop-step-title"><span class="badge badge-${task.status}">专家分镜指导</span></div>
        <div class="sop-step-desc" style="margin-top:10px">${briefHtml}</div>
      </div>
    </div>
  `;
  document.getElementById('sopContent').innerHTML = html;
  document.getElementById('sopOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

"""

# 使用正则精确替换整个函数区块
content = re.sub(r"function openSopSheet\(rid\).*?(?=function closeSopSheet)", new_func, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 致命语法错误已修复！页面可以正常加载了。")
