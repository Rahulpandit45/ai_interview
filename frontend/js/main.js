/**
 * main.js - Core API Client, Auth State Management, Theme Manager, and Responsive UI
 */

function getApiBase() {
  try {
    if (window.API_BASE_URL) return window.API_BASE_URL;
    let stored = localStorage.getItem("ai_api_base");
    if (stored && stored.includes("api-interview.rahulkumarpandit.com.np")) {
      localStorage.removeItem("ai_api_base");
      stored = null;
    }
    if (stored) return stored;

    const loc = window.location;
    // When served from the live domain, use same-origin relative endpoints
    if (loc.hostname === "interview.rahulkumarpandit.com.np") {
      return "";
    }

    // If running on a standalone static file server (port 5500, 3000, 5173, etc.) or file: protocol,
    // route API calls to the Flask backend on port 5000
    if (loc.protocol === "file:" || (loc.port && loc.port !== "5000" && loc.port !== "8000")) {
      return `${loc.protocol === "file:" ? "http:" : loc.protocol}//${loc.hostname || "localhost"}:5000`;
    }
  } catch (e) {
    console.warn("API base detection fallback:", e);
  }
  return ""; // Relative path when served directly from Flask/FastAPI or Cloudflare tunnel
}

const API_BASE = getApiBase();

// Immediate theme execution to prevent Flash of Unstyled Content (FOUC)
(function initThemeEarly() {
  try {
    const savedTheme = localStorage.getItem("ai_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
  } catch (e) {
    console.warn("Theme init error:", e);
  }
})();

const ThemeManager = {
  getTheme() {
    return localStorage.getItem("ai_theme") || "dark";
  },
  setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("ai_theme", theme);
    this.updateToggleIcon(theme);
  },
  toggleTheme() {
    const current = this.getTheme();
    const next = current === "light" ? "dark" : "light";
    this.setTheme(next);
    showToast(`Switched to ${next === "light" ? "Light" : "Dark"} Mode`, "info");
  },
  updateToggleIcon(theme) {
    const btn = document.getElementById("theme-toggle-btn");
    if (!btn) return;
    if (theme === "light") {
      btn.textContent = "🌙";
      btn.title = "Switch to Dark Mode";
      btn.setAttribute("aria-label", "Switch to Dark Mode");
    } else {
      btn.textContent = "🌞";
      btn.title = "Switch to Light Mode";
      btn.setAttribute("aria-label", "Switch to Light Mode");
    }
  }
};

const Api = {
  getToken() {
    return localStorage.getItem("token");
  },
  setToken(token) {
    localStorage.setItem("token", token);
  },
  getUser() {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  },
  setUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
  },
  clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },
  getBaseUrl() {
    return API_BASE;
  },
  async request(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const config = {
      ...options,
      headers
    };

    const targetUrl = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;

    try {
      const res = await fetch(targetUrl, config);
      const contentType = res.headers.get("content-type") || "";
      let data;
      if (contentType.includes("application/json")) {
        data = await res.json();
      } else {
        const text = await res.text();
        if (!res.ok) {
          throw new Error(`Server connection error (${res.status}). Please make sure backend is running.`);
        }
        try {
          data = JSON.parse(text);
        } catch {
          data = { message: text, status: "error" };
        }
      }

      if (!res.ok) {
        throw new Error(data.message || data.error || `Request failed with status ${res.status}`);
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }
};

function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  
  const iconSymbol = type === "success" ? "✓" 
    : type === "error" ? "✕" 
    : type === "warning" ? "⚠" 
    : "ℹ";

  toast.innerHTML = `
    <div class="toast-content">
      <span class="toast-icon">${iconSymbol}</span>
      <span class="toast-message">${escapeNavHtml(message)}</span>
    </div>
    <button type="button" class="toast-close-btn" aria-label="Dismiss notification" title="Close">✕</button>
  `;

  const closeBtn = toast.querySelector(".toast-close-btn");
  let isClosing = false;
  const dismiss = () => {
    if (isClosing) return;
    isClosing = true;
    toast.style.animation = "toastSlideOut 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards";
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 280);
  };

  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    dismiss();
  });

  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(dismiss, duration);
  }
}

