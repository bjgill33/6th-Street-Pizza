// Arthur Holmes
// 2/18/2025
// This file esablishes the pick up locations
// for carry out customers

// Function to initialize Google Maps
function initMaps() {
  // Define locations (latitude & longitude)
  const locations = [
    { lat: 35.7796, lng: -78.6382 }, // Location 1
    { lat: 35.7738, lng: -78.6385 }, // Location 2
    { lat: 35.7611, lng: -78.6389 }, // Location 3
  ];

  // Initialize maps for each location
  const maps = ["map1", "map2", "map3"]; // IDs of map containers

  maps.forEach((mapId, index) => {
    const map = new google.maps.Map(document.getElementById(mapId), {
      zoom: 14,
      center: locations[index],
    });

    new google.maps.Marker({
      position: locations[index],
      map: map,
      title: `Location ${index + 1}`,
    });
  });
}
