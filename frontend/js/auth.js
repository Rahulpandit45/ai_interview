/**
 * auth.js - Authentication handler for login, registration, and route guards
 */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const identifier = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();
      const portalRole = document.getElementById("portal-role")?.value || "candidate";
      const submitBtn = loginForm.querySelector("button[type='submit']");

      if (portalRole === "admin") {
        if (identifier.includes("@")) {
          showToast("Admins can log in only using their official Admin ID (e.g. ADM-2026-001). Email login is not permitted.", "error");
          return;
        }
      }

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = "Authenticating...";

        let payload;
        if (portalRole === "admin") {
          payload = { portal: "admin", admin_id: identifier, password };
        } else {
          payload = { portal: "candidate", identifier: identifier, email: identifier, password };
        }

        const data = await Api.request("/api/auth/login", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        const user = data.user;
        const isAdmin = user.role === "admin" || user.role === "recruiter";

        // Access enforcement: verify portal role match
        if (portalRole === "admin") {
          if (!isAdmin) {
            Api.clearAuth();
            showToast("Access Denied: Candidate accounts cannot access the Administrator Console. Please switch to Candidate Portal.", "error");
            return;
          }
          Api.setToken(data.token);
          Api.setUser(user);
          showToast(`Administrator authenticated. Welcome, ${user.full_name} (${user.admin_id || 'ADM'}).`, "success");
          setTimeout(() => {
            window.location.href = "admin.html";
          }, 800);
        } else {
          // Candidate portal login
          Api.setToken(data.token);
          Api.setUser(user);
          showToast(`Sign in successful! Welcome back, ${user.full_name}.`, "success");
          setTimeout(() => {
            window.location.href = "dashboard.html";
          }, 800);
        }
      } catch (err) {
        showToast(err.message || "Invalid credentials or password", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = portalRole === "admin" ? "Sign In with Official Admin ID" : "Sign In to Candidate Portal";
      }
    });
  }

  if (registerForm) {
    let selectedPhotoBlob = null;
    let webcamStream = null;

    // Detect if accessed directly via file:// which blocks webcam APIs in modern browsers
    if (window.location.protocol === "file:") {
      console.warn("Detected file:// protocol. Camera APIs are disabled by modern browsers on file://");
      showToast("Notice: Live camera requires http://localhost:5000/register.html (webcam is blocked on file://)", "warning");
    }

    const roleSelect = document.getElementById("role");
    const photoGroup = document.getElementById("candidate-photo-group");
    const photoFileInput = document.getElementById("photo-file-input");
    const photoPlaceholder = document.getElementById("photo-placeholder");
    const photoPreview = document.getElementById("photo-preview");
    const photoBadge = document.getElementById("photo-status-badge");
    const photoStatusText = document.getElementById("photo-status-text");
    const btnClearPhoto = document.getElementById("btn-clear-photo");

    if (typeof setupPasswordStrength === "function") {
      setupPasswordStrength("password", "password-strength-wrap");
    }

    // Polyfill & Cross-browser getUserMedia detection
    function getSupportedMediaDevices() {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        return navigator.mediaDevices;
      }
      const legacyGetUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;

      if (legacyGetUserMedia) {
        if (!navigator.mediaDevices) navigator.mediaDevices = {};
        navigator.mediaDevices.getUserMedia = function(constraints) {
          return new Promise((resolve, reject) => {
            legacyGetUserMedia.call(navigator, constraints, resolve, reject);
          });
        };
        return navigator.mediaDevices;
      }
      return null;
    }

    // Toggle photo section based on role
    if (roleSelect && photoGroup) {
      roleSelect.addEventListener("change", () => {
        photoGroup.style.display = roleSelect.value === "candidate" ? "block" : "none";
      });
    }

    // Clear/Retake camera photo
    if (btnClearPhoto) {
      btnClearPhoto.addEventListener("click", () => {
        selectedPhotoBlob = null;
        currentCapturedDataUrl = null;
        if (photoPreview) {
          photoPreview.src = "";
          photoPreview.style.display = "none";
        }
        if (photoPlaceholder) photoPlaceholder.style.display = "flex";
        if (photoBadge) photoBadge.style.display = "none";
        if (btnClearPhoto) btnClearPhoto.style.display = "none";
        if (photoStatusText) {
          photoStatusText.textContent = "Click 'Open Camera & Take Photo' to capture your live portrait for official Candidate ID generation.";
          photoStatusText.style.color = "var(--text-muted)";
        }
        if (btnOpenCamera) btnOpenCamera.click();
      });
    }

    // Webcam Modal Controls
    const webcamModal = document.getElementById("webcam-modal");
    const btnOpenCamera = document.getElementById("btn-open-camera");
    const btnCloseWebcam = document.getElementById("btn-close-webcam");
    const webcamVideo = document.getElementById("webcam-video");
    const webcamCanvas = document.getElementById("webcam-canvas");
    const webcamCapturedPreview = document.getElementById("webcam-captured-preview");
    const webcamFlash = document.getElementById("webcam-flash");
    const btnShutter = document.getElementById("btn-shutter");
    const webcamLiveControls = document.getElementById("webcam-live-controls");
    const webcamConfirmControls = document.getElementById("webcam-confirm-controls");
    const btnRetakePhoto = document.getElementById("btn-retake-photo");
    const btnUsePhoto = document.getElementById("btn-use-photo");

    let currentCapturedDataUrl = null;

    function stopWebcam() {
      if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
      }
      if (webcamVideo) webcamVideo.srcObject = null;
      if (webcamModal) webcamModal.classList.remove("open");
    }

    if (btnOpenCamera) {
      btnOpenCamera.addEventListener("click", async () => {
        const md = getSupportedMediaDevices();
        if (!md || !md.getUserMedia) {
          if (window.location.protocol === "file:") {
            showToast("Webcam is blocked on file:// by browser security. Redirecting to http://localhost:5000/register.html...", "warning");
            setTimeout(() => {
              window.location.href = "http://localhost:5000/register.html";
            }, 1200);
            return;
          }
          if (!window.isSecureContext && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
            showToast("Webcam requires a secure context (http://localhost:5000). Redirecting...", "warning");
            setTimeout(() => {
              window.location.href = `http://localhost:${window.location.port || 5000}/register.html`;
            }, 1200);
            return;
          }
          showToast("Camera access is not supported in this browser. Please open http://localhost:5000/register.html in Chrome, Edge, or Firefox.", "error");
          return;
        }

        try {
          try {
            webcamStream = await md.getUserMedia({
              video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
              audio: false
            });
          } catch (constraintErr) {
            console.warn("Ideal video constraints failed, trying basic video constraint:", constraintErr);
            webcamStream = await md.getUserMedia({ video: true, audio: false });
          }

          webcamVideo.srcObject = webcamStream;
          webcamVideo.style.display = "block";
          webcamCapturedPreview.style.display = "none";
          if (guideOverlay) guideOverlay.style.display = "flex";
          webcamLiveControls.style.display = "flex";
          webcamConfirmControls.style.display = "none";
          webcamModal.classList.add("open");
          await webcamVideo.play().catch(e => console.warn("Video play:", e));
        } catch (err) {
          console.error("Camera access error:", err);
          if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
            showToast("Camera permission denied. Please click the camera icon in your browser address bar to allow webcam access.", "error");
          } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
            showToast("No camera detected. Please connect or enable your webcam to capture your live photo.", "error");
          } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
            showToast("Camera is in use by another program (Zoom, Teams, etc.). Please close it and retry.", "error");
          } else {
            showToast(`Unable to access camera: ${err.message || "Unknown error"}`, "error");
          }
        }
      });
    }

    if (btnCloseWebcam) {
      btnCloseWebcam.addEventListener("click", stopWebcam);
    }

    if (webcamModal) {
      webcamModal.addEventListener("click", (e) => {
        if (e.target === webcamModal) stopWebcam();
      });
    }

    const guideOverlay = document.getElementById("webcam-guide-overlay");

    if (btnShutter) {
      btnShutter.addEventListener("click", () => {
        if (!webcamVideo || !webcamStream) return;

        // Flash animation
        if (webcamFlash) {
          webcamFlash.classList.add("flash");
          setTimeout(() => webcamFlash.classList.remove("flash"), 180);
        }

        const width = webcamVideo.videoWidth || 640;
        const height = webcamVideo.videoHeight || 480;
        webcamCanvas.width = width;
        webcamCanvas.height = height;

        const ctx = webcamCanvas.getContext("2d");
        // Flip canvas to match mirrored video
        ctx.translate(width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(webcamVideo, 0, 0, width, height);

        currentCapturedDataUrl = webcamCanvas.toDataURL("image/jpeg", 0.92);
        webcamCapturedPreview.src = currentCapturedDataUrl;
        webcamCapturedPreview.style.display = "block";
        webcamVideo.style.display = "none";
        if (guideOverlay) guideOverlay.style.display = "none";
        webcamLiveControls.style.display = "none";
        webcamConfirmControls.style.display = "flex";
      });
    }

    if (btnRetakePhoto) {
      btnRetakePhoto.addEventListener("click", () => {
        webcamCapturedPreview.style.display = "none";
        webcamVideo.style.display = "block";
        if (guideOverlay) guideOverlay.style.display = "flex";
        webcamLiveControls.style.display = "flex";
        webcamConfirmControls.style.display = "none";
        currentCapturedDataUrl = null;
      });
    }

    if (btnUsePhoto) {
      btnUsePhoto.addEventListener("click", () => {
        if (!currentCapturedDataUrl) return;

        // Convert base64 data URL to Blob
        fetch(currentCapturedDataUrl)
          .then(res => res.blob())
          .then(blob => {
            selectedPhotoBlob = blob;
            photoPreview.src = currentCapturedDataUrl;
            photoPreview.style.display = "block";
            photoPlaceholder.style.display = "none";
            photoBadge.style.display = "flex";
            btnClearPhoto.style.display = "inline-flex";
            photoStatusText.textContent = "✓ Live camera photo verified and ready for Candidate ID generation.";
            photoStatusText.style.color = "var(--accent-emerald)";
            showToast("Live camera photo captured and verified!", "success");
            stopWebcam();
          });
      });
    }

    // Success Modal elements
    const successModal = document.getElementById("success-id-modal");
    const issuedCidSpan = document.getElementById("issued-candidate-id");
    const btnModalCopyId = document.getElementById("btn-modal-copy-id");
    const btnProceedDashboard = document.getElementById("btn-proceed-dashboard");

    if (btnModalCopyId) {
      btnModalCopyId.addEventListener("click", () => {
        const cid = issuedCidSpan.textContent;
        navigator.clipboard.writeText(cid).then(() => {
          showToast(`Candidate ID ${cid} copied to clipboard!`, "success");
          btnModalCopyId.textContent = "✓ Copied";
          setTimeout(() => { btnModalCopyId.textContent = "📋 Copy"; }, 2000);
        });
      });
    }

    if (btnProceedDashboard) {
      btnProceedDashboard.addEventListener("click", () => {
        window.location.href = "dashboard.html";
      });
    }

    const btnSendOtp = document.getElementById("btn-register-submit");
    const sendOtpSpinner = document.getElementById("send-otp-spinner");
    const sendOtpBtnText = document.getElementById("send-otp-btn-text");

    // Direct Candidate Registration Form Submission (Instant Verification by Default)
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const full_name = document.getElementById("full_name").value.trim();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();
      const target_role = document.getElementById("target_role") ? document.getElementById("target_role").value : "Software Engineer";

      if (!selectedPhotoBlob) {
        showToast("Please capture your live photo using the camera before completing registration.", "warning");
        if (btnOpenCamera) btnOpenCamera.click();
        return;
      }

      try {
        if (sendOtpSpinner) sendOtpSpinner.style.display = "inline-block";
        if (btnSendOtp) btnSendOtp.disabled = true;
        if (sendOtpBtnText) sendOtpBtnText.textContent = "Creating Account...";

        const formData = new FormData();
        formData.append("full_name", full_name);
        formData.append("email", email);
        formData.append("password", password);
        formData.append("role", "candidate");
        formData.append("target_role", target_role);

        if (selectedPhotoBlob) {
          formData.append("profile_photo", selectedPhotoBlob, "candidate_photo.jpg");
        }

        const data = await Api.request("/api/auth/register", {
          method: "POST",
          body: formData
        });

        Api.setToken(data.token);
        Api.setUser(data.user);

        if (sendOtpBtnText) sendOtpBtnText.textContent = "Account Created ✓";
        showToast(`Registration successful! Candidate ID: ${data.candidate_id}`, "success");

        if (data.candidate_id) {
          if (issuedCidSpan) issuedCidSpan.textContent = data.candidate_id;
          if (successModal) {
            successModal.classList.add("open");
            const btnProceed = document.getElementById("btn-proceed-dashboard");
            if (btnProceed) {
              btnProceed.onclick = () => { window.location.href = "dashboard.html"; };
            }
          } else {
            setTimeout(() => { window.location.href = "dashboard.html"; }, 1000);
          }
        } else {
          setTimeout(() => { window.location.href = "dashboard.html"; }, 800);
        }

      } catch (err) {
        showToast(err.message || "Registration failed. Please check your details and try again.", "error");
      } finally {
        if (sendOtpSpinner) sendOtpSpinner.style.display = "none";
        if (btnSendOtp) btnSendOtp.disabled = false;
        if (sendOtpBtnText) sendOtpBtnText.textContent = "Create Candidate Account 🚀";
      }
    });
  }
});

function requireAuth(requiredRole = null) {
  const token = Api.getToken();
  const user = Api.getUser();
  if (!token || !user) {
    window.location.href = "login.html" + (requiredRole ? `?portal=${requiredRole}` : "");
    return false;
  }
  if (requiredRole === "admin" && user.role !== "admin" && user.role !== "recruiter") {
    showToast("Access Denied: Administrator privileges required.", "error");
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 1000);
    return false;
  }
  return true;
}

