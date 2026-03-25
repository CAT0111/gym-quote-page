(function() {
  var currentDetail = null;
  var currentSelectedItem = null;

  document.querySelectorAll(".grid-item").forEach(function(item) {
    item.addEventListener("click", function() { openDetail(item); });
  });

  function getColCount() {
    return window.innerWidth >= 768 ? 3 : 2;
  }

  function openDetail(gridItem) {
    var sku = gridItem.dataset.sku;
    if (currentDetail && currentDetail.dataset.forSku === sku) {
      closeDetail();
      return;
    }
    closeDetailImmediate();

    var specs = JSON.parse(gridItem.dataset.specs);
    var specsHTML = "";
    for (var k in specs) {
      if (specs.hasOwnProperty(k)) {
        specsHTML += '<div class="detail-spec-row"><span class="detail-spec-label">' + k + '</span><span class="detail-spec-value">' + specs[k] + '</span></div>';
      }
    }

    var videoUrl = gridItem.dataset.video || "";
    var videoHTML;
    if (videoUrl) {
      videoHTML = '<div class="detail-video-btn" data-action="toggle-video"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>Watch 60s Test Video</div><div class="detail-video-wrap"><video controls preload="none" playsinline><source src="' + videoUrl + '" type="video/mp4"></video></div>';
    } else {
      videoHTML = '<div class="detail-video-btn" style="opacity:.3;pointer-events:none"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>Video coming soon</div>';
    }

    var waNum = document.body.dataset.whatsapp || "8613800000000";
    var panel = document.createElement("div");
    panel.className = "detail-panel";
    panel.dataset.forSku = sku;
    panel.innerHTML = '<div class="detail-close"><span class="detail-close-sku">' + sku + '</span><button class="detail-close-btn">Close ✕</button></div>' +
      '<div class="detail-image"><img src="' + gridItem.dataset.img + '" alt="' + gridItem.dataset.name + '"></div>' +
      '<div class="detail-body">' +
      '<div class="detail-name">' + gridItem.dataset.name + '</div>' +
      '<div class="detail-price">' + gridItem.dataset.price + ' <span style="font-size:14px;color:rgba(255,255,255,.35);font-weight:400">FOB</span></div>' +
      '<div class="detail-specs">' + specsHTML + '</div>' +
      videoHTML +
      '<a class="detail-wa-link" href="https://wa.me/' + waNum + '?text=Hi%2C%20I%27d%20like%20to%20ask%20about%20' + sku + '%20' + encodeURIComponent(gridItem.dataset.name) + '">' +
      '<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/></svg>' +
      'Ask about this machine on WhatsApp</a></div>';

    panel.querySelector(".detail-close-btn").addEventListener("click", function(e) {
      e.stopPropagation();
      closeDetail();
    });

    var vbtn = panel.querySelector("[data-action=toggle-video]");
    if (vbtn) {
      vbtn.addEventListener("click", function() {
        var wrap = this.nextElementSibling;
        var video = wrap.querySelector("video");
        if (wrap.classList.contains("active")) {
          wrap.classList.remove("active");
          video.pause();
        } else {
          wrap.classList.add("active");
          video.play().catch(function(){});
          var p = wrap.closest(".detail-panel");
          if (p) { p.style.maxHeight = "none"; p.style.overflow = "visible"; }
        }
      });
    }

    var grid = gridItem.closest(".product-grid");
    var allItems = Array.from(grid.querySelectorAll(".grid-item"));
    var idx = allItems.indexOf(gridItem);
    var cols = getColCount();
    var rowEndIdx = Math.min(idx - (idx % cols) + cols - 1, allItems.length - 1);
    allItems[rowEndIdx].after(panel);

    panel.style.maxHeight = "0";
    panel.style.opacity = "0";
    panel.style.overflow = "hidden";

    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        panel.style.transition = "max-height .3s ease-out, opacity .25s ease-out";
        panel.style.maxHeight = panel.scrollHeight + "px";
        panel.style.opacity = "1";
      });
    });

    panel.addEventListener("transitionend", function handler(e) {
      if (e.propertyName === "max-height" && panel.style.opacity === "1") {
        panel.style.maxHeight = "none";
        panel.style.overflow = "visible";
        panel.removeEventListener("transitionend", handler);
      }
    });

    currentDetail = panel;
    currentSelectedItem = gridItem;
    gridItem.classList.add("selected");

    setTimeout(function() {
      panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 80);
  }

  function closeDetailImmediate() {
    if (currentDetail) {
      var video = currentDetail.querySelector("video");
      if (video) { video.pause(); video.currentTime = 0; }
      currentDetail.remove();
      currentDetail = null;
    }
    if (currentSelectedItem) {
      currentSelectedItem.classList.remove("selected");
      currentSelectedItem = null;
    }
  }

  function closeDetail() {
    if (!currentDetail) return;
    var panel = currentDetail;
    var video = panel.querySelector("video");
    if (video) { video.pause(); video.currentTime = 0; }

    panel.style.overflow = "hidden";
    panel.style.maxHeight = panel.scrollHeight + "px";
    requestAnimationFrame(function() {
      panel.style.transition = "max-height .25s ease-in, opacity .2s ease-in";
      panel.style.maxHeight = "0";
      panel.style.opacity = "0";
    });

    panel.addEventListener("transitionend", function handler(e) {
      if (e.propertyName === "max-height") {
        panel.remove();
        panel.removeEventListener("transitionend", handler);
      }
    });

    if (currentSelectedItem) {
      currentSelectedItem.classList.remove("selected");
      currentSelectedItem = null;
    }
    currentDetail = null;
  }
})();