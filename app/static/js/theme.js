// Doğruluk — gestion des thèmes (turquoise par défaut, sombre, noir, custom)
// Persistance localStorage + cookie `theme` (pour rendu serveur si besoin).
(function () {
  "use strict";
  var KEY = "dogruluk_theme";
  var C1 = "dogruluk_custom_c1";
  var C2 = "dogruluk_custom_c2";

  function applyCustomColors() {
    var root = document.documentElement;
    root.style.setProperty("--c1", localStorage.getItem(C1) || "#0d9488");
    root.style.setProperty("--c2", localStorage.getItem(C2) || "#0b3b36");
  }

  function setTheme(name) {
    document.documentElement.setAttribute("data-theme", name);
    try { localStorage.setItem(KEY, name); } catch (e) {}
    document.cookie = "theme=" + name + "; max-age=31536000; path=/; samesite=lax";
    document.querySelectorAll(".theme-switcher button[data-theme]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.theme === name ? "true" : "false");
    });
    var panel = document.getElementById("custom-theme-panel");
    if (panel) panel.style.display = (name === "custom") ? "" : "none";
  }

  window.dogrulukSetTheme = setTheme;

  document.addEventListener("DOMContentLoaded", function () {
    applyCustomColors();
    var saved = "turquoise";
    try { saved = localStorage.getItem(KEY) || "turquoise"; } catch (e) {}
    setTheme(saved);

    document.querySelectorAll(".theme-switcher button[data-theme]").forEach(function (b) {
      b.addEventListener("click", function () { setTheme(b.dataset.theme); });
    });

    ["--c1", "--c2"].forEach(function (varName, i) {
      var input = document.getElementById(i === 0 ? "custom-c1" : "custom-c2");
      if (!input) return;
      input.value = localStorage.getItem(i === 0 ? C1 : C2) || (i === 0 ? "#0d9488" : "#0b3b36");
      input.addEventListener("input", function () {
        localStorage.setItem(i === 0 ? C1 : C2, input.value);
        document.documentElement.style.setProperty(varName, input.value);
        setTheme("custom");
      });
    });
  });
})();
