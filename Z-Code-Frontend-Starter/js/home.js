/**
 * Z-Code — Dashboard Logic (home.js)
 */

document.addEventListener("DOMContentLoaded", async () => {

  // ─── DOM References ──────────────────────────────────────
  const fab = document.getElementById("aiFab");
  const chat = document.getElementById("aiChat");
  const closeAi = document.getElementById("closeAi");
  const aiForm = document.getElementById("aiForm");
  const aiInput = document.getElementById("aiInput");
  const aiBody = document.getElementById("aiBody");

  const themeToggle = document.getElementById("themeToggle");
  const notifBtn = document.getElementById("notifBtn");
  const notifPopover = document.getElementById("notifPopover");
  const profileMiniBtn = document.getElementById("profileMiniBtn");
  const profileDropdown = document.getElementById("profileDropdown");
  const logoutBtn = document.getElementById("logoutBtn");

  const modalBackdrop = document.getElementById("zModalBackdrop");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  const modalCloseBtn = document.getElementById("modalCloseBtn");

  // ─── Modal System ────────────────────────────────────────
  function openModal(title, html) {
    modalTitle.innerHTML = title;
    modalBody.innerHTML = html;
    modalBackdrop.classList.add("open");
  }

  function closeModal() {
    modalBackdrop.classList.remove("open");
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) closeModal();
    });
  }

  // ─── Load User Stats from Backend ────────────────────────
  if (window.ZCodeAuth && ZCodeAuth.isLoggedIn()) {
    try {
      const stats = await ZCodeAPI.getStats();
      if (stats) {
        const topName = document.getElementById("topUserName");
        const topAvatar = document.getElementById("topAvatar");
        const dropName = document.getElementById("dropName");
        const dropEmail = document.getElementById("dropEmail");
        const dropAvatar = document.getElementById("dropAvatar");

        const displayName = stats.name || "Dhanush";
        const initial = displayName.charAt(0).toUpperCase();

        if (topName) topName.textContent = displayName;
        if (topAvatar) topAvatar.textContent = initial;
        if (dropName) dropName.textContent = displayName;
        if (dropEmail) dropEmail.textContent = stats.email || "user@zcode.dev";
        if (dropAvatar) dropAvatar.textContent = initial;

        const greetingH1 = document.querySelector(".welcome-row h1");
        if (greetingH1) greetingH1.innerHTML = `${displayName} <span class="crown">♔</span>`;

        // Update Stats Bar
        const totalXpStrong = document.querySelector(".stats > div:nth-child(1) strong");
        if (totalXpStrong) totalXpStrong.innerHTML = `${stats.xp || 0} <i>XP</i>`;

        const lessonsStrong = document.querySelector(".stats > div:nth-child(2) strong");
        if (lessonsStrong) lessonsStrong.innerHTML = `${stats.completed_lessons || 0} <i>done</i>`;

        const streakStrong = document.querySelector(".stats > div:nth-child(4) strong");
        if (streakStrong) streakStrong.innerHTML = `${stats.current_streak || 1} days <i>active</i>`;

        // Update Level Card
        const levelSpan = document.querySelector(".level-copy span");
        if (levelSpan) levelSpan.textContent = `Level ${stats.level || 1}`;

        const levelXpSmall = document.querySelector(".level-card > small");
        const nextLevelXp = (stats.level || 1) * 500;
        if (levelXpSmall) levelXpSmall.textContent = `${stats.xp || 0} / ${nextLevelXp} XP`;

        const levelProgressSpan = document.querySelector(".level-card .progress span");
        if (levelProgressSpan) {
          const pct = Math.min(100, Math.round(((stats.xp || 0) / nextLevelXp) * 100));
          levelProgressSpan.style.width = `${pct}%`;
        }

        // Update Continue Learning card based on user's actual quiz attempts
        try {
          const history = await ZCodeAPI.getQuizHistory();
          const hasPassed = Array.isArray(history) && history.some(a => a.quiz_id === 1 && a.passed);
          const continueMiniSpan = document.querySelector(".course-mini span");
          const continueFooterSpan = document.querySelector(".course-footer span");
          const continueProgressSpan = document.querySelector(".continue-card .progress span");

          if (hasPassed) {
            if (continueMiniSpan) continueMiniSpan.textContent = "Chapter 2: Variables & Data Types";
            if (continueFooterSpan) continueFooterSpan.textContent = "15%";
            if (continueProgressSpan) continueProgressSpan.style.width = "15%";
          } else {
            if (continueMiniSpan) continueMiniSpan.textContent = "Chapter 1: Introduction to Python";
            if (continueFooterSpan) continueFooterSpan.textContent = "0%";
            if (continueProgressSpan) continueProgressSpan.style.width = "0%";
          }
        } catch (e) {}
      }
    } catch (err) {
      console.warn("Could not fetch user stats:", err.message);
    }
  }

  // ─── Profile Dropdown & Logout ───────────────────────────
  if (profileMiniBtn && profileDropdown) {
    profileMiniBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      profileDropdown.classList.toggle("show");
      if (notifPopover) notifPopover.classList.remove("show");
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to log out?")) {
        ZCodeAPI.logout();
      }
    });
  }

  // ─── Notifications Popover ───────────────────────────────
  if (notifBtn && notifPopover) {
    notifBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      notifPopover.classList.toggle("show");
      if (profileDropdown) profileDropdown.classList.remove("show");
    });
  }

  // Close menus on outside click
  document.addEventListener("click", () => {
    if (profileDropdown) profileDropdown.classList.remove("show");
    if (notifPopover) notifPopover.classList.remove("show");
  });

  // ─── Theme Toggle ────────────────────────────────────────
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("light");
    });
  }

  // ─── Sidebar & Dashboard Buttons ─────────────────────────

  // 1. Projects
  const showProjectsModal = () => {
    openModal("💻 Real-World Python Projects", `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div style="border:1px solid #332d20;border-radius:10px;padding:16px;background:#14120e;">
          <h4 style="margin:0 0 6px;color:#f7d994;font-size:16px;">1. CLI Password Generator</h4>
          <p style="margin:0 0 10px;color:#aaa;font-size:13px;">Generate cryptographically secure random passwords using Python's <code>secrets</code> and <code>string</code> modules.</p>
          <span style="font-size:11px;padding:3px 8px;border-radius:4px;background:#252016;color:#e9c77d;">Beginner · +60 XP</span>
        </div>
        <div style="border:1px solid #332d20;border-radius:10px;padding:16px;background:#14120e;">
          <h4 style="margin:0 0 6px;color:#f7d994;font-size:16px;">2. Terminal Weather Dashboard</h4>
          <p style="margin:0 0 10px;color:#aaa;font-size:13px;">Fetch live JSON forecasts from weather APIs using <code>requests</code> and format output in ASCII tables.</p>
          <span style="font-size:11px;padding:3px 8px;border-radius:4px;background:#252016;color:#e9c77d;">Intermediate · +120 XP</span>
        </div>
        <div style="border:1px solid #332d20;border-radius:10px;padding:16px;background:#14120e;">
          <h4 style="margin:0 0 6px;color:#f7d994;font-size:16px;">3. FastAPI Web Service with SQLite</h4>
          <p style="margin:0 0 10px;color:#aaa;font-size:13px;">Build your own RESTful backend with endpoints, JWT auth, and database persistence.</p>
          <span style="font-size:11px;padding:3px 8px;border-radius:4px;background:#252016;color:#e9c77d;">Advanced · +250 XP</span>
        </div>
      </div>
    `);
  };

  const sideProjects = document.getElementById("sideProjects");
  const featuredProjectsBtn = document.getElementById("featuredProjectsBtn");
  if (sideProjects) sideProjects.addEventListener("click", (e) => { e.preventDefault(); showProjectsModal(); });
  if (featuredProjectsBtn) featuredProjectsBtn.addEventListener("click", showProjectsModal);

  // 2. Weekly League Leaderboard
  const leagueBtn = document.getElementById("leagueBtn");
  if (leagueBtn) {
    leagueBtn.addEventListener("click", () => {
      openModal("♨ Weekly League — Gold Tier", `
        <p style="color:#aaa;margin-top:0;">Top 5 learners this week get promoted to Diamond League on Sunday!</p>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-radius:10px;background:rgba(233,199,125,0.15);border:1px solid #e9c77d;">
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="font-size:18px;">🥇</span>
              <strong>Dhanush (You)</strong>
            </div>
            <span style="color:#f7d994;font-weight:bold;">1,260 XP</span>
          </div>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-radius:10px;background:#14120e;border:1px solid #28241d;">
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="font-size:18px;">🥈</span>
              <span>Sarah Chen</span>
            </div>
            <span style="color:#bbb;">1,180 XP</span>
          </div>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-radius:10px;background:#14120e;border:1px solid #28241d;">
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="font-size:18px;">🥉</span>
              <span>Alex Rivera</span>
            </div>
            <span style="color:#bbb;">950 XP</span>
          </div>
        </div>
      `);
    });
  }

  // 3. Certificates
  const sideCerts = document.getElementById("sideCerts");
  if (sideCerts) {
    sideCerts.addEventListener("click", (e) => {
      e.preventDefault();
      openModal("🎓 Your Verified Certificates", `
        <div style="text-align:center;padding:15px 0;">
          <div style="font-size:54px;margin-bottom:12px;">📜</div>
          <h4 style="margin:0 0 8px;color:#f7d994;font-size:18px;">Python Programming Specialist</h4>
          <p style="color:#aaa;font-size:13px;max-width:400px;margin:0 auto 16px;">Pass all chapter quizzes to earn your verifiable Z-Code graduation certificate.</p>
          <div style="max-width:300px;margin:0 auto 18px;">
            <div class="progress" style="height:8px;"><span style="width:67%;"></span></div>
            <small style="color:#e9c77d;display:block;margin-top:6px;">8 of 12 lessons completed (67%)</small>
          </div>
          <button onclick="window.location.href='python.html'" style="border:none;border-radius:8px;padding:10px 20px;background:linear-gradient(#f5d993,#e4bb69);color:#1a1711;font-weight:700;cursor:pointer;">
            Continue Lessons →
          </button>
        </div>
      `);
    });
  }

  // 4. Community
  const sideCommunity = document.getElementById("sideCommunity");
  if (sideCommunity) {
    sideCommunity.addEventListener("click", (e) => {
      e.preventDefault();
      openModal("♧ Z-Code Developer Community", `
        <div style="display:flex;flex-direction:column;gap:14px;">
          <p style="color:#bbb;margin-top:0;">Connect with fellow learners, share your code, and solve daily Python challenges together.</p>
          <div style="padding:14px;border-radius:10px;background:#14120e;border:1px solid #28241d;">
            <strong style="color:#f7d994;">🔥 Daily Challenge: Palindrome String Checker</strong>
            <p style="color:#aaa;font-size:12px;margin:6px 0 10px;">Write a Python function <code>is_palindrome(s)</code> that ignores punctuation and spaces.</p>
            <button onclick="window.location.href='python.html'" style="border:none;background:#2a251b;color:#e9c77d;padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer;">Solve Challenge ⚡</button>
          </div>
          <div style="padding:14px;border-radius:10px;background:#14120e;border:1px solid #28241d;">
            <strong style="color:#f7d994;">💬 Discord Community</strong>
            <p style="color:#aaa;font-size:12px;margin:6px 0 0;">Over 12,000 students active daily helping each other debug code.</p>
          </div>
        </div>
      `);
    });
  }

  // 5. Resources & Documentation
  const sideResources = document.getElementById("sideResources");
  if (sideResources) {
    sideResources.addEventListener("click", (e) => {
      e.preventDefault();
      openModal("▱ Python Resources & Cheat Sheets", `
        <div style="display:flex;flex-direction:column;gap:12px;">
          <a href="https://docs.python.org/3/" target="_blank" style="padding:12px 16px;border-radius:8px;background:#14120e;border:1px solid #28241d;color:#f7d994;text-decoration:none;display:flex;justify-content:space-between;">
            <span>📖 Official Python 3 Documentation</span>
            <span>↗</span>
          </a>
          <a href="quiz.html" style="padding:12px 16px;border-radius:8px;background:#14120e;border:1px solid #28241d;color:#f7d994;text-decoration:none;display:flex;justify-content:space-between;">
            <span>⚡ Interactive Chapter 1 Quiz Practice</span>
            <span>→</span>
          </a>
          <a href="variables.html" style="padding:12px 16px;border-radius:8px;background:#14120e;border:1px solid #28241d;color:#f7d994;text-decoration:none;display:flex;justify-content:space-between;">
            <span>📦 Chapter 2: Variables & Data Types Guide</span>
            <span>→</span>
          </a>
        </div>
      `);
    });
  }

  // 6. Profile Modal
  const openProfileModal = async () => {
    let xp = 1260;
    let level = 3;
    let name = "Dhanush";
    let email = "dhanush@zcode.dev";

    if (window.ZCodeAuth && ZCodeAuth.isLoggedIn()) {
      try {
        const stats = await ZCodeAPI.getStats();
        if (stats) {
          xp = stats.xp || xp;
          level = stats.level || level;
          name = stats.name || name;
          email = stats.email || email;
        }
      } catch (e) {}
    }

    openModal("♙ Learner Profile", `
      <div style="text-align:center;padding:10px 0;">
        <div class="avatar" style="width:68px;height:68px;font-size:28px;margin:0 auto 14px;">${name.charAt(0).toUpperCase()}</div>
        <h3 style="margin:0 0 4px;color:#f7d994;font-size:20px;">${name}</h3>
        <p style="color:#888;font-size:13px;margin:0 0 20px;">${email}</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;text-align:left;">
          <div style="background:#14120e;padding:14px;border-radius:10px;border:1px solid #28241d;">
            <small style="color:#888;">Current Rank</small>
            <div style="font-size:18px;color:#e9c77d;font-weight:bold;margin-top:4px;">Level ${level} (Rising)</div>
          </div>
          <div style="background:#14120e;padding:14px;border-radius:10px;border:1px solid #28241d;">
            <small style="color:#888;">Total XP</small>
            <div style="font-size:18px;color:#e9c77d;font-weight:bold;margin-top:4px;">${xp} XP</div>
          </div>
        </div>
      </div>
    `);
  };

  const sideProfile = document.getElementById("sideProfile");
  const dropProfileBtn = document.getElementById("dropProfileBtn");
  if (sideProfile) sideProfile.addEventListener("click", (e) => { e.preventDefault(); openProfileModal(); });
  if (dropProfileBtn) dropProfileBtn.addEventListener("click", openProfileModal);

  // 7. Settings Modal
  const openSettingsModal = () => {
    openModal("⚙ Platform Settings", `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-radius:8px;background:#14120e;">
          <div>
            <strong>Theme Mode</strong>
            <p style="margin:2px 0 0;font-size:12px;color:#888;">Switch between Dark Gold and Clean Light themes</p>
          </div>
          <button onclick="document.body.classList.toggle('light')" style="background:#2a251b;border:1px solid #e9c77d;color:#f7d994;padding:8px 14px;border-radius:8px;cursor:pointer;">
            Toggle Theme ☼
          </button>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-radius:8px;background:#14120e;">
          <div>
            <strong>Interactive Backend Host</strong>
            <p style="margin:2px 0 0;font-size:12px;color:#888;">http://localhost:8000/api</p>
          </div>
          <span style="color:#4ade80;font-size:13px;font-weight:bold;">Active ●</span>
        </div>
      </div>
    `);
  };

  const sideSettings = document.getElementById("sideSettings");
  const dropSettingsBtn = document.getElementById("dropSettingsBtn");
  if (sideSettings) sideSettings.addEventListener("click", (e) => { e.preventDefault(); openSettingsModal(); });
  if (dropSettingsBtn) dropSettingsBtn.addEventListener("click", openSettingsModal);

  // ─── AI Chatbot Connected to Backend ─────────────────────
  if (fab && chat) {
    fab.addEventListener("click", () => {
      chat.classList.add("open");
      chat.setAttribute("aria-hidden", "false");
      if (aiInput) aiInput.focus();
    });
  }

  if (closeAi && chat) {
    closeAi.addEventListener("click", () => {
      chat.classList.remove("open");
      chat.setAttribute("aria-hidden", "true");
    });
  }

  if (aiForm && aiInput && aiBody) {
    aiForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = aiInput.value.trim();
      if (!text) return;

      // Render user prompt
      const userMsg = document.createElement("div");
      userMsg.className = "user-message";
      userMsg.textContent = text;
      aiBody.appendChild(userMsg);
      aiInput.value = "";
      aiBody.scrollTop = aiBody.scrollHeight;

      // Thinking indicator
      const thinkingMsg = document.createElement("div");
      thinkingMsg.className = "ai-message";
      thinkingMsg.style.fontStyle = "italic";
      thinkingMsg.style.color = "#999";
      thinkingMsg.textContent = "Z-Code AI is typing...";
      aiBody.appendChild(thinkingMsg);
      aiBody.scrollTop = aiBody.scrollHeight;

      try {
        if (window.ZCodeAuth && !ZCodeAuth.isLoggedIn()) {
          // Auto login demo user if not logged in
          await ZCodeAPI.login("dhanush@zcode.dev", "demo123");
        }

        const res = await ZCodeAPI.sendChatMessage(text);
        thinkingMsg.style.fontStyle = "normal";
        thinkingMsg.style.color = "";
        thinkingMsg.textContent = res.reply;
      } catch (err) {
        thinkingMsg.style.fontStyle = "normal";
        thinkingMsg.style.color = "#f87171";
        thinkingMsg.textContent = `Tutor Assistant: ${err.message || "Failed to reach AI service"}`;
      }

      aiBody.scrollTop = aiBody.scrollHeight;
    });
  }

});

// Global navigation helper
window.continueLearning = function() {
  window.location.href = "python.html";
};