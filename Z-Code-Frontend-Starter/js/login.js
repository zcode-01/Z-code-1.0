const form = document.getElementById("loginForm");
const message = document.getElementById("loginMessage");
const password = document.getElementById("password");
const toggle = document.getElementById("togglePassword");

toggle.addEventListener("click", () => {
  const isPassword = password.type === "password";
  password.type = isPassword ? "text" : "password";
  toggle.textContent = isPassword ? "○" : "◉";
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  message.textContent = "Demo login successful. Opening Z-Code…";
  setTimeout(() => location.href = "home.html", 450);
});

document.getElementById("googleBtn").addEventListener("click", () => {
  message.textContent = "Demo Google login successful. Opening Z-Code…";
  setTimeout(() => location.href = "home.html", 450);
});

document.getElementById("forgotLink").addEventListener("click", (e) => {
  e.preventDefault();
  message.textContent = "Password reset will be connected to Supabase later.";
});

document.getElementById("signupLink").addEventListener("click", (e) => {
  e.preventDefault();
  message.textContent = "Sign-up screen will be connected next.";
});
