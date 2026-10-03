const form = document.getElementById("loginForm");
const message = document.getElementById("loginMessage");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const toggle = document.getElementById("togglePassword");
const submitBtn = form.querySelector('button[type="submit"]');

toggle.addEventListener("click", () => {
  const isPassword = passwordInput.type === "password";
  passwordInput.type = isPassword ? "text" : "password";
  toggle.textContent = isPassword ? "○" : "◉";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  message.style.color = "";
  message.textContent = "Logging in...";
  if (submitBtn) submitBtn.disabled = true;

  try {
    const data = await ZCodeAPI.login(email, password);
    message.style.color = "#4ade80";
    message.textContent = "Login successful! Opening Z-Code…";
    setTimeout(() => {
      window.location.href = "home.html";
    }, 400);
  } catch (err) {
    if (submitBtn) submitBtn.disabled = false;
    message.style.color = "#ef4444";
    message.textContent = `Login failed: ${err.message || "Invalid credentials or backend not running"}`;
  }
});

document.getElementById("googleBtn").addEventListener("click", async () => {
  message.style.color = "";
  message.textContent = "Logging in with demo account...";
  try {
    await ZCodeAPI.login("dhanush@zcode.dev", "demo123");
    message.style.color = "#4ade80";
    message.textContent = "Welcome, Dhanush! Opening Z-Code…";
    setTimeout(() => {
      window.location.href = "home.html";
    }, 400);
  } catch (err) {
    message.style.color = "#ef4444";
    message.textContent = `Demo login failed: ${err.message || "Could not reach backend"}`;
  }
});

document.getElementById("forgotLink").addEventListener("click", (e) => {
  e.preventDefault();
  message.style.color = "";
  message.textContent = "Password reset: contact admin@zcode.dev or use demo credentials.";
});
