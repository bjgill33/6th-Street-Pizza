// Arthur Holmes
// 2/18/2025
// This script allows users to filter menu items based on their category.

function filterMenu(category) {
  const allCards = document.querySelectorAll(".pizza, .wings, .dessert, .drinks");

  allCards.forEach((card) => {
    if (category === "all") {
      card.style.display = "block";
    } else if (card.classList.contains(category)) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}
