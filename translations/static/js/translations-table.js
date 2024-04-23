// For handling the dropdowns in the translation table
function initializeDropdowns() {
  var dropdowns = document.querySelectorAll("#translation-table .dropdown");

  dropdowns.forEach(function (dropdown, index) {
    var dropdownButton = dropdown.querySelector(".button");
    var dropdownSpan = dropdown.querySelector(".material-symbols-outlined");

    dropdownButton.addEventListener("click", function (event) {
      event.preventDefault();
      dropdown.classList.toggle("is-active");

      if (dropdown.classList.contains("is-active")) {
        dropdownSpan.textContent = "expand_less";
      } else {
        dropdownSpan.textContent = "expand_more";
      }
    });

    // Close the dropdown if the user clicks outside of it
    document.addEventListener("click", function (event) {
      var isClickInside = dropdown.contains(event.target);

      if (!isClickInside) {
        dropdown.classList.remove("is-active");
        dropdownSpan.textContent = "expand_more";
      }
    });

    // Close dropdowns when the page is scrolled
    window.addEventListener("scroll", function () {
      dropdown.classList.remove("is-active");
      dropdownSpan.textContent = "expand_more";
    });
  });
}

document.addEventListener("DOMContentLoaded", initializeDropdowns);
document.body.addEventListener("htmx:afterSwap", initializeDropdowns);
