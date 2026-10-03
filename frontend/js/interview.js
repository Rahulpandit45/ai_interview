/**
 * interview.js - Interactive Interview Room Coordinator
 */

document.addEventListener("DOMContentLoaded", async () => {
  requireAuth();

  const user = Api.getUser();
  const urlParams = new URLSearchParams(window.location.search);
  const targetRole = urlParams.get("role") || user?.target_role || "Software Engineer";

  // Elements
  const questionNumberEl = document.getElementById("question-number");
  const questionCategoryEl = document.getElementById("question-category");
  const questionTextEl = document.getElementById("question-text");
  const questionCounterEl = document.getElementById("question-counter");
  const timerBadgeEl = document.getElementById("timer-badge");
  const recIndicatorEl = document.getElementById("rec-indicator");
  const transcriptPreviewEl = document.getElementById("live-transcript-preview");
  
  const startBtn = document.getElementById("btn-start-interview");
  const nextBtn = document.getElementById("btn-next-question");
  const finishBtn = document.getElementById("btn-finish-interview");
  const speakQuestionBtn = document.getElementById("btn-speak-question");
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingStatusText = document.getElementById("loading-status-text");

  // State
  let webcamManager = new InterviewWebcamManager("webcam-video", "webcam-canvas");
  let interviewId = null;
  let questions = [];
  let currentQuestionIndex = 0;
  let timerInterval = null;
  let secondsRemaining = 60;
  let liveTranscript = "";
  let speechRecognizer = null;

  // AI Proctoring Multi-Person Detection State
  let proctoringInterval = null;
  let isInterviewTerminated = false;
  const proctorAlertBanner = document.getElementById("proctor-alert-banner");
  const proctorAlertIcon = document.getElementById("proctor-alert-icon");
  const proctorAlertText = document.getElementById("proctor-alert-text");
  const proctorAlertTimer = document.getElementById("proctor-alert-timer");
  const proctorTerminationModal = document.getElementById("proctor-termination-modal");
  const proctorTerminationMsg = document.getElementById("proctor-termination-message");
  const hudFacesText = document.getElementById("hud-faces-text");
  const hudFacesDot = document.getElementById("hud-faces-dot");

  // Initialize Speech Recognition if supported in browser
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = true;
    speechRecognizer.interimResults = true;
    speechRecognizer.lang = "en-US";

    speechRecognizer.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          liveTranscript += event.results[i][0].transcript + " ";
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      if (transcriptPreviewEl) {
        transcriptPreviewEl.textContent = (liveTranscript + interim) || "Listening to your response...";
      }
    };
  }

  // Camera start
  await webcamManager.startCamera();

  // TTS Read Question Aloud
  function speakQuestion(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }

  if (speakQuestionBtn) {
    speakQuestionBtn.addEventListener("click", () => {
      if (questions[currentQuestionIndex]) {
        speakQuestion(questions[currentQuestionIndex].question_text);
      }
    });
  }

  function showSecurityBlockModal(message) {
    const modal = document.getElementById("security-block-modal");
    const msgEl = document.getElementById("security-block-message");
    if (modal) {
      if (msgEl && message) msgEl.textContent = message;
      modal.style.display = "flex";
    }
  }

  // Pre-flight security check: ensure candidate has a verified CV matching registered name
  async function checkCandidateCvStatus() {
    try {
      const res = await Api.request("/api/resume/parsed");
      if (res && res.resume) {
        if (!res.resume.is_verified) {
          showSecurityBlockModal("Your registered name does not match the name on your CV. Please upload the correct CV.");
          if (startBtn) startBtn.disabled = true;
        }
      }
    } catch (e) {
      showSecurityBlockModal("No CV uploaded. Please upload your CV before starting the interview.");
      if (startBtn) startBtn.disabled = true;
    }
  }
  checkCandidateCvStatus();

  // Start Interview Clicked
  startBtn.addEventListener("click", async () => {
    try {
      startBtn.disabled = true;
      startBtn.textContent = "Initiating Session...";

      const res = await Api.request("/api/interview/start", {
        method: "POST",
        body: JSON.stringify({ target_role: targetRole })
      });

      interviewId = res.data.interview_id;
      questions = res.data.questions;
      currentQuestionIndex = 0;

      startBtn.style.display = "none";
      nextBtn.style.display = "inline-flex";

      showToast("Interview session started. Good luck!", "success");
      loadQuestion(0);
      startProctoringMonitor(interviewId);
    } catch (err) {
      const errMsg = err.message || "";
      if (errMsg.includes("does not match the name on your CV") || errMsg.includes("No CV uploaded") || err.code === "CV_VERIFICATION_FAILED" || err.code === "NO_CV") {
        showSecurityBlockModal(errMsg);
      } else {
        showToast(errMsg, "error");
      }
      startBtn.disabled = false;
      startBtn.textContent = "Start Interview";
    }
  });

  function loadQuestion(indexOrObj) {
    let q;
    let index;
    if (typeof indexOrObj === "number") {
      index = indexOrObj;
      if (index >= questions.length) {
        handleInterviewCompletion();
        return;
      }
      q = questions[index];
    } else {
      q = indexOrObj;
      index = q.question_number ? q.question_number - 1 : currentQuestionIndex;
      if (questions.length <= index) {
        questions.push(q);
      } else {
        questions[index] = q;
      }
    }

    currentQuestionIndex = index;
    const totalCount = q.total_questions || questions.length || 10;

    if (questionNumberEl) questionNumberEl.textContent = `Question ${index + 1} of ${totalCount}`;
    if (questionCategoryEl) questionCategoryEl.textContent = (q.category || q.topic || "IT").toUpperCase();
    if (questionTextEl) questionTextEl.textContent = q.question_text || q.question;
    if (questionCounterEl) questionCounterEl.textContent = `${index + 1}/${totalCount}`;

    const difficultyEl = document.getElementById("question-difficulty");
    const diff = (q.difficulty || "easy").toLowerCase();
    if (difficultyEl) {
      if (diff === "easy") {
        difficultyEl.textContent = "🟢 EASY";
        difficultyEl.style.background = "rgba(16, 185, 129, 0.15)";
        difficultyEl.style.color = "#10b981";
        difficultyEl.style.borderColor = "rgba(16, 185, 129, 0.35)";
      } else if (diff === "medium") {
        difficultyEl.textContent = "🟡 MEDIUM";
        difficultyEl.style.background = "rgba(245, 158, 11, 0.15)";
        difficultyEl.style.color = "#f59e0b";
        difficultyEl.style.borderColor = "rgba(245, 158, 11, 0.35)";
      } else {
        difficultyEl.textContent = "🔴 HARD";
        difficultyEl.style.background = "rgba(244, 63, 94, 0.15)";
        difficultyEl.style.color = "#f43f5e";
        difficultyEl.style.borderColor = "rgba(244, 63, 94, 0.35)";
      }
    }

    // Dynamically render & update Progression Roadmap container for up to 10 stages
    const roadmapContainer = document.getElementById("progression-roadmap");
    if (roadmapContainer) {
      let existingSteps = roadmapContainer.querySelectorAll(".roadmap-step");
      if (existingSteps.length !== totalCount) {
        roadmapContainer.innerHTML = "";
        for (let i = 0; i < totalCount; i++) {
          if (i > 0) {
            const arrow = document.createElement("span");
            arrow.className = "roadmap-arrow";
            arrow.textContent = "➔";
            roadmapContainer.appendChild(arrow);
          }
          const stepDiv = document.createElement("div");
          stepDiv.id = `step-${i + 1}`;
          const defaultTier = i < 2 ? "easy" : (i < 6 ? "medium" : "hard");
          const icon = defaultTier === "easy" ? "🟢" : (defaultTier === "medium" ? "🟡" : "🔴");
          stepDiv.className = `roadmap-step ${defaultTier}`;
          stepDiv.innerHTML = `<span>${icon} Q${i + 1}</span>`;
          roadmapContainer.appendChild(stepDiv);
        }
      }

      const roadmapSteps = roadmapContainer.querySelectorAll(".roadmap-step");
      roadmapSteps.forEach((stepEl, idx) => {
        stepEl.classList.remove("active", "completed");
        if (idx === index) {
          stepEl.classList.add("active");
          stepEl.classList.remove("easy", "medium", "hard");
          stepEl.classList.add(diff);
          const icon = diff === "easy" ? "🟢" : (diff === "medium" ? "🟡" : "🔴");
          const diffLabel = diff.charAt(0).toUpperCase() + diff.slice(1);
          const catShort = (q.category || q.topic || 'Skill').split(' ')[0];
          stepEl.innerHTML = `<span>${icon} Q${index + 1}: ${catShort} (${diffLabel})</span>`;
        } else if (idx < index) {
          stepEl.classList.add("completed");
        }
      });
    }

    const roadmapStatusEl = document.getElementById("roadmap-current-status");
    if (roadmapStatusEl) {
      const diffUpper = diff.toUpperCase();
      const followUpBadge = q.is_follow_up ? " [Follow-Up]" : "";
      roadmapStatusEl.textContent = `Stage ${index + 1}/${totalCount}: ${diffUpper} TIER${followUpBadge}`;
      if (diffUpper === "EASY") roadmapStatusEl.style.color = "#10b981";
      else if (diffUpper === "MEDIUM") roadmapStatusEl.style.color = "#f59e0b";
      else roadmapStatusEl.style.color = "#f43f5e";
    }

    // Update buttons
    if (index >= totalCount - 1) {
      nextBtn.style.display = "none";
      finishBtn.style.display = "inline-flex";
    } else {
      nextBtn.style.display = "inline-flex";
      finishBtn.style.display = "none";
    }

    // Auto-read question using speech synthesis
    speakQuestion(q.question_text || q.question);

    // Reset and start recording response
    liveTranscript = "";
    if (transcriptPreviewEl) transcriptPreviewEl.textContent = "Listening to your response...";
    
    startQuestionTimer();
    webcamManager.startRecording();
    if (speechRecognizer) {
      try { speechRecognizer.start(); } catch (e) {}
    }

    if (recIndicatorEl) recIndicatorEl.style.display = "flex";
  }

  function startQuestionTimer() {
    clearInterval(timerInterval);
    secondsRemaining = 60;
    updateTimerBadge();

    timerInterval = setInterval(() => {
      secondsRemaining--;
      updateTimerBadge();

      if (secondsRemaining <= 0) {
        clearInterval(timerInterval);
        showToast("Time reached for this question. Moving to next.", "info");
        submitCurrentQuestionAndProceed();
      }
    }, 1000);
  }

  function updateTimerBadge() {
    if (!timerBadgeEl) return;
    const mins = Math.floor(secondsRemaining / 60);
    const secs = secondsRemaining % 60;
    timerBadgeEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    
    if (secondsRemaining <= 10) {
      timerBadgeEl.style.borderColor = "var(--accent-rose)";
      timerBadgeEl.style.color = "var(--accent-rose)";
    } else {
      timerBadgeEl.style.borderColor = "rgba(56, 189, 248, 0.3)";
      timerBadgeEl.style.color = "#38bdf8";
    }
  }

  async function fetchNextAdaptiveQuestion(currentQ, transcript) {
    const payload = {
      interview_id: interviewId,
      question_id: currentQ.id || currentQ.question_id || 1,
      answer: transcript || ""
    };

    // Primary: FastAPI backend on port 8000
    try {
      const fastApiUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/interview/next-question`;
      const fRes = await fetch(fastApiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (fRes.ok) {
        return await fRes.json();
      }
    } catch (e) {
      console.warn("FastAPI next-question fallback:", e);
    }

    // Secondary: Flask proxy endpoint
    return await Api.request(`/api/interview/${interviewId}/next-question`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  async function submitCurrentQuestionAndProceed() {
    if (isInterviewTerminated) return;

    clearInterval(timerInterval);
    if (speechRecognizer) {
      try { speechRecognizer.stop(); } catch (e) {}
    }

    const currentQ = questions[currentQuestionIndex];
    const recordedBlob = await webcamManager.stopRecording();
    const candidateAnswerText = liveTranscript.trim();

    // Show temporary submitting status
    if (transcriptPreviewEl) {
      transcriptPreviewEl.textContent = "Analyzing response with Whisper speech model & adaptive NLP engine...";
    }

    const formData = new FormData();
    formData.append("question_id", currentQ.id || currentQ.question_id || 1);
    formData.append("question_text", currentQ.question_text || currentQ.question || "");
    formData.append("benchmark_answer", currentQ.benchmark_answer || "");
    formData.append("transcript", candidateAnswerText);
    formData.append("metrics", JSON.stringify(webcamManager.liveMetrics));

    if (recordedBlob) {
      formData.append("recording", recordedBlob, `interview_${interviewId}_q${currentQ.id || currentQuestionIndex + 1}.webm`);
    }

    try {
      await Api.request(`/api/interview/${interviewId}/response`, {
        method: "POST",
        body: formData
      });
      showToast(`Question ${currentQuestionIndex + 1} response evaluated.`, "success");
    } catch (err) {
      console.warn("Response submission warning:", err);
    }

    // Query Next Adaptive Question based on Candidate's previous response
    let nextStep = null;
    try {
      nextStep = await fetchNextAdaptiveQuestion(currentQ, candidateAnswerText);
    } catch (e) {
      console.warn("Adaptive question fetch error, using local queue fallback:", e);
    }

    if (nextStep && nextStep.is_complete) {
      handleInterviewCompletion();
      return;
    }

    if (nextStep && (nextStep.question || nextStep.question_text)) {
      const formattedNextQ = {
        id: nextStep.question_id || (currentQuestionIndex + 2),
        question_id: nextStep.question_id || (currentQuestionIndex + 2),
        question_number: nextStep.question_number || (currentQuestionIndex + 2),
        total_questions: nextStep.total_questions || questions.length || 5,
        category: nextStep.topic || nextStep.category || "IT",
        difficulty: nextStep.difficulty || "medium",
        difficulty_level: nextStep.difficulty_level || 2,
        question_text: nextStep.question || nextStep.question_text,
        benchmark_answer: nextStep.benchmark_answer || "",
        is_follow_up: nextStep.is_follow_up || false
      };

      loadQuestion(formattedNextQ);
    } else if (currentQuestionIndex + 1 < questions.length) {
      loadQuestion(currentQuestionIndex + 1);
    } else {
      handleInterviewCompletion();
    }
  }

  nextBtn.addEventListener("click", () => {
    submitCurrentQuestionAndProceed();
  });

  finishBtn.addEventListener("click", () => {
    if (typeof showConfirmModal === "function") {
      showConfirmModal({
        title: "Submit Final Assessment?",
        message: "You are about to complete your AI video interview. Your multimodal answers (voice, face posture, and semantic content) will be synthesized to generate your final assessment report.",
        confirmText: "Yes, Finish & View Report",
        cancelText: "Review Answer",
        onConfirm: () => {
          submitCurrentQuestionAndProceed();
        }
      });
    } else {
      submitCurrentQuestionAndProceed();
    }
  });

  async function handleInterviewCompletion() {
    if (proctoringInterval) clearInterval(proctoringInterval);
    clearInterval(timerInterval);
    if (speechRecognizer) {
      try { speechRecognizer.stop(); } catch (e) {}
    }
    webcamManager.stopCamera();

    // Show loading overlay
    if (loadingOverlay) loadingOverlay.style.display = "flex";
    if (loadingStatusText) loadingStatusText.textContent = "Synthesizing Multimodal Features (Text, Audio, Video)...";

    try {
      const res = await Api.request(`/api/interview/${interviewId}/finish`, {
        method: "POST"
      });

      if (loadingStatusText) loadingStatusText.textContent = "Generating Comprehensive AI Assessment Report...";
      
      setTimeout(() => {
        window.location.href = `report.html?interview_id=${interviewId}`;
      }, 1500);
    } catch (err) {
      if (loadingOverlay) loadingOverlay.style.display = "none";
      showToast("Error generating report: " + err.message, "error");
    }
  }

  // =========================================================================
  // AI Proctoring Real-time Multi-Person Monitoring & Enforcement
  // =========================================================================
  function startProctoringMonitor(currentInterviewId) {
    if (proctoringInterval) clearInterval(proctoringInterval);

    proctoringInterval = setInterval(async () => {
      if (isInterviewTerminated || !currentInterviewId) return;

      const frameB64 = webcamManager.captureFrameBase64();
      if (!frameB64) return;

      try {
        const payload = {
          interview_id: currentInterviewId,
          frame_b64: frameB64,
          timestamp: Date.now() / 1000.0
        };

        let result = null;
        // Primary: FastAPI enforcement backend on port 8000
        try {
          const fastApiUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/proctoring/check`;
          const fRes = await fetch(fastApiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          if (fRes.ok) {
            result = await fRes.json();
          }
        } catch (e) {
          // Fallback to Flask proxy if FastAPI is unreachable
          result = await Api.request(`/api/interview/${currentInterviewId}/proctoring-check`, {
            method: "POST",
            body: JSON.stringify(payload)
          });
        }

        if (result) {
          handleProctoringResult(result);
        }
      } catch (err) {
        console.warn("Proctoring monitor tick warning:", err);
      }
    }, 1000); // Check every 1000ms
  }

  function handleProctoringResult(res) {
    if (isInterviewTerminated) return;

    // Update HUD indicator
    const hudFacesPill = document.getElementById("hud-faces-pill");
    if (hudFacesText && hudFacesDot) {
      if (res.faces_detected >= 2) {
        hudFacesText.textContent = `Multiple (${res.faces_detected} Faces)`;
        hudFacesText.style.color = "#f43f5e";
        hudFacesDot.style.background = "#f43f5e";
        if (hudFacesPill) {
          hudFacesPill.style.border = "1px solid rgba(244, 63, 94, 0.7)";
          hudFacesPill.style.boxShadow = "0 0 14px rgba(244, 63, 94, 0.4)";
          hudFacesPill.style.background = "rgba(244, 63, 94, 0.12)";
        }
      } else {
        hudFacesText.textContent = "Alone (1 Face)";
        hudFacesText.style.color = "#10b981";
        hudFacesDot.style.background = "#10b981";
        if (hudFacesPill) {
          hudFacesPill.style.border = "1px solid rgba(255, 255, 255, 0.08)";
          hudFacesPill.style.boxShadow = "none";
          hudFacesPill.style.background = "rgba(15, 23, 42, 0.75)";
        }
      }
    }

    if (res.status === "warning_1") {
      // Warning 1: Yellow/Amber banner with frosted glass effect
      if (proctorAlertBanner) {
        proctorAlertBanner.style.display = "block";
        proctorAlertBanner.style.background = "linear-gradient(135deg, rgba(217, 119, 6, 0.95), rgba(180, 83, 9, 0.95))";
        proctorAlertBanner.style.color = "#ffffff";
        proctorAlertBanner.style.border = "1.5px solid #fbbf24";
        proctorAlertBanner.style.boxShadow = "0 8px 32px rgba(245, 158, 11, 0.35)";
        if (proctorAlertIcon) proctorAlertIcon.textContent = "⚠️";
        if (proctorAlertText) {
          proctorAlertText.innerHTML = `<strong>Warning 1: Another person has been detected.</strong><br><span style="font-size: 0.82rem; opacity: 0.95;">Please ensure you are alone during the interview.</span>`;
        }
        if (proctorAlertTimer) proctorAlertTimer.style.display = "none";
      }
    } else if (res.status === "final_warning") {
      // Final Warning: Rose/Red banner with countdown
      if (proctorAlertBanner) {
        proctorAlertBanner.style.display = "block";
        proctorAlertBanner.style.background = "linear-gradient(135deg, rgba(225, 29, 72, 0.95), rgba(190, 18, 60, 0.95))";
        proctorAlertBanner.style.color = "#ffffff";
        proctorAlertBanner.style.border = "2px solid #f43f5e";
        proctorAlertBanner.style.boxShadow = "0 8px 32px rgba(244, 63, 94, 0.45)";
        if (proctorAlertIcon) proctorAlertIcon.textContent = "⚠️";
        if (proctorAlertText) {
          proctorAlertText.innerHTML = `<strong>Final Warning: Another person has been detected again!</strong><br><span style="font-size: 0.82rem; opacity: 0.95;">Session will terminate automatically if not alone.</span>`;
        }
        if (proctorAlertTimer) {
          proctorAlertTimer.style.display = "inline-block";
          proctorAlertTimer.textContent = `${Math.ceil(res.remaining_seconds || 10)}s`;
        }
      }
    } else if (res.status === "warning_cleared" || res.status === "clean") {
      // Clear warning banner
      if (proctorAlertBanner) {
        proctorAlertBanner.style.display = "none";
      }
    }

    // Check for Termination
    if (res.status === "terminated" || res.is_terminated) {
      terminateInterviewDueToViolation(res.message);
    }
  }

  function terminateInterviewDueToViolation(message) {
    if (isInterviewTerminated) return;
    isInterviewTerminated = true;

    if (proctoringInterval) clearInterval(proctoringInterval);
    if (timerInterval) clearInterval(timerInterval);
    if (speechRecognizer) {
      try { speechRecognizer.stop(); } catch (e) {}
    }
    webcamManager.stopCamera();

    if (proctorAlertBanner) proctorAlertBanner.style.display = "none";

    // Disable all progression controls
    if (nextBtn) nextBtn.style.display = "none";
    if (finishBtn) finishBtn.style.display = "none";
    if (startBtn) startBtn.style.display = "none";

    // Show Termination Modal
    if (proctorTerminationModal) {
      if (proctorTerminationMsg && message) {
        proctorTerminationMsg.textContent = message;
      }
      proctorTerminationModal.style.display = "flex";
    }
    showToast("Interview Terminated: Another person remained present after the final warning.", "error");
  }
});
