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

    // Multi-Step OTP Verification & Candidate Registration Controller
    const stepForm = document.getElementById("step-form-container");
    const stepOtp = document.getElementById("step-otp-container");
    const stepSuccess = document.getElementById("step-success-container");

    const btnSendOtp = document.getElementById("btn-register-submit");
    const sendOtpSpinner = document.getElementById("send-otp-spinner");
    const sendOtpBtnText = document.getElementById("send-otp-btn-text");

    const otpDisplayEmail = document.getElementById("otp-display-email");
    const otpErrorBanner = document.getElementById("otp-error-banner");
    const otpInputsRow = document.getElementById("otp-inputs-row");
    const otpBoxes = document.querySelectorAll(".otp-box");
    const otpTimerWrap = document.getElementById("otp-timer-wrap");
    const otpTimerCount = document.getElementById("otp-timer-count");
    const otpExpiredMsg = document.getElementById("otp-expired-msg");
    const btnVerifyOtp = document.getElementById("btn-verify-otp");
    const verifyOtpSpinner = document.getElementById("verify-otp-spinner");
    const verifyOtpBtnText = document.getElementById("verify-otp-btn-text");
    const btnResendOtp = document.getElementById("btn-resend-otp");
    const resendCooldownText = document.getElementById("resend-cooldown-text");
    const btnBackToForm = document.getElementById("btn-back-to-form");

    let currentVerificationToken = null;
    let pendingCandidateData = null;
    let countdownTimerId = null;
    let cooldownTimerId = null;
    let linkPollingTimer = null;

    function stopLinkPolling() {
      if (linkPollingTimer) {
        clearInterval(linkPollingTimer);
        linkPollingTimer = null;
      }
    }

    function startLinkPolling(email) {
      stopLinkPolling();
      linkPollingTimer = setInterval(async () => {
        if (!email) return;
        try {
          const res = await Api.request(`/api/auth/verification-status?email=${encodeURIComponent(email)}`);
          if (res && res.verified && res.verification_token) {
            stopLinkPolling();
            clearInterval(countdownTimerId);
            currentVerificationToken = res.verification_token;
            showToast("Email verified via link! Completing your registration...", "success");
            setTimeout(async () => {
              switchStep(stepOtp, stepSuccess);
              await completeCandidateRegistration();
            }, 300);
          }
        } catch (e) {
          // Ignore background polling network glitches
        }
      }, 3000);
    }

    function switchStep(fromEl, toEl) {
      if (fromEl) {
        fromEl.classList.remove("reg-step-active");
        fromEl.classList.add("reg-step-hidden");
      }
      if (toEl) {
        toEl.classList.remove("reg-step-hidden");
        toEl.classList.add("reg-step-active");
      }
    }

    function startCountdown(durationSecs = 300) {
      clearInterval(countdownTimerId);
      let remaining = durationSecs;
      if (otpTimerCount) {
        otpTimerCount.classList.remove("warning", "expired");
      }
      if (otpTimerWrap) otpTimerWrap.style.display = "flex";
      if (otpExpiredMsg) otpExpiredMsg.style.display = "none";
      if (btnVerifyOtp) btnVerifyOtp.disabled = false;

      function tick() {
        if (!otpTimerCount) return;
        const mins = Math.floor(remaining / 60);
        const secs = remaining % 60;
        otpTimerCount.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

        if (remaining <= 60 && remaining > 0) {
          otpTimerCount.classList.add("warning");
        }

        if (remaining <= 0) {
          clearInterval(countdownTimerId);
          stopLinkPolling();
          otpTimerCount.classList.remove("warning");
          otpTimerCount.classList.add("expired");
          otpTimerCount.textContent = "00:00";
          if (otpExpiredMsg) otpExpiredMsg.style.display = "block";
          if (btnVerifyOtp) btnVerifyOtp.disabled = true;
          showToast("Your verification code has expired. Please click Resend OTP.", "warning");
        }
        remaining--;
      }

      tick();
      countdownTimerId = setInterval(tick, 1000);
    }

    function startCooldown(cooldownSecs = 60) {
      clearInterval(cooldownTimerId);
      let remaining = cooldownSecs;
      if (btnResendOtp) btnResendOtp.disabled = true;
      if (resendCooldownText) resendCooldownText.style.display = "inline";

      function tick() {
        if (remaining <= 0) {
          clearInterval(cooldownTimerId);
          if (btnResendOtp) {
            btnResendOtp.disabled = false;
            btnResendOtp.textContent = "Resend Link";
          }
          if (resendCooldownText) resendCooldownText.style.display = "none";
        } else {
          if (resendCooldownText) resendCooldownText.textContent = `(${remaining}s)`;
          remaining--;
        }
      }

      tick();
      cooldownTimerId = setInterval(tick, 1000);
    }

    function clearOtpBoxes() {
      if (otpBoxes && otpBoxes.length) {
        otpBoxes.forEach(box => {
          box.value = "";
          box.classList.remove("error", "pop");
        });
      }
      if (otpErrorBanner) {
        otpErrorBanner.style.display = "none";
        otpErrorBanner.textContent = "";
      }
    }

    // OTP Input Event Listeners (Auto-advance, Backspace, Paste, Animations)
    if (otpBoxes && otpBoxes.length > 0) {
      otpBoxes.forEach((box, idx) => {
        // Input event
        box.addEventListener("input", (e) => {
          const val = e.target.value;
          // Keep only numeric characters
          const cleanVal = val.replace(/\D/g, "");
          e.target.value = cleanVal.slice(-1);

          if (e.target.value) {
            // Pop animation
            e.target.classList.add("pop");
            setTimeout(() => e.target.classList.remove("pop"), 220);

            // Remove error highlight on input
            otpBoxes.forEach(b => b.classList.remove("error"));
            if (otpErrorBanner) otpErrorBanner.style.display = "none";

            // Auto-advance to next box
            if (idx < otpBoxes.length - 1) {
              otpBoxes[idx + 1].focus();
            } else {
              // Last box filled: auto-trigger verification if all 6 filled
              const fullCode = Array.from(otpBoxes).map(b => b.value).join("");
              if (fullCode.length === 6 && btnVerifyOtp && !btnVerifyOtp.disabled) {
                btnVerifyOtp.click();
              }
            }
          }
        });

        // Keydown navigation (Backspace, Arrow keys)
        box.addEventListener("keydown", (e) => {
          if (e.key === "Backspace") {
            if (!box.value && idx > 0) {
              otpBoxes[idx - 1].focus();
            }
          } else if (e.key === "ArrowLeft" && idx > 0) {
            otpBoxes[idx - 1].focus();
          } else if (e.key === "ArrowRight" && idx < otpBoxes.length - 1) {
            otpBoxes[idx + 1].focus();
          }
        });

        // Paste support: Handles full 6-digit paste across boxes
        box.addEventListener("paste", (e) => {
          e.preventDefault();
          const pastedData = (e.clipboardData || window.clipboardData).getData("text");
          const digits = pastedData.replace(/\D/g, "").slice(0, 6);

          if (digits) {
            digits.split("").forEach((digit, i) => {
              if (otpBoxes[i]) {
                otpBoxes[i].value = digit;
                otpBoxes[i].classList.add("pop");
                setTimeout(() => otpBoxes[i].classList.remove("pop"), 250);
              }
            });

            // Focus appropriate box
            const nextIdx = Math.min(digits.length, otpBoxes.length - 1);
            otpBoxes[nextIdx].focus();

            // Auto trigger verification if complete 6 digits pasted
            if (digits.length === 6 && btnVerifyOtp && !btnVerifyOtp.disabled) {
              setTimeout(() => { btnVerifyOtp.click(); }, 150);
            }
          }
        });
      });
    }

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

    // Step 2: Verify OTP
    if (btnVerifyOtp) {
      btnVerifyOtp.addEventListener("click", async () => {
        if (!pendingCandidateData) {
          showToast("Session expired. Please re-enter your registration details.", "error");
          switchStep(stepOtp, stepForm);
          return;
        }

        const otpCode = Array.from(otpBoxes).map(b => b.value.trim()).join("");

        if (otpCode.length < 6) {
          if (otpInputsRow) {
            otpInputsRow.classList.add("shake");
            setTimeout(() => otpInputsRow.classList.remove("shake"), 500);
          }
          if (otpErrorBanner) {
            otpErrorBanner.textContent = "Please enter all 6 digits of the verification code.";
            otpErrorBanner.style.display = "block";
          }
          otpBoxes.forEach(b => { if (!b.value) b.classList.add("error"); });
          showToast("Please enter all 6 digits.", "warning");
          return;
        }

        try {
          if (verifyOtpSpinner) verifyOtpSpinner.style.display = "inline-block";
          if (verifyOtpBtnText) verifyOtpBtnText.textContent = "Checking OTP...";
          btnVerifyOtp.disabled = true;

          const verifyRes = await Api.request("/api/auth/verify-otp", {
            method: "POST",
            body: JSON.stringify({
              email: pendingCandidateData.email,
              otp: otpCode
            })
          });

          // Verification succeeded
          clearInterval(countdownTimerId);
          stopLinkPolling();
          currentVerificationToken = verifyRes.verification_token;

          if (verifyOtpBtnText) verifyOtpBtnText.textContent = "Success ✓";
          showToast("Email successfully verified!", "success");

          // Transition to Step 3: Checkmark & Final Registration
          setTimeout(async () => {
            switchStep(stepOtp, stepSuccess);
            await completeCandidateRegistration();
          }, 450);

        } catch (err) {
          if (otpInputsRow) {
            otpInputsRow.classList.add("shake");
            setTimeout(() => otpInputsRow.classList.remove("shake"), 500);
          }
          otpBoxes.forEach(b => b.classList.add("error"));

          if (otpErrorBanner) {
            otpErrorBanner.textContent = err.message || "Invalid OTP. Please check the code and try again.";
            otpErrorBanner.style.display = "block";
          }
          showToast(err.message || "Invalid OTP code", "error");

          if (otpBoxes[0]) otpBoxes[0].focus();
        } finally {
          if (verifyOtpSpinner) verifyOtpSpinner.style.display = "none";
          if (verifyOtpBtnText) verifyOtpBtnText.textContent = "Verify Email";
          btnVerifyOtp.disabled = false;
        }
      });
    }

    // Resend OTP Button
    if (btnResendOtp) {
      btnResendOtp.addEventListener("click", async () => {
        if (!pendingCandidateData || !pendingCandidateData.email) {
          showToast("Candidate data not found. Please restart registration.", "error");
          switchStep(stepOtp, stepForm);
          return;
        }

        try {
          btnResendOtp.disabled = true;
          btnResendOtp.textContent = "Sending...";

          const res = await Api.request("/api/auth/resend-otp", {
            method: "POST",
            body: JSON.stringify({
              email: pendingCandidateData.email,
              full_name: pendingCandidateData.full_name
            })
          });

          showToast("New verification code sent successfully!", "success");
          clearOtpBoxes();

          const devLinkContainer = document.getElementById("dev-link-container");
          const devLinkAnchor = document.getElementById("dev-link-anchor");
          if (devLinkContainer && devLinkAnchor && res.verification_link) {
            devLinkAnchor.href = res.verification_link;
            devLinkContainer.style.display = "block";
          }

          if (otpBoxes[0]) otpBoxes[0].focus();
          startCountdown(res.expires_in_seconds || 300);
          startCooldown(res.cooldown_seconds || 60);

        } catch (err) {
          showToast(err.message || "Failed to resend OTP.", "error");
          btnResendOtp.disabled = false;
          btnResendOtp.textContent = "Resend OTP";
        }
      });
    }

    // Back to form button
    if (btnBackToForm) {
      btnBackToForm.addEventListener("click", () => {
        clearInterval(countdownTimerId);
        clearInterval(cooldownTimerId);
        stopLinkPolling();
        switchStep(stepOtp, stepForm);
      });
    }

    // Step 3: Final Registration with Verified Token
    async function completeCandidateRegistration() {
      if (!pendingCandidateData || !currentVerificationToken) {
        showToast("Missing verification token. Please verify your email.", "error");
        switchStep(stepSuccess, stepForm);
        return;
      }

      try {
        const formData = new FormData();
        formData.append("full_name", pendingCandidateData.full_name);
        formData.append("email", pendingCandidateData.email);
        formData.append("password", pendingCandidateData.password);
        formData.append("role", "candidate");
        formData.append("target_role", pendingCandidateData.target_role);
        formData.append("verification_token", currentVerificationToken);

        if (pendingCandidateData.photoBlob) {
          formData.append("profile_photo", pendingCandidateData.photoBlob, "candidate_photo.jpg");
        }

        const data = await Api.request("/api/auth/register", {
          method: "POST",
          headers: {
            "X-Verification-Token": currentVerificationToken
          },
          body: formData
        });

        Api.setToken(data.token);
        Api.setUser(data.user);

        if (data.candidate_id) {
          if (issuedCidSpan) issuedCidSpan.textContent = data.candidate_id;
          if (successModal) {
            successModal.classList.add("open");
          } else {
            showToast(`Registration successful! Candidate ID: ${data.candidate_id}`, "success");
            setTimeout(() => { window.location.href = "dashboard.html"; }, 1200);
          }
        } else {
          showToast("Registration successful! Account created.", "success");
          setTimeout(() => { window.location.href = "dashboard.html"; }, 800);
        }

      } catch (err) {
        showToast(err.message || "Registration failed. Please try again.", "error");
        switchStep(stepSuccess, stepForm);
      }
    }
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

