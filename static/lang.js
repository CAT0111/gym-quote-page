/* static/lang.js — 多语言切换 (en / zh / ms, 预留 fr / es) */
;(function () {
  'use strict';

  var SUPPORTED = ['en', 'zh', 'ms'];
  var DEFAULT   = 'en';
  var STORAGE_KEY = 'ql_lang';

  /* ---- 语言检测优先级: URL ?lang= > localStorage > navigator.language > en ---- */
  function detectLang() {
    try {
      var p = new URLSearchParams(window.location.search).get('lang');
      if (p && SUPPORTED.indexOf(p) !== -1) return p;
    } catch(e) {}
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED.indexOf(saved) !== -1) return saved;
    var nav = (navigator.language || navigator.userLanguage || '').toLowerCase();
    if (nav.indexOf('zh') === 0) return 'zh';
    if (nav.indexOf('ms') === 0 || nav.indexOf('my') === 0) return 'ms';
    return DEFAULT;
  }

  /* ---- 应用语言到所有带 data-en 的静态元素 ---- */
  function applyLang(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang === 'zh' ? 'zh-CN' : lang);
    localStorage.setItem(STORAGE_KEY, lang);

    var els = document.querySelectorAll('[data-en]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var text = el.getAttribute('data-' + lang) || el.getAttribute('data-en');
      if (text) el.textContent = text;
    }

    /* 更新切换器按钮高亮 */
    var btns = document.querySelectorAll('.lang-btn');
    for (var j = 0; j < btns.length; j++) {
      btns[j].classList.toggle('lang-active', btns[j].getAttribute('data-lang-val') === lang);
    }

    /* 更新已展开的 detail panel（如果有的话） */
    updateOpenPanel(lang);
  }

  /* ---- 更新已展开的 detail-panel 里的框架文案 ---- */
  function updateOpenPanel(lang) {
    var panel = document.querySelector('.detail-panel');
    if (!panel) return;
    var els = panel.querySelectorAll('[data-en]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var text = el.getAttribute('data-' + lang) || el.getAttribute('data-en');
      if (text) el.textContent = text;
    }
  }

  /* ---- 渲染切换器按钮 ---- */
  function renderSwitcher() {
    var container = document.querySelector('.lang-switcher');
    if (!container) return;
    var labels = { en: 'EN', zh: '中', ms: 'MS' };
    SUPPORTED.forEach(function (code) {
      var btn = document.createElement('button');
      btn.className = 'lang-btn';
      btn.setAttribute('data-lang-val', code);
      btn.textContent = labels[code];
      btn.addEventListener('click', function () { applyLang(code); });
      container.appendChild(btn);
    });
  }

  /* ---- 暴露给 detail-panel.js 读取当前语言 ---- */
  window.__QL_LANG = {
    current: function () {
      return document.documentElement.getAttribute('data-lang') || DEFAULT;
    }
  };

  /* ---- 初始化 ---- */
  function init() {
    renderSwitcher();
    applyLang(detectLang());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
