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

document.addEventListener("DOMContentLoaded", function () {
  initializeTableSorting();
  initializeSidebarMenu();
});
