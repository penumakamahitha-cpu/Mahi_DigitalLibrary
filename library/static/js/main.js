/**
 * Digital Library & E-Book Circulation Portal - Main JavaScript
 * Implements: Instant Catalog Search, Interactive Due Date & Fine Calculations
 */

document.addEventListener('DOMContentLoaded', function () {
  initCatalogInstantSearch();
  initDueDateCalculator();
  initReturnFineCalculator();
  initAutoDismissAlerts();
});

/**
 * 1. Instant Book Catalog Search and Genre Filter (Client-Side)
 */
function initCatalogInstantSearch() {
  const searchInput = document.getElementById('instantCatalogSearch');
  const bookCards = document.querySelectorAll('.catalog-book-item');
  const countDisplay = document.getElementById('visibleBookCount');
  const noResultsAlert = document.getElementById('noSearchResultsAlert');
  const clearBtn = document.getElementById('clearSearchBtn');
  const genrePills = document.querySelectorAll('.js-genre-filter');

  let activeGenre = 'all';

  if (!searchInput && bookCards.length === 0) return;

  function filterBooks() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    let visibleCount = 0;

    bookCards.forEach(function (card) {
      const title = card.getAttribute('data-title') || '';
      const author = card.getAttribute('data-author') || '';
      const isbn = card.getAttribute('data-isbn') || '';
      const genre = card.getAttribute('data-genre') || '';

      const matchesQuery = !query ||
        title.includes(query) ||
        author.includes(query) ||
        isbn.includes(query) ||
        genre.includes(query);

      const matchesGenre = activeGenre === 'all' || genre === activeGenre;

      if (matchesQuery && matchesGenre) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (countDisplay) {
      countDisplay.textContent = visibleCount;
    }

    if (noResultsAlert) {
      noResultsAlert.classList.toggle('d-none', visibleCount > 0);
    }

    if (clearBtn && searchInput) {
      clearBtn.classList.toggle('d-none', !searchInput.value);
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterBooks);
  }

  if (clearBtn && searchInput) {
    clearBtn.addEventListener('click', function () {
      searchInput.value = '';
      filterBooks();
      searchInput.focus();
    });
  }

  // Client-side quick genre filtering pills
  genrePills.forEach(function (pill) {
    pill.addEventListener('click', function (e) {
      e.preventDefault();
      genrePills.forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      activeGenre = this.getAttribute('data-genre') || 'all';
      filterBooks();
    });
  });
}

/**
 * 2. Interactive Due Date Calculator
 * Handles date calculation when issuing a book or on calculator page
 */
function initDueDateCalculator() {
  const issueDateInput = document.getElementById('id_issue_date') || document.getElementById('calc_issue_date');
  const dueDateInput = document.getElementById('id_due_date') || document.getElementById('calc_due_date');
  const daysButtons = document.querySelectorAll('.js-add-days-btn');
  const previewText = document.getElementById('dueDatePreviewText');

  if (!issueDateInput) return;

  function setDueDateByOffset(days) {
    let issueVal = issueDateInput.value;
    let baseDate = issueVal ? new Date(issueVal + 'T00:00:00') : new Date();

    if (isNaN(baseDate.getTime())) baseDate = new Date();

    const resultDate = new Date(baseDate);
    resultDate.setDate(resultDate.getDate() + parseInt(days, 10));

    const yyyy = resultDate.getFullYear();
    const mm = String(resultDate.getMonth() + 1).padStart(2, '0');
    const dd = String(resultDate.getDate()).padStart(2, '0');
    const formatted = `${yyyy}-${mm}-${dd}`;

    if (dueDateInput) {
      dueDateInput.value = formatted;
    }

    if (previewText) {
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      previewText.textContent = `Due on: ${resultDate.toLocaleDateString(undefined, options)} (${days} day loan)`;
    }
  }

  // Quick loan duration buttons (+7, +14, +28, +30)
  daysButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      daysButtons.forEach(b => b.classList.remove('btn-primary', 'active'));
      this.classList.add('btn-primary', 'active');
      this.classList.remove('btn-outline-secondary');
      const days = this.getAttribute('data-days') || '14';
      setDueDateByOffset(days);
    });
  });

  // When issue date input changes, recalculate due date (default 14 days)
  issueDateInput.addEventListener('change', function () {
    const activeBtn = document.querySelector('.js-add-days-btn.active');
    const days = activeBtn ? activeBtn.getAttribute('data-days') : '14';
    setDueDateByOffset(days);
  });
}

/**
 * 3. Interactive Overdue Fine Calculator
 * Calculates overdue days and fine amount ($1.00 per day) dynamically
 */
function initReturnFineCalculator() {
  const dueDateInput = document.getElementById('return_due_date') || document.getElementById('calc_check_due_date');
  const returnDateInput = document.getElementById('id_return_date') || document.getElementById('calc_return_date');
  const fineAmountInput = document.getElementById('id_fine_amount') || document.getElementById('calc_fine_amount');
  const daysOverdueBadge = document.getElementById('liveDaysOverdue');
  const fineBadge = document.getElementById('liveFineCalculated');
  const statusAlert = document.getElementById('returnStatusAlert');
  const finePerDay = 1.00; // $1.00 per day overdue standard

  if (!dueDateInput || !returnDateInput) return;

  function calculateFine() {
    const dueVal = dueDateInput.value;
    const retVal = returnDateInput.value;

    if (!dueVal || !retVal) return;

    const dueDate = new Date(dueVal + 'T00:00:00');
    const retDate = new Date(retVal + 'T00:00:00');

    const diffTime = retDate - dueDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const overdueDays = Math.max(0, diffDays);
    const totalFine = (overdueDays * finePerDay).toFixed(2);

    if (fineAmountInput) {
      fineAmountInput.value = totalFine;
    }

    if (daysOverdueBadge) {
      daysOverdueBadge.textContent = overdueDays;
    }

    if (fineBadge) {
      fineBadge.textContent = '$' + totalFine;
    }

    if (statusAlert) {
      if (overdueDays > 0) {
        statusAlert.className = 'alert alert-danger d-flex align-items-center gap-2 mb-3';
        statusAlert.innerHTML = `<i class="bi bi-exclamation-triangle-fill fs-5"></i>
          <div><strong>Overdue Loan:</strong> Book is <strong>${overdueDays} day(s) overdue</strong>. Overdue fine calculated at $${finePerDay.toFixed(2)}/day is <strong>$${totalFine}</strong>.</div>`;
      } else {
        statusAlert.className = 'alert alert-success d-flex align-items-center gap-2 mb-3';
        statusAlert.innerHTML = `<i class="bi bi-check-circle-fill fs-5"></i>
          <div><strong>On Time Return:</strong> Book returned on or before due date. <strong>No fine assessed ($0.00)</strong>.</div>`;
      }
    }
  }

  returnDateInput.addEventListener('change', calculateFine);
  dueDateInput.addEventListener('change', calculateFine);

  // Run initial fine calculation on load
  calculateFine();
}

/**
 * 4. Auto dismiss alerts after 5 seconds
 */
function initAutoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });
}