/**
 * Setup password visibility eye toggles on any .password-input-wrap
 */
function setupPasswordToggles() {
  document.querySelectorAll(".password-input-wrap").forEach(wrap => {
    const input = wrap.querySelector("input");
    const toggleBtn = wrap.querySelector(".password-eye-btn");
    if (!input || !toggleBtn || toggleBtn.dataset.bound) return;

    toggleBtn.dataset.bound = "true";
    toggleBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";
      toggleBtn.innerHTML = isPassword ? "🙈" : "👁";
      toggleBtn.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
      toggleBtn.title = isPassword ? "Hide password" : "Show password";
      input.focus();
    });
  });
}

/**
 * Setup real-time password strength meter
 */
function setupPasswordStrength(inputId, containerId) {
  const input = document.getElementById(inputId);
  const container = document.getElementById(containerId);
  if (!input || !container) return;

  const bar = container.querySelector(".password-strength-bar");
  const label = container.querySelector(".password-strength-label");
  if (!bar || !label) return;

  input.addEventListener("input", () => {
    const val = input.value;
    if (!val) {
      bar.className = "password-strength-bar";
      bar.style.width = "0%";
      label.textContent = "Strength: None";
      label.style.color = "var(--text-muted)";
      return;
    }

    let score = 0;
    if (val.length >= 8) score++;
    if (val.length >= 12) score++;
    if (/[a-z]/.test(val) && /[A-Z]/.test(val)) score++;
    if (/\d/.test(val)) score++;
    if (/[^a-zA-Z0-9]/.test(val)) score++;

    bar.className = "password-strength-bar";
    if (score <= 2) {
      bar.classList.add("weak");
      label.textContent = "Strength: Weak";
      label.style.color = "var(--accent-rose)";
    } else if (score === 3) {
      bar.classList.add("fair");
      label.textContent = "Strength: Fair";
      label.style.color = "var(--accent-amber)";
    } else if (score === 4) {
      bar.classList.add("good");
      label.textContent = "Strength: Good";
      label.style.color = "#38bdf8";
    } else {
      bar.classList.add("strong");
      label.textContent = "Strength: Strong (Secure)";
      label.style.color = "var(--accent-emerald)";
    }
  });
}

/**
 * Standard confirmation modal helper
 */
