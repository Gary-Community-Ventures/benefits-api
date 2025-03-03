// For handing the sorting of tables
function initializeTableSorting() {
  let table = document.querySelector(".table");
  let headers = table.querySelectorAll("th");
  let currentSortColumn = null;
  let sortDirection = "asc";

  headers.forEach(function (header, index) {
    header.addEventListener("click", function () {
      sortTable(index);
    });
  });

  function sortTable(columnIndex) {
    let rows = Array.from(table.querySelectorAll("tbody tr"));
    if (columnIndex === currentSortColumn) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      currentSortColumn = columnIndex;
      sortDirection = "asc";
    }

    rows.sort(function (a, b) {
      let cellA = a.querySelectorAll("td")[columnIndex].textContent.trim();
      let cellB = b.querySelectorAll("td")[columnIndex].textContent.trim();

      let valueA = isNaN(cellA) ? cellA.toLowerCase() : parseInt(cellA, 10);
      let valueB = isNaN(cellB) ? cellB.toLowerCase() : parseInt(cellB, 10);

      if (valueA < valueB) return sortDirection === "asc" ? -1 : 1;
      if (valueA > valueB) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });

    let tbody = table.querySelector("tbody");
    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
  }
}

// For handling the sidebar menu
function initializeSidebarMenu() {
  let menuItems = document.querySelectorAll(".menu-list .sidebar-item");
  let currentUrl = window.location.href;

  menuItems.forEach(function (menuItem) {
    let linkUrl = menuItem.href;

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
  let dropdowns = document.querySelectorAll("#" + tableId + " .dropdown");
  dropdowns.forEach(function (dropdown, index) {
    let dropdownButton = dropdown.querySelector(".button");
    let dropdownSpan = dropdown.querySelector(".material-symbols-outlined");
    let dropdownContent = dropdown.querySelector(".dropdown-content");

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
      let isClickInside = dropdown.contains(event.target);
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
  let dropdownRect = dropdown.getBoundingClientRect();
  let dropdownContentRect = dropdownContent.getBoundingClientRect();
  let viewportHeight = window.innerHeight;

  if (dropdownRect.bottom + dropdownContentRect.height > viewportHeight) {
    dropdown.classList.remove("is-top");
  } else {
    dropdown.classList.add("is-top");
  }
}

function exportButton() {
  let exportBtn = document.querySelector(".export-btn");

  exportBtn.addEventListener("click", async function (event) {
    event.preventDefault();

    if (!confirm("This process may take a few seconds. Do you want to continue?")) {
      return;
    }

    try {
      let response = await fetch("/api/translations/admin?export=true");

      if (!response.ok) {
        throw new Error("Failed to generate/download the file");
      }

      let blob = await response.blob();
      let link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "models-data.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      alert("Error: " + error.message);
    }
  });
}

function initializeAll() {
  initializeTableSorting();
  initializeSidebarMenu();
  initializeDropdowns();
}

document.addEventListener("DOMContentLoaded", initializeAll);
document.body.addEventListener("htmx:afterSwap", initializeAll);
exportButton();