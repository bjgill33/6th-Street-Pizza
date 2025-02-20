// Arthur Holmes
// 2/18/2025
// This file creates a Bootstrap modal for selecting a location
// Wait for the DOM to fully load before executing the script
document.addEventListener("DOMContentLoaded", function () {
  /**
   * Creates and inserts the location selection modal dynamically.
   * - Contains three locations with embedded Google Maps placeholders.
   * - Allows users to select a location.
   * - Uses Bootstrap modal for functionality.
   */

  const locationModalHTML = `
        <div class="modal fade" id="locationModal" tabindex="-1" aria-labelledby="locationModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="locationModalLabel">Select a Location</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <!-- Location 1 -->
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <div id="map1" style="height: 300px;"></div>
                                        <h5 class="card-title">Location 1</h5>
                                        <p>123 Main St, Raleigh, NC 27601</p>
                                        <p>Phone: (919) 555-1234</p>
                                        <button class="btn btn-primary pick-location" data-location="1">Pick this location</button>
                                    </div>
                                </div>
                            </div>
                            <!-- Location 2 -->
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <div id="map2" style="height: 300px;"></div>
                                        <h5 class="card-title">Location 2</h5>
                                        <p>456 Oak St, Raleigh, NC 27602</p>
                                        <p>Phone: (919) 555-5678</p>
                                        <button class="btn btn-primary pick-location" data-location="2">Pick this location</button>
                                    </div>
                                </div>
                            </div>
                            <!-- Location 3 -->
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <div id="map3" style="height: 300px;"></div>
                                        <h5 class="card-title">Location 3</h5>
                                        <p>789 Pine St, Raleigh, NC 27603</p>
                                        <p>Phone: (919) 555-8765</p>
                                        <button class="btn btn-primary pick-location" data-location="3">Pick this location</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

  // Append modal HTML to the document body
  document.body.insertAdjacentHTML("beforeend", locationModalHTML);

  /**
   * Handles the selection of a location.
   * - Logs the selected location (extend this logic for real use cases).
   */
  document.querySelectorAll(".pick-location").forEach((button) => {
    button.addEventListener("click", function () {
      let selectedLocation = this.getAttribute("data-location");
      console.log(`Location ${selectedLocation} selected!`);
      // Expand here (work for next sprint): Implement logic to save or process the selected location
    });
  });
});
