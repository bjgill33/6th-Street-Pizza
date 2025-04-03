 // 🔐 Inject CSRF token into a global variable so it can be reused in the modal HTML
window.csrfTokenHTML = `{% csrf_token %}`;

// 🍕 Inject toppings into a usable JavaScript array for dropdown rendering
window.toppingsHTML = `{% for topping in toppings %}
  <option value="{{ topping.name }}" data-price="{{ topping.price }}">{{ topping.name }} (${{ topping.price }})</option>
{% endfor %}`;
