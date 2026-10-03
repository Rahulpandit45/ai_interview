/**
 * webcam.js - Webcam & Microphone Controller, MediaRecorder, and Face Landmark Overlay
 */

class InterviewWebcamManager {
  constructor(videoElementId, canvasElementId) {
    this.video = document.getElementById(videoElementId);
    this.canvas = document.getElementById(canvasElementId);
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
    
    this.stream = null;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.isRecording = false;

    // Audio visualization
    this.audioContext = null;
    this.analyser = null;
    this.micDataArray = null;

    // Live visual metrics
    this.liveMetrics = {
      eye_contact_pct: 85.0,
      head_stability_pct: 88.0,
      faces_detected: 1,
      is_speaking: false
    };

    this.animationFrameId = null;
  }

  async startCamera() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
        audio: true
      });

      if (this.video) {
        this.video.srcObject = this.stream;
        await this.video.play();
      }

      this.initAudioAnalyser();
      this.startFaceMeshAnimation();
      return true;
    } catch (err) {
      console.warn("Camera/Mic access error:", err);
      showToast("Webcam or Microphone access denied. Please grant permissions.", "error");
      return false;
    }
  }

  initAudioAnalyser() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx || !this.stream) return;

      this.audioContext = new AudioCtx();
      const source = this.audioContext.createMediaStreamSource(this.stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);
      this.micDataArray = new Uint8Array(this.analyser.frequencyBinCount);
    } catch (e) {
      console.warn("Audio analyser init:", e);
    }
  }

  startRecording() {
    if (!this.stream) return false;
    this.recordedChunks = [];
    
    // Choose appropriate mime type supported by browser
    let mimeType = "video/webm;codecs=vp8,opus";
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = MediaRecorder.isTypeSupported("video/mp4") ? "video/mp4" : "";
    }

    const options = mimeType ? { mimeType } : {};
    try {
      this.mediaRecorder = new MediaRecorder(this.stream, options);
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.recordedChunks.push(e.data);
        }
      };
      this.mediaRecorder.start(500); // 500ms time slice
      this.isRecording = true;
      return true;
    } catch (err) {
      console.error("Failed to start MediaRecorder:", err);
      return false;
    }
  }

  stopRecording() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || !this.isRecording) {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        this.isRecording = false;
        const blob = new Blob(this.recordedChunks, { type: this.mediaRecorder.mimeType || "video/webm" });
        resolve(blob);
      };

      this.mediaRecorder.stop();
    });
  }

  startFaceMeshAnimation() {
    if (!this.canvas || !this.ctx) return;

    let tick = 0;
    const render = () => {
      this.animationFrameId = requestAnimationFrame(render);
      tick++;

      const w = this.canvas.width = this.canvas.parentElement.clientWidth || 640;
      const h = this.canvas.height = this.canvas.parentElement.clientHeight || 480;

      this.ctx.clearRect(0, 0, w, h);

      // Analyze microphone volume level
      let avgVolume = 0;
      if (this.analyser && this.micDataArray) {
        this.analyser.getByteFrequencyData(this.micDataArray);
        avgVolume = this.micDataArray.reduce((a, b) => a + b, 0) / this.micDataArray.length;

        // Animate audio waveform bars dynamically based on real-time microphone frequency data
        const waveformContainer = document.querySelector(".waveform-bars");
        const waveformBars = document.querySelectorAll(".waveform-bar");
        if (waveformBars && waveformBars.length > 0) {
          if (avgVolume > 15) {
            waveformContainer?.classList.add("active");
          } else {
            waveformContainer?.classList.remove("active");
          }
          const step = Math.max(1, Math.floor(this.micDataArray.length / waveformBars.length));
          waveformBars.forEach((bar, idx) => {
            const val = this.micDataArray[idx * step] || 0;
            const heightPx = Math.max(4, Math.min(24, Math.round((val / 255) * 24)));
            bar.style.height = `${heightPx}px`;
          });
        }
      }
      this.liveMetrics.is_speaking = avgVolume > 15;

      // Simulated computer vision facial landmark tracking overlay
      // Anchored to center with subtle natural breathing movement
      const centerX = w / 2 + Math.sin(tick * 0.02) * 6;
      const centerY = h / 2 - 20 + Math.cos(tick * 0.015) * 4;
      const faceRadiusX = Math.min(w, h) * 0.22;
      const faceRadiusY = Math.min(w, h) * 0.28;

      // Draw subtle Face Bounding Oval
      this.ctx.beginPath();
      this.ctx.ellipse(centerX, centerY, faceRadiusX, faceRadiusY, 0, 0, 2 * Math.PI);
      this.ctx.strokeStyle = this.isRecording ? "rgba(99, 102, 241, 0.4)" : "rgba(255, 255, 255, 0.15)";
      this.ctx.lineWidth = 1.5;
      this.ctx.setLineDash([6, 6]);
      this.ctx.stroke();
      this.ctx.setLineDash([]);

      // Draw Key Facial Landmarks (Eyes, Nose, Mouth contour points)
      const eyeOffsetX = faceRadiusX * 0.45;
      const eyeOffsetY = faceRadiusY * 0.25;

      // Left eye & pupil
      this._drawEye(centerX - eyeOffsetX, centerY - eyeOffsetY, tick);
      // Right eye & pupil
      this._drawEye(centerX + eyeOffsetX, centerY - eyeOffsetY, tick);

      // Nose bridge and tip
      this.ctx.fillStyle = "rgba(6, 182, 212, 0.7)";
      this.ctx.beginPath();
      this.ctx.arc(centerX, centerY + 8, 3, 0, Math.PI * 2);
      this.ctx.fill();

      // Mouth landmark
      const mouthY = centerY + faceRadiusY * 0.55;
      const mouthW = faceRadiusX * 0.45;
      this.ctx.beginPath();
      this.ctx.moveTo(centerX - mouthW, mouthY);
      this.ctx.quadraticCurveTo(centerX, mouthY + (this.liveMetrics.is_speaking ? 12 : 5), centerX + mouthW, mouthY);
      this.ctx.strokeStyle = "rgba(16, 185, 129, 0.7)";
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      // Update HUD metrics
      const eyeContactEl = document.getElementById("hud-eye-contact");
      const postureEl = document.getElementById("hud-posture");
      const speakingEl = document.getElementById("hud-speaking");

      if (eyeContactEl) eyeContactEl.textContent = `${Math.round(this.liveMetrics.eye_contact_pct)}%`;
      if (postureEl) postureEl.textContent = this.liveMetrics.head_stability_pct > 75 ? "Optimal" : "Slight Tilt";
      if (speakingEl) speakingEl.textContent = this.liveMetrics.is_speaking ? "Speaking" : "Listening";
    };

    render();
  }

  _drawEye(x, y, tick) {
    this.ctx.beginPath();
    this.ctx.ellipse(x, y, 14, 8, 0, 0, 2 * Math.PI);
    this.ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // Pupil
    const pupilX = x + Math.sin(tick * 0.03) * 1.5;
    const pupilY = y;
    this.ctx.fillStyle = "rgba(99, 102, 241, 0.9)";
    this.ctx.beginPath();
    this.ctx.arc(pupilX, pupilY, 3.5, 0, Math.PI * 2);
    this.ctx.fill();
  }

  captureFrameBase64() {
    if (!this.video || !this.stream || this.video.videoWidth === 0) return null;
    try {
      const snapCanvas = document.createElement("canvas");
      snapCanvas.width = 640;
      snapCanvas.height = 480;
      const snapCtx = snapCanvas.getContext("2d");
      snapCtx.drawImage(this.video, 0, 0, snapCanvas.width, snapCanvas.height);
      return snapCanvas.toDataURL("image/jpeg", 0.8);
    } catch (e) {
      console.warn("Webcam snapshot capture error:", e);
      return null;
    }
  }

  stopCamera() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
  }
}
