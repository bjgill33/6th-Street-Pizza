// Wait for the DOM to finish loading
document.addEventListener("DOMContentLoaded", () => {
  const modalElement = document.getElementById('locationModal');

  // Define reusable close button HTML
  const closeButtonHTML = `
    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="locationCloseBtn"></button>
  `;

  // Initialize the modal instance
  const modal = new bootstrap.Modal(modalElement, {
    backdrop: 'static',
    keyboard: false
  });

  // Check sessionStorage to determine if user has already selected a store
  const userLocation = sessionStorage.getItem("storeLocation");
  const modalHeader = modalElement.querySelector(".modal-header");

  // Only add close button if one doesn't already exist in the header
  if (userLocation && !modalHeader.querySelector("#locationCloseBtn")) {
    modalHeader.insertAdjacentHTML("beforeend", closeButtonHTML);
  }

  // Fetch store locations from backend
  fetch('/locations/')
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('store-buttons-container');
      container.innerHTML = ''; // Clear initial loading message

      data.locations.forEach(store => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline-primary m-2';
        btn.innerHTML = `
          <div><strong>Store ${store.store_number}</strong></div>
          <div>${store.address}, ${store.city}, ${store.state} ${store.zip}</div>
          <div>${store.phone}</div>
        `;
        btn.onclick = () => selectStore(`store${store.store_number}`, store);
        container.appendChild(btn);
      });
    })
    .catch(error => {
      console.error("Error loading locations:", error);
      document.getElementById('store-buttons-container').innerHTML = '<p>Error loading locations.</p>';
    });

  // Show the modal if no store is selected
  if (!userLocation) {
    modal.show();
  }
});

// Triggered when user selects a store
function selectStore(locationKey, storeData) {
  sessionStorage.setItem("storeLocation", locationKey);

  fetch('/set-location/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ location: locationKey })
  }).then(res => {
    if (res.ok) {
      const modalElement = document.getElementById('locationModal');
      const modal = bootstrap.Modal.getInstance(modalElement);
      modal.hide();

      // Dynamically update location display (if present)
      const displayContainer = document.getElementById('store-info-display');
      if (displayContainer) {
        displayContainer.innerHTML = `
          <div class="alert alert-info text-center" role="alert">
            <strong>Selected Location:</strong><br>
            Store ${storeData.store_number} – ${storeData.address}, ${storeData.city}, ${storeData.state} ${storeData.zip}<br>
            Phone: ${storeData.phone}<br>
            <button class="btn btn-sm btn-outline-secondary mt-2" onclick="showLocationModal()">Change Store Location</button>
          </div>
        `;
      } else {
        location.reload(); // Fallback reload
      }
    }
  });
}

// Helper to get CSRF token from cookie
function getCSRFToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

// Exposed function to manually trigger the modal
function showLocationModal() {
  const modal = new bootstrap.Modal(document.getElementById('locationModal'));
  modal.show();
}
