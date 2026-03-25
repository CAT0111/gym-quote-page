(function() {
  var overlay = null;
  var currentSku = null;
  var currentSelectedItem = null;
  var touchStartY = 0;

  var TEXTS = {
    en: { watchVideo:'Watch 60s Test Video', videoSoon:'Video coming soon', close:'Close ✕', askWA:'Ask about this machine on WhatsApp', fob:'FOB' },
    zh: { watchVideo:'观看60秒试机视频', videoSoon:'视频即将上线', close:'关闭 ✕', askWA:'通过 WhatsApp 咨询此器械', fob:'FOB' },
    ms: { watchVideo:'Tonton Video Ujian 60s', videoSoon:'Video akan datang', close:'Tutup ✕', askWA:'Tanya tentang mesin ini di WhatsApp', fob:'FOB' }
  };
  var SPEC_KEYS = {
    en: {},
    zh: { 'Weight Stack':'配重片','Dimensions':'尺寸','Net Weight':'净重','Target':'目标肌群','Feature':'特点','Type':'类型','Accessories':'配件','Bar Weight':'杠铃重量','Capacity':'容量','Angles':'角度调节','Motor':'电机','Speed':'速度','Belt':'跑带尺寸','Display':'显示屏','Resistance':'阻力','Stride':'步幅','Flywheel':'飞轮','Rail Length':'滑轨长度' },
    ms: { 'Weight Stack':'Tumpukan Berat','Dimensions':'Dimensi','Net Weight':'Berat Bersih','Target':'Sasaran','Feature':'Ciri','Type':'Jenis','Accessories':'Aksesori','Bar Weight':'Berat Bar','Capacity':'Kapasiti','Angles':'Sudut','Motor':'Motor','Speed':'Kelajuan','Belt':'Tali Pinggang','Display':'Paparan','Resistance':'Rintangan','Stride':'Langkah','Flywheel':'Roda Tenaga','Rail Length':'Panjang Rel' }
  };

  function getLang() { return (window.__QL_LANG && window.__QL_LANG.current()) || 'en'; }
  function t(key) { var l = getLang(); return (TEXTS[l] && TEXTS[l][key]) || TEXTS.en[key] || key; }
  function specKey(key) { var l = getLang(); return (SPEC_KEYS[l] && SPEC_KEYS[l][key]) || key; }
  function prodName(gi) {
    var l = getLang();
    if (l === 'zh' && gi.dataset.nameZh) return gi.dataset.nameZh;
    if (l === 'ms' && gi.dataset.nameMs) return gi.dataset.nameMs;
    return gi.dataset.name;
  }

  document.querySelectorAll(".grid-item").forEach(function(item) {
    item.addEventListener("click", function() { openDetail(item); });
  });

  function openDetail(gridItem) {
    var sku = gridItem.dataset.sku;
    if (currentSku === sku && overlay) { closeDetail(); return; }
    if (overlay) removeOverlayImmediate();
    if (currentSelectedItem) currentSelectedItem.classList.remove("selected");

    var specs = JSON.parse(gridItem.dataset.specs);
    var specsHTML = "";
    for (var k in specs) {
      if (specs.hasOwnProperty(k)) {
        specsHTML += '<div class="detail-spec-row"><span class="detail-spec-label">' + specKey(k) + '</span><span class="detail-spec-value">' + specs[k] + '</span></div>';
      }
    }

    var name = prodName(gridItem);
    var videoUrl = gridItem.dataset.video || "";
    var videoHTML;
    if (videoUrl) {
      videoHTML = '<div class="detail-video-btn" data-action="toggle-video"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><span data-en="'+TEXTS.en.watchVideo+'" data-zh="'+TEXTS.zh.watchVideo+'" data-ms="'+TEXTS.ms.watchVideo+'">'+t('watchVideo')+'</span></div><div class="detail-video-wrap"><video controls preload="none" playsinline><source src="'+videoUrl+'" type="video/mp4"></video></div>';
    } else {
      videoHTML = '<div class="detail-video-btn" style="opacity:.3;pointer-events:none"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><span data-en="'+TEXTS.en.videoSoon+'" data-zh="'+TEXTS.zh.videoSoon+'" data-ms="'+TEXTS.ms.videoSoon+'">'+t('videoSoon')+'</span></div>';
    }

    var waNum = document.body.dataset.whatsapp || "8613800000000";
    var waSvg = '<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/></svg>';

    overlay = document.createElement("div");
    overlay.className = "detail-overlay";
    overlay.innerHTML =
      '<div class="detail-backdrop"></div>' +
      '<div class="detail-sheet">' +
        '<div class="detail-handle"></div>' +
        '<div class="detail-header">' +
          '<span class="detail-header-sku">'+sku+'</span>' +
          '<button class="detail-close-btn" data-en="'+TEXTS.en.close+'" data-zh="'+TEXTS.zh.close+'" data-ms="'+TEXTS.ms.close+'">'+t('close')+'</button>' +
        '</div>' +
        '<div class="detail-scroll">' +
          '<div class="detail-image"><img src="'+gridItem.dataset.img+'" alt="'+name+'"></div>' +
          '<div class="detail-body">' +
            '<div class="detail-name" data-en="'+gridItem.dataset.name+'" data-zh="'+(gridItem.dataset.nameZh||gridItem.dataset.name)+'" data-ms="'+(gridItem.dataset.nameMs||gridItem.dataset.name)+'">'+name+'</div>' +
            '<div class="detail-price">'+gridItem.dataset.price+' <span style="font-size:14px;color:rgba(255,255,255,.35);font-weight:400">'+t('fob')+'</span></div>' +
            '<div class="detail-specs">'+specsHTML+'</div>' +
            videoHTML +
            '<a class="detail-wa-link" href="https://wa.me/'+waNum+'?text=Hi%2C%20I%27d%20like%20to%20ask%20about%20'+sku+'%20'+encodeURIComponent(gridItem.dataset.name)+'">'+waSvg+'<span data-en="'+TEXTS.en.askWA+'" data-zh="'+TEXTS.zh.askWA+'" data-ms="'+TEXTS.ms.askWA+'">'+t('askWA')+'</span></a>' +
          '</div>' +
        '</div>' +
      '</div>';

    document.body.appendChild(overlay);
    document.body.classList.add('overlay-open');

    overlay.querySelector(".detail-close-btn").addEventListener("click", function(e) { e.stopPropagation(); closeDetail(); });
    overlay.querySelector(".detail-backdrop").addEventListener("click", closeDetail);

    var vbtn = overlay.querySelector("[data-action=toggle-video]");
    if (vbtn) {
      vbtn.addEventListener("click", function() {
        var wrap = this.nextElementSibling;
        var video = wrap.querySelector("video");
        var scrollContainer = overlay.querySelector('.detail-scroll');
        if (wrap.classList.contains("active")) {
          wrap.classList.remove("active");
          video.pause();
        } else {
          wrap.classList.add("active");
          video.play().catch(function(){});
          setTimeout(function() {
            scrollContainer.scrollTo({ top: wrap.offsetTop - vbtn.offsetHeight - 8, behavior: 'smooth' });
          }, 50);
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
    overlay = null; currentSku = null;
  }

  function removeOverlayImmediate() {
    if (!overlay) return;
    var video = overlay.querySelector("video");
    if (video) { video.pause(); video.currentTime = 0; }
    overlay.remove();
    document.body.classList.remove('overlay-open');
    overlay = null; currentSku = null;
    if (currentSelectedItem) { currentSelectedItem.classList.remove("selected"); currentSelectedItem = null; }
  }
})();
