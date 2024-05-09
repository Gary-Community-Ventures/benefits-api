// For handing the sorting of tables
function initializeTableSorting() {
  var table = document.querySelector(".table");
  var headers = table.querySelectorAll("th");
  var currentSortColumn = null;
  var sortDirection = "asc";

  headers.forEach(function (header, index) {
    header.addEventListener("click", function () {
      sortTable(index);
    });
  });

  function sortTable(columnIndex) {
    var rows = Array.from(table.querySelectorAll("tbody tr"));
    if (columnIndex === currentSortColumn) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      currentSortColumn = columnIndex;
      sortDirection = "asc";
    }

    rows.sort(function (a, b) {
      var cellA = a.querySelectorAll("td")[columnIndex].textContent.trim();
      var cellB = b.querySelectorAll("td")[columnIndex].textContent.trim();

      var valueA = isNaN(cellA) ? cellA.toLowerCase() : parseInt(cellA, 10);
      var valueB = isNaN(cellB) ? cellB.toLowerCase() : parseInt(cellB, 10);

      if (valueA < valueB) return sortDirection === "asc" ? -1 : 1;
      if (valueA > valueB) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });

    var tbody = table.querySelector("tbody");
    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
  }
}

// For handling the sidebar menu
function initializeSidebarMenu() {
  var menuItems = document.querySelectorAll(".menu-list .sidebar-item");
  var currentUrl = window.location.href;

  menuItems.forEach(function (menuItem) {
    var linkUrl = menuItem.href;

    if (linkUrl === currentUrl) {
      menuItem.classList.add("is-active");
    }

    menuItem.addEventListener("click", function (event) {
      menuItems.forEach(function (item) {
        item.classList.remove("is-active");
      });

      event.currentTarget.classList.add("is-active");
    });
  });
}

// For handling the dropdown menu in the tables
function initializeDropdowns() {
  var dropdowns = document.querySelectorAll("#" + tableId + " .dropdown");
  dropdowns.forEach(function (dropdown, index) {
    var dropdownButton = dropdown.querySelector(".button");
    var dropdownSpan = dropdown.querySelector(".material-symbols-outlined");
    var dropdownContent = dropdown.querySelector(".dropdown-content");

    dropdownButton.addEventListener("click", function (event) {
      event.preventDefault();
      dropdown.classList.toggle("is-active");
      if (dropdown.classList.contains("is-active")) {
        dropdownSpan.textContent = "expand_less";
        checkDropdownPosition(dropdown, dropdownContent);
      } else {
        dropdownSpan.textContent = "expand_more";
        dropdown.classList.remove("is-top");
      }
    });

    // Close the dropdown if the user clicks outside of it
    document.addEventListener("click", function (event) {
      var isClickInside = dropdown.contains(event.target);
      if (!isClickInside) {
        dropdown.classList.remove("is-active");
        dropdown.classList.remove("is-top");
        dropdownSpan.textContent = "expand_more";
      }
    });

    // Close dropdowns when the page is scrolled
    window.addEventListener("scroll", function () {
      dropdown.classList.remove("is-active");
      dropdown.classList.remove("is-top");
      dropdownSpan.textContent = "expand_more";
    });
  });
}

function checkDropdownPosition(dropdown, dropdownContent) {
  var dropdownRect = dropdown.getBoundingClientRect();
  var dropdownContentRect = dropdownContent.getBoundingClientRect();
  var viewportHeight = window.innerHeight;

  if (dropdownRect.bottom + dropdownContentRect.height > viewportHeight) {
    dropdown.classList.remove("is-top");
  } else {
    dropdown.classList.add("is-top");
  }
}

function initializeAll() {
  initializeTableSorting();
  initializeSidebarMenu();
  initializeDropdowns();
}

document.addEventListener("DOMContentLoaded", initializeAll);
document.body.addEventListener("htmx:afterSwap", initializeAll);
