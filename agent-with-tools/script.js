// script.js - Simple Whack-a-Mole implementation

// Game configuration
const GAME_DURATION = 30000; // 30 seconds
const MOLE_INTERVAL = 800; // time between mole appearances (ms)

// State variables
let score = 0;
let gameActive = true;
let moleTimer = null;
let gameTimer = null;

// DOM elements
const grid = document.getElementById("grid");
const scoreEl = document.getElementById("score");

// Helper to update score display
function updateScore() {
  scoreEl.textContent = `Score: ${score}`;
}

// Create 9 holes with a mole inside each
function createGrid() {
  for (let i = 0; i < 9; i++) {
    const hole = document.createElement("div");
    hole.className = "hole";

    const mole = document.createElement("div");
    mole.className = "mole";
    hole.appendChild(mole);

    // Click handling for whacking
    hole.addEventListener("click", () => {
      if (!gameActive) return;
      if (hole.classList.contains("active")) {
        // Successful whack
        score++;
        updateScore();
        hole.classList.remove("active");
        hole.classList.add("hit");
        // Remove hit animation class after it finishes
        setTimeout(() => hole.classList.remove("hit"), 300);
      }
    });

    grid.appendChild(hole);
  }
}

// Randomly show a mole in one of the holes
function showMole() {
  if (!gameActive) return;
  const holes = document.querySelectorAll(".hole");
  const randomIndex = Math.floor(Math.random() * holes.length);
  const chosenHole = holes[randomIndex];
  // Show mole
  chosenHole.classList.add("active");
  // Hide mole after a short delay if not whacked
  setTimeout(() => {
    chosenHole.classList.remove("active");
  }, MOLE_INTERVAL - 200); // mole stays visible slightly less than the interval
}

// Start the recurring mole appearances
function startMoleLoop() {
  moleTimer = setInterval(showMole, MOLE_INTERVAL);
}

// End the game – stop timers and disable further whacking
function endGame() {
  gameActive = false;
  clearInterval(moleTimer);
  clearTimeout(gameTimer);
  // Remove any visible mole
  document.querySelectorAll(".hole.active").forEach((h) => h.classList.remove("active"));
  alert(`Game over! Your final score is ${score}`);
}

// Initialise the game
function init() {
  createGrid();
  updateScore();
  startMoleLoop();
  // Set overall game timer
  gameTimer = setTimeout(endGame, GAME_DURATION);
}

// Run when the DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
