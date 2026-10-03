/**
 * Z-Code — Dedicated Interactive Quiz Logic
 */

const questions = [
  {
    id: 1,
    text: "1. Which language are you learning in this course?",
    options: ["Python", "Java", "C++", "HTML"],
    optionLetters: ["a", "b", "c", "d"],
  },
  {
    id: 2,
    text: "2. Which symbol is used to create a comment in Python?",
    options: ["#", "//", "/*", "--"],
    optionLetters: ["a", "b", "c", "d"],
  },
  {
    id: 3,
    text: "3. Which function displays output in Python?",
    options: ["print()", "display()", "show()", "output()"],
    optionLetters: ["a", "b", "c", "d"],
  },
  {
    id: 4,
    text: "4. Which one is a valid Python variable name?",
    options: ["name", "2name", "my-name", "class"],
    optionLetters: ["a", "b", "c", "d"],
  },
  {
    id: 5,
    text: "5. What type of value is \"Hello\"?",
    options: ["String", "Integer", "Boolean", "Float"],
    optionLetters: ["a", "b", "c", "d"],
  }
];

let currentIndex = 0;
const userAnswers = [null, null, null, null, null]; // Stores "a" | "b" | "c" | "d"

// DOM Elements
const questionView = document.getElementById("questionView");
const resultView = document.getElementById("resultView");
const questionStepper = document.getElementById("questionStepper");
const questionText = document.getElementById("questionText");
const optionsGrid = document.getElementById("optionsGrid");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const progressFill = document.getElementById("progressFill");
const questionDots = document.querySelectorAll(".q-dot");

function renderQuestion(index) {
  const q = questions[index];
  currentIndex = index;

  // Update Stepper & Dots
  questionStepper.innerHTML = `Question ${index + 1} <span>of ${questions.length}</span>`;
  questionDots.forEach((dot, idx) => {
    dot.className = "q-dot";
    if (idx === index) dot.classList.add("active");
    if (userAnswers[idx] !== null) dot.classList.add("answered");
  });

  // Update Progress bar
  const progressPercent = ((index + 1) / questions.length) * 100;
  progressFill.style.width = `${progressPercent}%`;

  // Question Prompt
  questionText.textContent = q.text;

  // Render Options
  optionsGrid.innerHTML = "";
  q.options.forEach((optText, optIdx) => {
    const letter = q.optionLetters[optIdx];
    const isSelected = userAnswers[index] === letter;

    const optCard = document.createElement("div");
    optCard.className = `option-item ${isSelected ? "selected" : ""}`;
    optCard.innerHTML = `
      <div class="option-badge">${letter.toUpperCase()}</div>
      <div class="option-label">${optText}</div>
    `;

    optCard.addEventListener("click", () => selectOption(letter));
    optionsGrid.appendChild(optCard);
  });

  // Navigation Buttons State
  prevBtn.disabled = index === 0;

  if (index === questions.length - 1) {
    nextBtn.textContent = "Submit Quiz & Claim XP →";
    nextBtn.className = "nav-btn submit-btn";
  } else {
    nextBtn.textContent = "Next →";
    nextBtn.className = "nav-btn next-btn";
  }
}

function selectOption(letter) {
  userAnswers[currentIndex] = letter;
  renderQuestion(currentIndex);
}

prevBtn.addEventListener("click", () => {
  if (currentIndex > 0) {
    renderQuestion(currentIndex - 1);
  }
});

nextBtn.addEventListener("click", () => {
  if (currentIndex < questions.length - 1) {
    // If not answered yet, remind the user
    if (!userAnswers[currentIndex]) {
      alert("Please select an answer before continuing to the next question.");
      return;
    }
    renderQuestion(currentIndex + 1);
  } else {
    // Final submit
    if (userAnswers.includes(null)) {
      alert("Please answer all questions before submitting the quiz.");
      return;
    }
    handleSubmit();
  }
});

// Clickable stepper dots
questionDots.forEach((dot) => {
  dot.addEventListener("click", () => {
    const targetIdx = parseInt(dot.getAttribute("data-q"), 10);
    renderQuestion(targetIdx);
  });
});

