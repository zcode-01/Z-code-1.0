const form = document.getElementById("signupForm");
const message = document.getElementById("signupMessage");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const toggle = document.getElementById("togglePassword");
const submitBtn = document.getElementById("submitBtn");

if (toggle) {
  toggle.addEventListener("click", () => {
    const isPassword = passwordInput.type === "password";
    passwordInput.type = isPassword ? "text" : "password";
    toggle.textContent = isPassword ? "○" : "◉";
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (password.length < 6) {
    message.style.color = "#ef4444";
    message.textContent = "Password must be at least 6 characters long.";
    return;
  }

  message.style.color = "";
  message.textContent = "Creating your account...";
  if (submitBtn) submitBtn.disabled = true;

  try {
    const data = await ZCodeAPI.signup(name, email, password);
    message.style.color = "#4ade80";
    message.textContent = `Account created successfully! Welcome, ${name}! Redirecting…`;
    setTimeout(() => {
      window.location.href = "home.html";
    }, 600);
  } catch (err) {
    if (submitBtn) submitBtn.disabled = false;
    message.style.color = "#ef4444";
    message.textContent = `Sign-up failed: ${err.message || "Please check your inputs"}`;
  }
});

const demoBtn = document.getElementById("demoBtn");
if (demoBtn) {
  demoBtn.addEventListener("click", async () => {
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
}
