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

function getApiBase() {
  // 1. Manually overridden in localStorage
  try {
    const saved = localStorage.getItem("zcode_api_base");
    if (saved && saved.trim()) return saved.trim().replace(/\/+$/, "");
  } catch (e) {}

  // 2. Window global configuration if provided
  if (window.__ZCODE_API_BASE__) return window.__ZCODE_API_BASE__.replace(/\/+$/, "");

  // 3. Localhost development (or opened from file system)
  const host = window.location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || host === "" || window.location.protocol === "file:") {
    return "http://localhost:8000/api";
  }

  // 4. In production, connect directly to the live Render backend
  return "https://zcode-backend-9sfe.onrender.com/api";
}

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

  const base = getApiBase();
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const response = await fetch(`${base}${cleanPath}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || "";
    } catch (e) {
      errorDetail = `HTTP ${response.status} ${response.statusText || ""}`.trim();
    }
    throw new Error(errorDetail || `HTTP ${response.status}`);
  }

  return response.json();
}

// NVIDIA Configuration for frontend client
const NVIDIA_AI_CONFIG = {
  apiKey: "", // Kept securely on the backend in .env; never exposed in public client code
  baseUrl: "https://integrate.api.nvidia.com/v1",
  model: "nvidia/nemotron-3-ultra-550b-a55b",
  systemPrompt: `You are Z-Code AI, a friendly and encouraging coding tutor for the Z-Code learning platform.

Your role:
- Help students learn Python programming (and other languages)
- Explain programming concepts in simple, clear terms
- Encourage students when they're stuck
- Provide short code examples when helpful
- Keep answers concise and easy to understand for beginners
- Stay focused on coding/programming topics

Z-Code Platform features:
- Structured courses (Python, JavaScript, etc.)
- Lessons with quizzes to unlock the next chapter
- XP and leveling system to gamify learning
- Streak tracking for daily motivation

Always be warm, supportive, and encouraging. If someone is confused, reassure them that it's normal and that they'll get it with practice.`
};

// ─── Z-Code API ─────────────────────────────
const ZCodeAPI = {
  getBaseUrl() {
    return getApiBase();
  },
  setBaseUrl(url) {
    if (!url || !url.trim()) {
      localStorage.removeItem("zcode_api_base");
    } else {
      localStorage.setItem("zcode_api_base", url.trim().replace(/\/+$/, ""));
    }
  },

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

  // ─── NVIDIA NEMOTRON AI CLIENT ──────────────────
  getNvidiaConfig() {
    return { ...NVIDIA_AI_CONFIG };
  },

  setNvidiaApiKey(key) {
    if (key) NVIDIA_AI_CONFIG.apiKey = key;
  },

  async callNvidiaDirect(message, history = []) {
    const messages = [
      { role: "system", content: NVIDIA_AI_CONFIG.systemPrompt }
    ];
    if (Array.isArray(history)) {
      history.slice(-10).forEach(m => {
        messages.push({
          role: m.role === "assistant" || m.role === "model" ? "assistant" : "user",
          content: m.content || ""
        });
      });
    }
    messages.push({ role: "user", content: message });

    const response = await fetch(`${NVIDIA_AI_CONFIG.baseUrl.replace(/\/+$/, "")}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${NVIDIA_AI_CONFIG.apiKey}`,
      },
      body: JSON.stringify({
        model: NVIDIA_AI_CONFIG.model,
        messages: messages,
        temperature: 0.7,
        top_p: 0.95,
        max_tokens: 4096,
        chat_template_kwargs: { enable_thinking: true },
        stream: false,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`NVIDIA API error (${response.status}): ${errText}`);
    }

    const data = await response.json();
    const choice = data.choices && data.choices[0];
    const reply = (choice?.message?.content || choice?.message?.reasoning_content || "").trim();
    return {
      reply: reply || "I'm here to help you code! Ask me anything about your lessons.",
      reasoning: choice?.message?.reasoning_content || null,
      model: NVIDIA_AI_CONFIG.model,
      source: "nvidia-direct"
    };
  },

  // AI CHAT
  async sendChatMessage(message) {
    if (!message || !message.trim()) {
      throw new Error("Message cannot be empty.");
    }

    // 1. Send to backend endpoint (routes to NVIDIA Nemotron 3 Ultra and persists chat history)
    try {
      return await apiFetch("/chat", {
        method: "POST",
        body: { message },
      });
    } catch (backendError) {
      // 2. If backend is offline or returned an error, attempt direct client call (if permitted by environment)
      try {
        return await this.callNvidiaDirect(message);
      } catch (_) {
        const isNetworkErr = backendError.message && (
          backendError.message.includes("Failed to fetch") ||
          backendError.message.includes("NetworkError") ||
          backendError.message.includes("Load failed")
        );
        if (isNetworkErr) {
          throw new Error("Backend server is not running. Please start it with: cd backend && ./start.sh");
        }
        throw new Error(backendError.message || "Failed to reach AI service.");
      }
    }
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