// Keyboard shortcuts (1-4 or A-D to select, Arrow keys to navigate)
window.addEventListener("keydown", (e) => {
  if (resultView.style.display === "block") return;
  const key = e.key.toLowerCase();
  if (["a", "1"].includes(key)) selectOption("a");
  if (["b", "2"].includes(key)) selectOption("b");
  if (["c", "3"].includes(key)) selectOption("c");
  if (["d", "4"].includes(key)) selectOption("d");
  if (e.key === "ArrowRight" && currentIndex < questions.length - 1) {
    if (userAnswers[currentIndex]) renderQuestion(currentIndex + 1);
  }
  if (e.key === "ArrowLeft" && currentIndex > 0) {
    renderQuestion(currentIndex - 1);
  }
});

async function handleSubmit() {
  // Ensure user is logged in
  if (!window.ZCodeAuth || !ZCodeAuth.isLoggedIn()) {
    const loginNow = confirm(
      "You are not logged in yet!\n\nClick OK to automatically log in as Demo User (dhanush@zcode.dev) and submit your quiz, or Cancel to go to the login page."
    );
    if (loginNow) {
      try {
        await ZCodeAPI.login("dhanush@zcode.dev", "demo123");
      } catch (err) {
        alert("Could not reach backend. Please ensure ./start.sh is running!");
        return;
      }
    } else {
      window.location.href = "login.html";
      return;
    }
  }

  const payload = userAnswers.map((ans, idx) => ({
    question_id: questions[idx].id,
    answer: ans,
  }));

  nextBtn.disabled = true;
  nextBtn.textContent = "Grading Quiz...";

  try {
    const result = await ZCodeAPI.submitQuiz(1, payload);
    displayResults(result);
  } catch (err) {
    alert(`Error submitting quiz: ${err.message}`);
    nextBtn.disabled = false;
    nextBtn.textContent = "Submit Quiz & Claim XP →";
  }
}

function displayResults(result) {
  questionView.style.display = "none";
  resultView.style.display = "block";

  const scoreNum = document.getElementById("scoreNum");
  const scoreLabel = document.getElementById("scoreLabel");
  const resultHeading = document.getElementById("resultHeading");
  const resultMessage = document.getElementById("resultMessage");
  const resultIcon = document.getElementById("resultIcon");
  const resultActions = document.getElementById("resultActions");

  scoreNum.textContent = `${result.score}/${result.total}`;

  if (result.passed) {
    const userId = window.ZCodeAuth ? ZCodeAuth.getUserId() : null;
    if (userId) {
      localStorage.setItem(`zcode_quiz_1_passed_${userId}`, "true");
    }
    localStorage.removeItem("pythonIntroductionPassed");
    resultIcon.textContent = "🎉";
    resultHeading.textContent = "Quiz Passed! Outstanding Work!";
    scoreLabel.textContent = "PASSED";
    scoreLabel.style.color = "#4ade80";
    resultMessage.innerHTML = `
      ${result.message}<br>
      <strong style="color:#f7d994;font-size:18px;">+${result.xp_earned} XP Awarded to your profile!</strong>
    `;

    resultActions.innerHTML = `
      <a href="variables.html" class="primary-action-btn">
        Continue to Chapter 2: Variables →
      </a>
      <a href="python.html" class="secondary-action-btn">
        Return to Python Course Overview
      </a>
    `;
  } else {
    resultIcon.textContent = "💡";
    resultHeading.textContent = "Almost there! Keep practicing!";
    scoreLabel.textContent = "TRY AGAIN";
    scoreLabel.style.color = "#ef4444";
    resultMessage.innerHTML = `
      You scored ${result.score}/${result.total}. You need at least 4 correct answers to unlock Chapter 2.<br>
      Review the lesson and try again!
    `;

    resultActions.innerHTML = `
      <button class="primary-action-btn" onclick="retryQuiz()">
        ↺ Retry Quiz
      </button>
      <a href="python.html" class="secondary-action-btn">
        Review Chapter 1 Lessons
      </a>
    `;
  }
}

window.retryQuiz = function() {
  for (let i = 0; i < userAnswers.length; i++) userAnswers[i] = null;
  resultView.style.display = "none";
  questionView.style.display = "block";
  renderQuestion(0);
};

// Initial Render
renderQuestion(0);
