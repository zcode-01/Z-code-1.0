const fab = document.getElementById("aiFab");
const chat = document.getElementById("aiChat");
const closeAi = document.getElementById("closeAi");
const form = document.getElementById("aiForm");
const input = document.getElementById("aiInput");
const body = document.getElementById("aiBody");

fab.addEventListener("click", () => {
  chat.classList.add("open");
  chat.setAttribute("aria-hidden", "false");
  input.focus();
});

closeAi.addEventListener("click", () => {
  chat.classList.remove("open");
  chat.setAttribute("aria-hidden", "true");
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  const user = document.createElement("div");
  user.className = "user-message";
  user.textContent = text;
  body.appendChild(user);
  input.value = "";

  const ai = document.createElement("div");
  ai.className = "ai-message";
  ai.textContent = "Demo mode: I’ll connect this chat to Ollama + Qwen3 4B after the frontend is finalized. For learning questions, I’ll guide you with explanations and hints rather than simply giving the answer.";
  body.appendChild(ai);
  body.scrollTop = body.scrollHeight;
});

document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("light");
});
const pythonCourse = document.getElementById("pythonCourse");

if (pythonCourse) {
    pythonCourse.addEventListener("click", function () {
        window.location.href = "python.html";
    });
}
function continueLearning() {
    window.location.href = "python.html";
}