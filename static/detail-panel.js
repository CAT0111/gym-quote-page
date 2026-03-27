(function() {
  var overlay = null;
  var currentSku = null;
  var currentSelectedItem = null;
  var currentGridItem = null;
  var touchStartY = 0;

  var TEXTS = {
    en: { videoLabel:'Watch 60s Test Video', videoSoon:'Video coming soon', close:'Close ✕', askWA:'Ask about this machine on WhatsApp', fob:'FOB', inquire:'Inquire', partsBtn:'View Spare Parts & Maintenance Cycle', qtyLabel:'Qty',
          maintTitle:'Spare Parts & Maintenance', maintBack:'Back', maintParts:'SPARE PARTS LIST', maintPartName:'Part', maintPartQty:'Qty', maintPartCycle:'Cycle', maintSchedule:'MAINTENANCE SCHEDULE', maintDurability:'DURABILITY', maintFooter:'Need any spare part? Contact us on WhatsApp for fast delivery.',
          badgeFullKit:'Full spare parts kit shipped with equipment', badgeLongLife:'Industrial-grade durability, minimal maintenance', badgeConsumable:'Consumable — replace on schedule',
          maintCareTitle:'Maintenance Guide', maintCareLife:'Long-life Equipment' },
    zh: { videoLabel:'观看60秒试机视频', videoSoon:'视频即将上线', close:'关闭 ✕', askWA:'通过 WhatsApp 咨询此器械', fob:'FOB', inquire:'询价', partsBtn:'查看备件包和保养维护周期', qtyLabel:'数量',
          maintTitle:'备件包与保养维护', maintBack:'返回', maintParts:'备件清单', maintPartName:'部件', maintPartQty:'备量', maintPartCycle:'更换周期', maintSchedule:'保养周期表', maintDurability:'耐用性说明', maintFooter:'需要任何备件？WhatsApp联系我们，快速发货。',
          badgeFullKit:'全套备件已随货配送', badgeLongLife:'工业级耐久，极少维护', badgeConsumable:'消耗品 · 按周期整体更换',
          maintCareTitle:'保养指南', maintCareLife:'长寿命设备' },
    ms: { videoLabel:'Tonton Video Ujian 60s', videoSoon:'Video akan datang', close:'Tutup ✕', askWA:'Tanya tentang mesin ini di WhatsApp', fob:'FOB', inquire:'Tanya Harga', partsBtn:'Lihat Alat Ganti & Kitaran Penyelenggaraan', qtyLabel:'Kuantiti',
          maintTitle:'Alat Ganti & Penyelenggaraan', maintBack:'Kembali', maintParts:'SENARAI ALAT GANTI', maintPartName:'Bahagian', maintPartQty:'Kuantiti', maintPartCycle:'Kitaran', maintSchedule:'JADUAL PENYELENGGARAAN', maintDurability:'KETAHANAN', maintFooter:'Perlukan alat ganti? Hubungi kami di WhatsApp untuk penghantaran pantas.',
          badgeFullKit:'Kit alat ganti lengkap dihantar bersama peralatan', badgeLongLife:'Ketahanan gred industri, penyelenggaraan minimum', badgeConsumable:'Boleh guna — ganti mengikut jadual',
          maintCareTitle:'Panduan Penyelenggaraan', maintCareLife:'Peralatan Jangka Hayat Panjang' }
  };
  var SPEC_KEYS = {
    en: {},
    zh: {
      'Weight Stack':'配重片','Dimensions':'尺寸','Net Weight':'净重','Gross Weight':'毛重','Target':'目标肌群','Feature':'特点','Type':'类型',
      'Accessories':'配件','Bar Weight':'杠铃重量','Capacity':'容量','Angles':'角度调节','Motor':'电机','Speed':'速度','Belt':'跑带尺寸',
      'Display':'显示屏','Resistance':'阻力','Stride':'步幅','Flywheel':'飞轮','Rail Length':'滑轨长度',
      'Loading':'加载方式','Packing':'包装尺寸','Material':'材质','Installation':'安装方式','Note':'备注',
      'Crate 1':'木箱1','Crate 2':'木箱2','Crate Volume':'木箱体积','Model':'型号','Power':'电源',
      'Incline':'坡度','Max Load':'最大承重','Roller Diameter':'滚筒直径','Drive':'驱动类型','Handlebar':'扶手','Container':'装柜量',
      'Spec':'规格','Total Qty':'总数量','Total Net Weight':'总净重','Total Gross Weight':'总毛重','Total Weight':'总重量',
      'Bore':'孔径','Length':'长度','Diameter':'直径','Bearing':'轴承','Storage':'存放方式',
      'Unit Size':'单件尺寸','Unit Weight':'单件重量','Size':'尺寸','Weight':'重量',
      'Coverage':'覆盖面积','Thickness':'厚度','Tile Size':'拼接规格','Lock':'锁具',
      'Bar Weight':'杠铃自重'
    },
    ms: {
      'Weight Stack':'Tumpukan Berat','Dimensions':'Dimensi','Net Weight':'Berat Bersih','Gross Weight':'Berat Kasar','Target':'Sasaran','Feature':'Ciri','Type':'Jenis',
      'Accessories':'Aksesori','Bar Weight':'Berat Bar','Capacity':'Kapasiti','Angles':'Sudut','Motor':'Motor','Speed':'Kelajuan','Belt':'Tali Pinggang',
      'Display':'Paparan','Resistance':'Rintangan','Stride':'Langkah','Flywheel':'Roda Tenaga','Rail Length':'Panjang Rel',
      'Loading':'Jenis Beban','Packing':'Saiz Pembungkusan','Material':'Bahan','Installation':'Pemasangan','Note':'Nota',
      'Crate 1':'Peti 1','Crate 2':'Peti 2','Crate Volume':'Isipadu Peti','Model':'Model','Power':'Kuasa',
      'Incline':'Kecerunan','Max Load':'Beban Maks','Roller Diameter':'Diameter Penggelek','Drive':'Pemacu','Handlebar':'Pemegang','Container':'Muatan Kontena',
      'Spec':'Spesifikasi','Total Qty':'Jumlah Kuantiti','Total Net Weight':'Jumlah Berat Bersih','Total Gross Weight':'Jumlah Berat Kasar','Total Weight':'Jumlah Berat',
      'Bore':'Lubang','Length':'Panjang','Diameter':'Diameter','Bearing':'Galas','Storage':'Penyimpanan',
      'Unit Size':'Saiz Unit','Unit Weight':'Berat Unit','Size':'Saiz','Weight':'Berat',
      'Coverage':'Kawasan Liputan','Thickness':'Ketebalan','Tile Size':'Saiz Jubin','Lock':'Kunci',
      'Bar Weight':'Berat Bar'
    }
  };
  var SPEC_VALS = {
    en: {},
    zh: {
      'Standard pin-loaded':'标配插片式','Plate loaded':'挂片式',
      'Rear Delt / Chest':'后三角肌 / 胸大肌','Front / Middle Deltoid':'三角肌前束 / 中束',
      'Lats / Rhomboids / Biceps':'背阔肌 / 菱形肌 / 二头肌','Biceps':'肱二头肌','Hamstrings':'腘绳肌',
      'Quadriceps':'股四头肌','Inner / Outer Thigh':'大腿内侧 / 外侧','Middle Deltoid':'三角肌中束',
      'Lats / Teres Major':'背阔肌 / 大圆肌','Deltoid / Triceps':'三角肌 / 肱三头肌',
      'Lats / Rhomboids':'背阔肌 / 菱形肌','Upper Chest / Front Deltoid':'胸大肌上束 / 三角肌前束',
      'Outer Chest / Serratus Anterior':'胸大肌外沿 / 前锯肌','Triceps / Lats':'肱三头肌 / 背阔肌',
      'Lower Chest':'胸大肌下束','Mid Chest':'胸大肌中束',
      'Quads / Glutes':'股四头肌 / 臀大肌','Quads / Glutes / Hamstrings':'股四头肌 / 臀大肌 / 腘绳肌',
      'Chest / Front Deltoid / Triceps':'胸大肌 / 三角肌前束 / 肱三头肌',
      'Chest / Back / Shoulders multi-function':'胸 / 背 / 肩多功能',
      'Full body multi-joint':'全身多关节','Full body (core focused)':'全身（核心为主）',
      'Full body (upper + lower limbs linked)':'全身（上下肢联动）',
      'Full body explosive power / Core / Glutes & Legs':'全身爆发力 / 核心 / 臀腿',
      'Full body (squat / bench press / row / shrug etc.)':'全身（深蹲/卧推/划船/耸肩等）',
      'Full body (lat pull / low row / pec fly / legs etc.)':'全身（高拉/低拉/蝴蝶夹胸/腿部等）',
      'Squat / Deadlift / Bench Press / Pull-up':'深蹲 / 硬拉 / 卧推 / 引体向上',
      'Erector Spinae / Glutes':'竖脊肌 / 臀大肌','Lats / Biceps / Core':'背阔肌 / 二头肌 / 核心',
      'Shoulders / Arms / Glutes / Legs':'肩部 / 手臂 / 臀部 / 腿部',
      'Bicep curl / Triceps':'二头肌弯举 / 三头肌',
      'Pec fly + reverse fly 2-in-1':'蝴蝶夹胸+反飞鸟二合一',
      'Adjustable handle':'把手可调','Quick-adjust key':'快调键',
      'Adjustable backrest, single machine switches inner/outer':'靠背可调，内外侧一机切换',
      'Adjustable seat, stepless hi-lo pulley':'座椅可调，高低滑轮无级调节',
      'Independent diverging arms':'分动独立臂设计',
      'Adjustable foot plate height & travel range':'踏板高低可调，行程可调节',
      'Flat / Incline / Decline multi-angle adjustable':'平/上斜/下斜多角度可调',
      'Pairs with open squat rack, flush-mount installation':'配合开放深蹲架使用，嵌入式安装',
      'High-density rubber + solid wood composite':'高密度橡胶+实木复合',
      'Plate loaded (Olympic barbell + plates)':'挂片式（奥林匹克杠铃+杠铃片）',
      'Anti-static, anti-EMI, anti-slip side rails, belt anti-drift design':'防静电、抗电磁、防滑边条、防跑带跑偏设计',
      'Magnetic':'磁控','Air (infinite)':'风阻（无极）','Rear-wheel drive':'后轮驱动','PU foam':'PU发泡',
      'Injection-molded shell, durable & aesthetic':'注塑外壳，美观结实耐用',
      'Chrome / rubber-coated (per factory)':'电镀/包胶（按厂家确认）',
      'Cast iron / rubber-coated':'铸铁/包胶','Cast iron + powder coat / competition KB':'铸铁+喷塑/竞技壶铃',
      '45# steel':'45#钢','Bearing + bronze bushing':'轴承+铜套','Dual bearing + dual bronze bushing':'双轴承+双铜套',
      'Polyester / hemp':'涤纶/麻绳','Wall-mounted anchor point':'墙面固定锚点','Ceiling / beam anchor point':'天花板/横梁固定锚点',
      'Wall-mounted hook rack':'挂架上墙','NBR / TPE':'NBR/TPE','EVA / EPP':'EVA/EPP',
      'Plywood + anti-slip soft cover':'多层板+防滑软包','Wall-mounted bolts, load-bearing wall required':'壁挂螺栓固定，需承重墙',
      'EPDM rubber granule':'EPDM橡胶颗粒','High-density EPDM rubber':'高密度EPDM橡胶',
      'Wall adhesive + corner brackets':'墙面粘贴+角码固定','Cold-rolled steel / ABS plastic':'冷轧钢板/ABS塑料',
      'Combination lock or electronic lock':'密码锁或电子锁','LED display':'LED显示屏'
    },
    ms: {
      'Standard pin-loaded':'Beban pin standard','Plate loaded':'Beban plat',
      'Rear Delt / Chest':'Delt Belakang / Dada','Front / Middle Deltoid':'Deltoid Depan / Tengah',
      'Lats / Rhomboids / Biceps':'Lat / Rhomboid / Bisep','Biceps':'Bisep','Hamstrings':'Hamstring',
      'Quadriceps':'Kuadrisep','Inner / Outer Thigh':'Peha Dalam / Luar','Middle Deltoid':'Deltoid Tengah',
      'Lats / Teres Major':'Lat / Teres Major','Deltoid / Triceps':'Deltoid / Trisep',
      'Lats / Rhomboids':'Lat / Rhomboid','Upper Chest / Front Deltoid':'Dada Atas / Deltoid Depan',
      'Outer Chest / Serratus Anterior':'Dada Luar / Serratus Anterior','Triceps / Lats':'Trisep / Lat',
      'Lower Chest':'Dada Bawah','Mid Chest':'Dada Tengah',
      'Quads / Glutes':'Kuad / Glut','Quads / Glutes / Hamstrings':'Kuad / Glut / Hamstring',
      'Chest / Front Deltoid / Triceps':'Dada / Deltoid Depan / Trisep',
      'Chest / Back / Shoulders multi-function':'Dada / Belakang / Bahu pelbagai fungsi',
      'Full body multi-joint':'Seluruh badan pelbagai sendi','Full body (core focused)':'Seluruh badan (fokus teras)',
      'Full body (upper + lower limbs linked)':'Seluruh badan (anggota atas + bawah)',
      'Full body explosive power / Core / Glutes & Legs':'Kuasa letupan seluruh badan / Teras / Glut & Kaki',
      'Full body (squat / bench press / row / shrug etc.)':'Seluruh badan (squat / bench press / row / shrug dll.)',
      'Full body (lat pull / low row / pec fly / legs etc.)':'Seluruh badan (lat pull / low row / pec fly / kaki dll.)',
      'Squat / Deadlift / Bench Press / Pull-up':'Squat / Deadlift / Bench Press / Pull-up',
      'Erector Spinae / Glutes':'Erector Spinae / Glut','Lats / Biceps / Core':'Lat / Bisep / Teras',
      'Shoulders / Arms / Glutes / Legs':'Bahu / Lengan / Glut / Kaki',
      'Bicep curl / Triceps':'Bisep curl / Trisep',
      'Magnetic':'Magnetik','Air (infinite)':'Udara (tanpa had)','Rear-wheel drive':'Pemacu roda belakang','PU foam':'Busa PU',
      'LED display':'Paparan LED'
    }
  };

  function getLang() { return (window.__QL_LANG && window.__QL_LANG.current()) || 'en'; }
  function t(key) { var l = getLang(); return (TEXTS[l] && TEXTS[l][key]) || TEXTS.en[key] || key; }
  function trSpecKey(key) { var l = getLang(); return (SPEC_KEYS[l] && SPEC_KEYS[l][key]) || key; }
  function trSpecVal(val) { var l = getLang(); return (SPEC_VALS[l] && SPEC_VALS[l][val]) || val; }
  function prodName(gi) {
    var l = getLang();
    if (l === 'zh' && gi.dataset.nameZh) return gi.dataset.nameZh;
    if (l === 'ms' && gi.dataset.nameMs) return gi.dataset.nameMs;
    return gi.dataset.name;
  }

  /* ---- helpers for multilang maintenance fields ---- */
  function ml(obj, field) {
    var l = getLang();
    if (l === 'zh') return obj[field + '_zh'] || obj[field] || '';
    if (l === 'ms') return obj[field + '_ms'] || obj[field] || '';
    return obj[field] || '';
  }

  /* ---- read maintenance data from DOM attribute ---- */
  function getMaintData(gridItem) {
    var raw = gridItem.getAttribute('data-maintenance');
    if (!raw || raw === 'null' || raw === 'None') return null;
    try { return JSON.parse(raw); } catch(e) { return null; }
  }

  /* ---- SVG icons ---- */
  var playSvg = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
  var waSvg = '<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/></svg>';
  var boxSvg = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 14H5v-2h14v2zm0-4H5v-2h14v2zm0-4H5V6h14v2z"/></svg>';
  var shieldSvg = '<svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>';
  var backArrowSvg = '<svg viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>';
  var durableStarSvg = '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>';
  var waSmallSvg = '<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/></svg>';

  /* ---- build maintenance page HTML ---- */
  function buildMaintPage(maint, sku) {
    var l = getLang();
    var badge = maint.badge || 'full-kit';
    var badgeText;
    if (l === 'zh') badgeText = maint.badge_text_zh || maint.badge_text || '';
    else if (l === 'ms') badgeText = maint.badge_text_ms || maint.badge_text || '';
    else badgeText = maint.badge_text || '';

    var parts = maint.spare_parts || [];
    var sched = maint.schedule || [];
    var durNote;
    if (l === 'zh') durNote = maint.durability_note_zh || maint.durability_note || '';
    else if (l === 'ms') durNote = maint.durability_note_ms || maint.durability_note || '';
    else durNote = maint.durability_note || '';

    var badgeClass = badge === 'consumable' ? ' consumable' : '';
    var shieldIconClass = badge === 'consumable' ? ' consumable' : '';

    var html = '';
    html += '<div class="maint-header">';
    html += '<button class="maint-back-btn">' + backArrowSvg + ' ' + t('maintBack') + '</button>';
    html += '</div>';
    html += '<div class="maint-scroll">';

    /* shield */
    html += '<div class="maint-shield">';
    html += '<div class="maint-shield-icon' + shieldIconClass + '">' + shieldSvg + '</div>';
    html += '<div><div class="maint-shield-title">' + t('maintTitle') + '</div>';
    html += '<div class="maint-shield-sub">' + sku + '</div></div>';
    html += '</div>';

    /* badge */
    html += '<div class="maint-badge' + badgeClass + '">' + shieldSvg + ' ' + badgeText + '</div>';

    /* spare parts table — only if non-empty */
    if (parts.length > 0) {
      html += '<div class="maint-section-label">' + t('maintParts') + '</div>';
      html += '<table class="maint-table"><thead><tr><th>' + t('maintPartName') + '</th><th>' + t('maintPartQty') + '</th><th>' + t('maintPartCycle') + '</th></tr></thead><tbody>';
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        var pName = (l === 'zh') ? (p.name_zh || p.name) : (l === 'ms') ? (p.name_ms || p.name) : p.name;
        var pQty  = (l === 'zh') ? (p.qty_zh || p.qty) : (l === 'ms') ? (p.qty_ms || p.qty) : p.qty;
        var pCyc  = (l === 'zh') ? (p.cycle_zh || p.cycle) : (l === 'ms') ? (p.cycle_ms || p.cycle) : p.cycle;
        html += '<tr><td>' + pName + '</td><td>' + pQty + '</td><td>' + pCyc + '</td></tr>';
      }
      html += '</tbody></table>';
    }

    /* schedule — only if non-empty */
    if (sched.length > 0) {
      html += '<div class="maint-section-label">' + t('maintSchedule') + '</div>';
      html += '<div class="maint-schedule">';
      for (var j = 0; j < sched.length; j++) {
        var s = sched[j];
        var sInt = (l === 'zh') ? (s.interval_zh || s.interval) : (l === 'ms') ? (s.interval_ms || s.interval) : s.interval;
        var sAct = (l === 'zh') ? (s.action_zh || s.action) : (l === 'ms') ? (s.action_ms || s.action) : s.action;
        html += '<div class="maint-schedule-row"><div class="maint-schedule-interval">' + sInt + '</div><div class="maint-schedule-action">' + sAct + '</div></div>';
      }
      html += '</div>';
    }

    /* durability note */
    if (durNote) {
      html += '<div class="maint-section-label">' + t('maintDurability') + '</div>';
      html += '<div class="maint-durability">' + durNote + '</div>';
    }

    /* footer */
    html += '<div class="maint-footer">' + waSmallSvg + ' ' + t('maintFooter') + '</div>';

    html += '</div>'; /* close maint-scroll */

    return html;
  }

  /* ---- bind grid items ---- */
  document.querySelectorAll(".grid-item").forEach(function(item) {
    item.addEventListener("click", function() { openDetail(item); });
  });

  function openDetail(gridItem) {
    var sku = gridItem.dataset.sku;
    if (currentSku === sku && overlay) { closeDetail(); return; }
    if (overlay) removeOverlayImmediate();
    if (currentSelectedItem) currentSelectedItem.classList.remove("selected");

    currentGridItem = gridItem;

    var specs = JSON.parse(gridItem.dataset.specs);
    var specsHTML = "";
    for (var k in specs) {
      if (specs.hasOwnProperty(k)) {
        specsHTML += '<div class="detail-spec-row"><span class="detail-spec-label">' + trSpecKey(k) + '</span><span class="detail-spec-value">' + trSpecVal(specs[k]) + '</span></div>';
      }
    }

    var name = prodName(gridItem);
    var videoUrl = gridItem.dataset.video || "";
    var lang = getLang();
    var priceRaw = "";
    if (lang === "zh" && gridItem.dataset.priceCny) {
      priceRaw = "¥" + gridItem.dataset.priceCny;
    } else if (lang === "ms" && gridItem.dataset.priceMyr) {
      priceRaw = "RM" + gridItem.dataset.priceMyr;
    } else if (gridItem.dataset.priceUsd) {
      priceRaw = "$" + gridItem.dataset.priceUsd;
    }
    var qty = parseInt(gridItem.dataset.qty) || 1;

    var priceHTML;
    if (priceRaw) {
      priceHTML = priceRaw + ' <span style="font-size:14px;color:rgba(255,255,255,.35);font-weight:400">' + t('fob') + '</span>';
    } else {
      priceHTML = '<span style="font-size:16px">' + t('inquire') + '</span>';
    }

    var qtyHTML = '';
    if (qty > 1) {
      qtyHTML = '<div style="display:inline-block;background:rgba(200,164,78,.15);border:1px solid rgba(200,164,78,.25);color:#c8a44e;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:700;margin-bottom:8px">' + t('qtyLabel') + ': ' + qty + '</div>';
    }

    var mediaHTML;
    if (videoUrl) {
      mediaHTML = '<div class="detail-media">' +
        '<video controls preload="metadata" playsinline poster="' + gridItem.dataset.img + '"><source src="' + videoUrl + '" type="video/mp4"></video>' +
        '<div class="detail-media-label">' + playSvg + '<span data-en="' + TEXTS.en.videoLabel + '" data-zh="' + TEXTS.zh.videoLabel + '" data-ms="' + TEXTS.ms.videoLabel + '">' + t('videoLabel') + '</span></div>' +
        '</div>';
    } else {
      mediaHTML = '<div class="detail-image">' +
        '<img src="' + gridItem.dataset.img + '" alt="' + name + '">' +
        '<div class="detail-image-badge">' + playSvg + '<span data-en="' + TEXTS.en.videoSoon + '" data-zh="' + TEXTS.zh.videoSoon + '" data-ms="' + TEXTS.ms.videoSoon + '">' + t('videoSoon') + '</span></div>' +
        '</div>';
    }

    var waNum = document.body.dataset.whatsapp || "8613800000000";

    overlay = document.createElement("div");
    overlay.className = "detail-overlay";
    overlay.innerHTML =
      '<div class="detail-backdrop"></div>' +
      '<div class="detail-sheet">' +
        '<div class="detail-handle"></div>' +
        '<div class="detail-header">' +
          '<span class="detail-header-sku">' + sku + '</span>' +
          '<button class="detail-close-btn" data-en="' + TEXTS.en.close + '" data-zh="' + TEXTS.zh.close + '" data-ms="' + TEXTS.ms.close + '">' + t('close') + '</button>' +
        '</div>' +
        '<div class="detail-scroll">' +
          mediaHTML +
          '<div class="detail-body">' +
            '<div class="detail-name" data-en="' + gridItem.dataset.name + '" data-zh="' + (gridItem.dataset.nameZh || gridItem.dataset.name) + '" data-ms="' + (gridItem.dataset.nameMs || gridItem.dataset.name) + '">' + name + '</div>' +
            '<div class="detail-price">' + priceHTML + '</div>' +
            qtyHTML +
            '<div class="detail-specs">' + specsHTML + '</div>' +
            '<div class="detail-parts-btn">' + boxSvg + '<span data-en="' + TEXTS.en.partsBtn + '" data-zh="' + TEXTS.zh.partsBtn + '" data-ms="' + TEXTS.ms.partsBtn + '">' + t('partsBtn') + '</span></div>' +
            '<a class="detail-wa-link" href="https://wa.me/' + waNum + '?text=Hi%2C%20I%27d%20like%20to%20ask%20about%20' + sku + '%20' + encodeURIComponent(gridItem.dataset.name) + '">' + '<span data-en="' + TEXTS.en.askWA + '" data-zh="' + TEXTS.zh.askWA + '" data-ms="' + TEXTS.ms.askWA + '">' + t('askWA') + '</span></a>' +
          '</div>' +
        '</div>' +
        '<div class="maint-page"></div>' +
      '</div>';

    document.body.appendChild(overlay);
    document.body.classList.add('overlay-open');

    overlay.querySelector(".detail-close-btn").addEventListener("click", function(e) { e.stopPropagation(); closeDetail(); });
    overlay.querySelector(".detail-backdrop").addEventListener("click", closeDetail);

    /* ---- Parts button → flip to maintenance page ---- */
    var partsBtn = overlay.querySelector(".detail-parts-btn");
    if (partsBtn) {
      partsBtn.addEventListener("click", function() {
        var maint = getMaintData(currentGridItem);
        if (!maint) {
          /* no data — show simple message */
          alert(getLang() === 'zh' ? '该产品暂无备件数据' : getLang() === 'ms' ? 'Tiada data alat ganti untuk produk ini' : 'No spare parts data for this product');
          return;
        }
        var maintPage = overlay.querySelector('.maint-page');
        maintPage.innerHTML = buildMaintPage(maint, sku);
        /* hide main page elements */
        overlay.querySelector('.detail-scroll').classList.add('hidden');
        overlay.querySelector('.detail-header').classList.add('hidden');
        overlay.querySelector('.detail-handle').classList.add('hidden');
        /* show maint page */
        maintPage.classList.add('active');
        /* back button */
        var backBtn = maintPage.querySelector('.maint-back-btn');
        if (backBtn) {
          backBtn.addEventListener('click', function() {
            maintPage.classList.remove('active');
            maintPage.innerHTML = '';
            overlay.querySelector('.detail-scroll').classList.remove('hidden');
            overlay.querySelector('.detail-header').classList.remove('hidden');
            overlay.querySelector('.detail-handle').classList.remove('hidden');
          });
        }
      });
    }

    var handle = overlay.querySelector('.detail-handle');
    handle.addEventListener('touchstart', function(e) { touchStartY = e.touches[0].clientY; }, { passive: true });
    handle.addEventListener('touchmove', function(e) { if (e.touches[0].clientY - touchStartY > 80) closeDetail(); }, { passive: true });

    requestAnimationFrame(function() { requestAnimationFrame(function() { overlay.classList.add('active'); }); });
    currentSku = sku;
    currentSelectedItem = gridItem;
    gridItem.classList.add("selected");
  }

  function closeDetail() {
    if (!overlay) return;
    var ol = overlay;
    var video = ol.querySelector("video");
    if (video) { video.pause(); video.currentTime = 0; }
    ol.classList.remove('active');
    document.body.classList.remove('overlay-open');
    var sheet = ol.querySelector('.detail-sheet');
    sheet.addEventListener('transitionend', function handler(e) {
      if (e.propertyName === 'transform') { ol.remove(); sheet.removeEventListener('transitionend', handler); }
    });
    setTimeout(function() { if (ol.parentNode) ol.remove(); }, 350);
    if (currentSelectedItem) { currentSelectedItem.classList.remove("selected"); currentSelectedItem = null; }
    overlay = null; currentSku = null; currentGridItem = null;
  }

  function removeOverlayImmediate() {
    if (!overlay) return;
    var video = overlay.querySelector("video");
    if (video) { video.pause(); video.currentTime = 0; }
    overlay.remove();
    document.body.classList.remove('overlay-open');
    overlay = null; currentSku = null; currentGridItem = null;
    if (currentSelectedItem) { currentSelectedItem.classList.remove("selected"); currentSelectedItem = null; }
  }
})();
