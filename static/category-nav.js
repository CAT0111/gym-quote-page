(function() {
  var tabs = document.querySelectorAll(".cat-tab");
  var sections = document.querySelectorAll("[id^=sec-]");

  tabs.forEach(function(tab) {
    tab.addEventListener("click", function() {
      tabs.forEach(function(t) { t.classList.remove("active"); });
      tab.classList.add("active");
      var target = document.getElementById(tab.dataset.target);
      if (target) {
        var y = target.getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo({ top: y, behavior: "smooth" });
      }
    });
  });

  window.addEventListener("scroll", function() {
    var current = "";
    sections.forEach(function(s) {
      if (window.pageYOffset >= s.offsetTop - 120) current = s.id;
    });
    tabs.forEach(function(t) {
      t.classList.toggle("active", t.dataset.target === current);
    });
  }, { passive: true });

  var hint = document.querySelector(".scroll-hint");
  if (hint) {
    hint.addEventListener("click", function() {
      var nav = document.querySelector(".cat-nav");
      if (nav) nav.scrollIntoView({ behavior: "smooth" });
    });
  }
})();