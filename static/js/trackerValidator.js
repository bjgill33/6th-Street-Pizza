document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form[action*="track_order"]');
  const input = form.querySelector('input[name="tracking_id"]');
  const button = form.querySelector('button[type="submit"]');

  const pattern = /^PIZZA-[A-F0-9]{8}-[A-F0-9]{8}-\d$/;

  function validate() {
    const value = input.value.trim().toUpperCase();
    if (pattern.test(value)) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
      button.disabled = false;
    } else {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      button.disabled = true;
    }
  }

  input.addEventListener('input', validate);
  form.addEventListener('submit', function (e) {
    if (button.disabled) e.preventDefault();
  });

  // Initial state
  button.disabled = true;
});
