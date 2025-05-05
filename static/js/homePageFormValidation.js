document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#deliveryModal form');
  const submitBtn = form.querySelector('button[type="submit"]');

  const errorFields = {
    fullName: 'Full Name',
    email: 'Email',
    address: 'Address',
    city: 'City',
    state: 'State',
    zip: 'Zip Code',
    phone: 'Phone',
    specialInstructions: 'Special Instructions'
  };

  const maxLengths = {
    fullName: 30,
    email: 70,
    address: 100,
    city: 30,
    zip: 5,
    phone: 20,
    specialInstructions: 100
  };

  function hasInvalidChars(value) {
    return /['"<>;`\\]/.test(value);
  }

  function showError(id, message) {
    const errorEl = document.getElementById(id + 'Error');
    if (errorEl) errorEl.innerText = message;
  }

  function clearErrors() {
    Object.keys(errorFields).forEach(id => showError(id, ''));
  }

  function validateFormFields() {
    clearErrors();
    let isValid = true;

    const values = {};
    for (let field in errorFields) {
      const input = form.elements[field];
      values[field] = input ? input.value.trim() : '';
    }

    for (let field in values) {
      const val = values[field];
      if (!val) {
        showError(field, `${errorFields[field]} is required.`);
        isValid = false;
      } else if (hasInvalidChars(val)) {
        showError(field, `Invalid characters in ${errorFields[field]}.`);
        isValid = false;
      } else if (field in maxLengths && val.length > maxLengths[field]) {
        showError(field, `${errorFields[field]} must be under ${maxLengths[field]} characters.`);
        isValid = false;
      }
    }

    if (values.zip && !/^\d{5}$/.test(values.zip)) {
      showError('zip', 'Zip Code must be exactly 5 digits.');
      isValid = false;
    }

    if (values.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
      showError('email', 'Invalid email format.');
      isValid = false;
    }

    submitBtn.disabled = !isValid;
    return isValid;
  }

  Object.keys(errorFields).forEach(field => {
    const el = form.elements[field];
    if (el) el.addEventListener('input', validateFormFields);
  });

  form.addEventListener('submit', function (e) {
    if (!validateFormFields()) {
      e.preventDefault(); // Block submission
    } else {
      submitBtn.disabled = true;
    }
  });

  validateFormFields();
});
