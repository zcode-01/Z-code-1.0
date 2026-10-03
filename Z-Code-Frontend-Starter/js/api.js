/**
 * Z-Code API Client
 * ─────────────────────────────────────────────
 * Drop this file in your frontend js/ folder and
 * import it on any page to talk to the backend.
 *
 * Usage example:
 *   const token = await ZCodeAPI.login('dhanush@zcode.dev', 'demo123');
 *   const stats = await ZCodeAPI.getStats();
 */

const API_BASE = "http://localhost:8000/api";

// ─── Token Storage ───────────────────────────
const ZCodeAuth = {
  setToken(token) {
    localStorage.setItem("zcode_token", token);
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      if (payload && payload.sub) {
        localStorage.setItem("zcode_user_id", payload.sub);
      }
    } catch (e) {}
  },
  getToken() { return localStorage.getItem("zcode_token"); },
  getUserId() { return localStorage.getItem("zcode_user_id"); },
  clearToken() {
    localStorage.removeItem("zcode_token");
    localStorage.removeItem("zcode_user_id");
    localStorage.removeItem("pythonIntroductionPassed");
  },
  isLoggedIn() { return !!this.getToken(); },
};

// ─── Core Fetch Helper ───────────────────────
async function apiFetch(path, options = {}) {
  const token = ZCodeAuth.getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ─── Z-Code API ─────────────────────────────
const ZCodeAPI = {

  // AUTH
  async signup(name, email, password) {
    const data = await apiFetch("/auth/signup", {
      method: "POST",
      body: { name, email, password },
    });
    ZCodeAuth.setToken(data.access_token);
    return data;
  },

  async login(email, password) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    ZCodeAuth.setToken(data.access_token);
    return data;
  },

  logout() {
    ZCodeAuth.clearToken();
    window.location.href = "login.html";
  },

  async getMe() {
    return apiFetch("/auth/me");
  },

  // PROFILE & STATS
  async getStats() {
    return apiFetch("/users/stats");
  },

  async getProfile() {
    return apiFetch("/users/profile");
  },

  async updateProfile(name, avatarLetter) {
    return apiFetch("/users/profile", {
      method: "PATCH",
      body: { name, avatar_letter: avatarLetter },
    });
  },

  // COURSES
  async listCourses() {
    return apiFetch("/courses");
  },

  async getCourse(slug) {
    return apiFetch(`/courses/${slug}`);
  },

  async getCourseProgress(slug) {
    return apiFetch(`/courses/${slug}/progress`);
  },

  async completeLesson(courseSlug, lessonId) {
    return apiFetch(`/courses/${courseSlug}/complete`, {
      method: "POST",
      body: { lesson_id: lessonId },
    });
  },

  // QUIZZES
  async getQuiz(lessonId) {
    return apiFetch(`/quizzes/lesson/${lessonId}`);
  },

  /**
   * Submit quiz answers.
   * @param {number} quizId
   * @param {Array<{question_id: number, answer: string}>} answers
   */
  async submitQuiz(quizId, answers) {
    return apiFetch("/quizzes/submit", {
      method: "POST",
      body: { quiz_id: quizId, answers },
    });
  },

  async getQuizHistory() {
    return apiFetch("/quizzes/history");
  },

  // AI CHAT
  async sendChatMessage(message) {
    return apiFetch("/chat", {
      method: "POST",
      body: { message },
    });
  },

  async getChatHistory() {
    return apiFetch("/chat/history");
  },

  async clearChatHistory() {
    return apiFetch("/chat/history", { method: "DELETE" });
  },
};

// Export for use in other scripts
window.ZCodeAPI = ZCodeAPI;
window.ZCodeAuth = ZCodeAuth;
