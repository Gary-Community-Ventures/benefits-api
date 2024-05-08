(() => {
    "use strict";
    const prefersDarkMode = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    const defaultTheme = prefersDarkMode ? "dark" : "light";
    const preferredTheme = localStorage.getItem("theme");
    const toggleDarkMode = document.querySelector("#bd-theme");
  
    if (!preferredTheme) {
      localStorage.setItem("theme", defaultTheme);
    }
  
    document.documentElement.setAttribute(
      "data-theme",
      preferredTheme || defaultTheme
    );
  
    toggleDarkMode.checked = preferredTheme === "dark" ? true : false;
  
    toggleDarkMode.addEventListener("change", function () {
      const isDarkTheme = localStorage.getItem("theme") === "dark";
      const newTheme = isDarkTheme ? "light" : "dark";
      localStorage.setItem("theme", newTheme);
      document.documentElement.setAttribute("data-theme", newTheme);
    });
  })();