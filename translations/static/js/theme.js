(() => {
  "use strict";
  const toggleDarkMode = document.querySelector("input[id=bd-theme]");
  toggleDarkMode.addEventListener("change", function () {
    if (this.checked) {
      document.documentElement.setAttribute("data-bs-theme", "dark");
    } else {
      document.documentElement.setAttribute("data-bs-theme", "light");
    }
  });
})();