function showConfirmModal({ title, message, confirmText = "Confirm", cancelText = "Cancel", onConfirm }) {
  let overlay = document.getElementById("app-confirm-modal");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "app-confirm-modal";
    overlay.className = "modal-overlay";
    overlay.innerHTML = `
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title" id="modal-title-text">Confirm Action</h3>
          <button type="button" class="toast-close-btn" id="modal-close-icon">✕</button>
        </div>
        <div class="modal-body" id="modal-body-text">Are you sure?</div>
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" id="modal-cancel-btn">Cancel</button>
          <button type="button" class="btn btn-primary" id="modal-confirm-btn">Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
  }

  const titleEl = document.getElementById("modal-title-text");
  const bodyEl = document.getElementById("modal-body-text");
  const confirmBtn = document.getElementById("modal-confirm-btn");
  const cancelBtn = document.getElementById("modal-cancel-btn");
  const closeIcon = document.getElementById("modal-close-icon");

  titleEl.textContent = title;
  bodyEl.textContent = message;
  confirmBtn.textContent = confirmText;
  cancelBtn.textContent = cancelText;

  const close = () => {
    overlay.classList.remove("open");
  };

  const newConfirm = confirmBtn.cloneNode(true);
  confirmBtn.parentNode.replaceChild(newConfirm, confirmBtn);
  const newCancel = cancelBtn.cloneNode(true);
  cancelBtn.parentNode.replaceChild(newCancel, cancelBtn);
  const newClose = closeIcon.cloneNode(true);
  closeIcon.parentNode.replaceChild(newClose, closeIcon);

  newConfirm.addEventListener("click", () => {
    close();
    if (typeof onConfirm === "function") onConfirm();
  });
  newCancel.addEventListener("click", close);
  newClose.addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  requestAnimationFrame(() => {
    overlay.classList.add("open");
  });
}

function setupResponsiveNavbar() {
  const navContainer = document.querySelector(".navbar .nav-container");
  if (!navContainer) return;

  // 1. Ensure nav-menu-wrapper wraps .nav-links and #nav-user-slot
  let menuWrapper = document.getElementById("nav-menu-wrapper");
  const navLinksElem = navContainer.querySelector(".nav-links");
  const navUserElem = document.getElementById("nav-user-slot");

  if (!menuWrapper && navLinksElem) {
    menuWrapper = document.createElement("div");
    menuWrapper.id = "nav-menu-wrapper";
    menuWrapper.className = "nav-menu-wrapper";

    // Insert wrapper before navLinksElem and move elements inside
    navLinksElem.parentNode.insertBefore(menuWrapper, navLinksElem);
    menuWrapper.appendChild(navLinksElem);
    if (navUserElem) {
      menuWrapper.appendChild(navUserElem);
    }
  }

  // 2. Ensure .nav-actions exists for Theme Toggle & Mobile Hamburger Toggle
  let navActions = navContainer.querySelector(".nav-actions");
  if (!navActions) {
    navActions = document.createElement("div");
    navActions.className = "nav-actions";
    navContainer.appendChild(navActions);
  }

  // 3. Ensure Theme Toggle Button exists
  let themeBtn = document.getElementById("theme-toggle-btn");
  if (!themeBtn) {
    themeBtn = document.createElement("button");
    themeBtn.id = "theme-toggle-btn";
    themeBtn.className = "theme-toggle-btn";
    themeBtn.type = "button";
    navActions.appendChild(themeBtn);

    themeBtn.addEventListener("click", () => {
      ThemeManager.toggleTheme();
    });
  }
  ThemeManager.updateToggleIcon(ThemeManager.getTheme());

  // 4. Ensure Mobile Hamburger Toggle Button exists
  let navToggleBtn = document.getElementById("nav-toggle-btn");
  if (!navToggleBtn) {
    navToggleBtn = document.createElement("button");
    navToggleBtn.id = "nav-toggle-btn";
    navToggleBtn.className = "nav-toggle-btn";
    navToggleBtn.type = "button";
    navToggleBtn.setAttribute("aria-label", "Toggle Navigation");
    navToggleBtn.innerHTML = "☰";
    navActions.appendChild(navToggleBtn);

    navToggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = menuWrapper.classList.toggle("open");
      navToggleBtn.innerHTML = isOpen ? "✕" : "☰";
    });

    // Close menu on click outside
    document.addEventListener("click", (e) => {
      if (menuWrapper.classList.contains("open") && !menuWrapper.contains(e.target) && !navToggleBtn.contains(e.target)) {
        menuWrapper.classList.remove("open");
        navToggleBtn.innerHTML = "☰";
      }
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && menuWrapper.classList.contains("open")) {
        menuWrapper.classList.remove("open");
        navToggleBtn.innerHTML = "☰";
      }
    });

    // Close on window resize to desktop
    window.addEventListener("resize", () => {
      if (window.innerWidth > 860 && menuWrapper.classList.contains("open")) {
        menuWrapper.classList.remove("open");
        navToggleBtn.innerHTML = "☰";
      }
    });
  }
}

function updateNavigationAuth() {
  setupResponsiveNavbar();

  const user = Api.getUser();
  const navUserElem = document.getElementById("nav-user-slot");
  const navLinksElem = document.querySelector(".nav-links");
  const currentPath = window.location.pathname.split("/").pop() || "index.html";

  // Dynamic role-based navigation links
  if (navLinksElem) {
    if (user && (user.role === "admin" || user.role === "recruiter")) {
      navLinksElem.innerHTML = `
        <li><a href="index.html" class="nav-link ${currentPath === 'index.html' || currentPath === '' ? 'active' : ''}">Home</a></li>
        <li><a href="admin.html" class="nav-link ${currentPath === 'admin.html' ? 'active' : ''}">Admin Console</a></li>
        <li><a href="db_viewer.html" class="nav-link ${currentPath === 'db_viewer.html' ? 'active' : ''}">Database Records</a></li>
      `;
    } else if (user) {
      navLinksElem.innerHTML = `
        <li><a href="index.html" class="nav-link ${currentPath === 'index.html' || currentPath === '' ? 'active' : ''}">Home</a></li>
        <li><a href="dashboard.html" class="nav-link ${currentPath === 'dashboard.html' ? 'active' : ''}">Candidate Dashboard</a></li>
        <li><a href="resume_upload.html" class="nav-link ${currentPath === 'resume_upload.html' ? 'active' : ''}">Resume Screening</a></li>
        <li><a href="interview.html" class="nav-link ${currentPath === 'interview.html' ? 'active' : ''}">Interview Room</a></li>
      `;
    } else {
      const isIndex = currentPath === 'index.html' || currentPath === '';
      if (isIndex) {
        navLinksElem.innerHTML = `
          <li><a href="index.html" class="nav-link active">Home</a></li>
          <li><a href="#workflow" class="nav-link">How to Use</a></li>
          <li><a href="#warning-system" class="nav-link">Proctoring &amp; Warning</a></li>
          <li><a href="login.html?portal=candidate" class="nav-link">Candidate Portal</a></li>
          <li><a href="login.html?portal=admin" class="nav-link">Administrator Portal</a></li>
        `;
      } else {
        navLinksElem.innerHTML = `
          <li><a href="index.html" class="nav-link">Home</a></li>
          <li><a href="index.html#workflow" class="nav-link">How to Use</a></li>
          <li><a href="index.html#warning-system" class="nav-link">Proctoring &amp; Warning</a></li>
          <li><a href="login.html?portal=candidate" class="nav-link ${currentPath === 'login.html' && window.location.search.includes('candidate') ? 'active' : ''}">Candidate Portal</a></li>
          <li><a href="login.html?portal=admin" class="nav-link ${currentPath === 'login.html' && (window.location.search.includes('admin') || window.location.search.includes('recruiter')) ? 'active' : ''}">Administrator Portal</a></li>
        `;
      }
    }
  }

  // Nav user profile slot
  if (navUserElem) {
    if (user) {
      const isAdmin = user.role === "admin" || user.role === "recruiter";
      const roleLabel = isAdmin ? "Administrator" : "Candidate";
      const roleBadgeBg = isAdmin ? "rgba(99, 102, 241, 0.2)" : "rgba(16, 185, 129, 0.2)";
      const roleBadgeColor = isAdmin ? "#a5b4fc" : "#34d399";

      const avatarHtml = user.profile_photo_url
        ? `<img src="${user.profile_photo_url}" class="candidate-avatar-nav" alt="${escapeNavHtml(user.full_name)}">`
        : "";

      navUserElem.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
          ${avatarHtml}
          <span class="badge-role" style="background:${roleBadgeBg}; color:${roleBadgeColor}; font-weight:700;">${roleLabel}</span>
          <span style="font-weight:600; font-size:0.92rem; color:var(--text-primary);">${escapeNavHtml(user.full_name)}</span>
          <button id="nav-logout-btn" class="btn btn-outline btn-sm">Sign Out</button>
        </div>
      `;
      document.getElementById("nav-logout-btn")?.addEventListener("click", () => {
        const wasAdmin = isAdmin;
        Api.clearAuth();
        showToast("Signed out successfully", "info");
        setTimeout(() => {
          window.location.href = wasAdmin ? "login.html?portal=admin" : "login.html?portal=candidate";
        }, 500);
      });
    } else {
      navUserElem.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
          <a href="login.html" class="btn btn-outline btn-sm">Sign In</a>
          <a href="register.html" class="btn btn-primary btn-sm">Register</a>
        </div>
      `;
    }
  }

  // Ensure theme button state is refreshed
  ThemeManager.updateToggleIcon(ThemeManager.getTheme());
}

function escapeNavHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  updateNavigationAuth();
  setupPasswordToggles();
});
