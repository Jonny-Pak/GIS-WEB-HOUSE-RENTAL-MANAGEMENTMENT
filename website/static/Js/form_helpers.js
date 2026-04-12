document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-confirm-submit]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const message = form.getAttribute('data-confirm-submit') || 'Xác nhận thao tác này?';
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  document.querySelectorAll('[data-auto-submit]').forEach((field) => {
    field.addEventListener('change', () => {
      const form = field.form;
      if (form) {
        form.submit();
      }
    });
  });
});