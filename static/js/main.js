// static/js/main.js - SocketIO通信・UI制御

const socket = io();

// 状態管理
let landmarkVisible = true;
let faceEnabled = false;

// ===== SocketIO イベント =====

socket.on("connect", () => {
    setStatus(true);
});

socket.on("disconnect", () => {
    setStatus(false);
});

socket.on("status", (data) => {
    updateGesture(data.gesture);
    updateOrientation(data.orientation);

    // サーバー側の状態とUIを同期
    landmarkVisible = data.landmark_visible;
    faceEnabled = data.face_enabled;
    syncToggleUI();
});

// ===== UI更新 =====

function updateGesture(gesture) {
    const el = document.getElementById("gesture-display");
    if (gesture) {
        el.innerHTML = `<span>${gesture}</span>`;
    } else {
        el.innerHTML = `<span class="gesture-waiting">手をかざしてください</span>`;
    }
}

function updateOrientation(orientation) {
    const panel = document.getElementById("orientation-panel");
    if (!faceEnabled || !orientation) {
        document.getElementById("val-yaw").textContent   = "—";
        document.getElementById("val-pitch").textContent = "—";
        document.getElementById("val-roll").textContent  = "—";
        return;
    }
    document.getElementById("val-yaw").textContent   = formatDeg(orientation.yaw);
    document.getElementById("val-pitch").textContent = formatDeg(orientation.pitch);
    document.getElementById("val-roll").textContent  = formatDeg(orientation.roll);
}

function formatDeg(val) {
    return (val >= 0 ? "+" : "") + val.toFixed(1);
}

function setStatus(connected) {
    const dot  = document.getElementById("status-dot");
    const text = document.getElementById("status-text");
    if (connected) {
        dot.classList.add("connected");
        text.textContent = "connected";
    } else {
        dot.classList.remove("connected");
        text.textContent = "disconnected";
    }
}

function syncToggleUI() {
    const btnLandmark = document.getElementById("btn-landmark");
    const btnFace     = document.getElementById("btn-face");
    const panel       = document.getElementById("orientation-panel");

    landmarkVisible
        ? btnLandmark.classList.add("active")
        : btnLandmark.classList.remove("active");

    faceEnabled
        ? btnFace.classList.add("active")
        : btnFace.classList.remove("active");

    faceEnabled
        ? panel.classList.add("active")
        : panel.classList.remove("active");
}

// ===== トグル操作 =====

function toggleLandmark() {
    landmarkVisible = !landmarkVisible;
    socket.emit("toggle_landmark", { visible: landmarkVisible });
}

function toggleFace() {
    faceEnabled = !faceEnabled;
    socket.emit("toggle_face", { enabled: faceEnabled });
}