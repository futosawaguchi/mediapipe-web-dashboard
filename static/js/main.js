// static/js/main.js - SocketIO通信・UI制御

const socket = io();

// 状態管理
let landmarkVisible = true;
let faceEnabled     = true;
let arrowEnabled    = false;

// 矢印キャンバス
const arrowCanvas = document.getElementById("arrow-canvas");
const ctx         = arrowCanvas.getContext("2d");

// キャンバスサイズをvideo-wrapperに合わせる
function resizeCanvas() {
    arrowCanvas.width  = arrowCanvas.offsetWidth;
    arrowCanvas.height = arrowCanvas.offsetHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

// ===== SocketIO イベント =====

socket.on("connect", () => setStatus(true));
socket.on("disconnect", () => setStatus(false));

socket.on("status", (data) => {
    updateGesture(data.gesture);
    updateOrientation(data.orientation);
    updateDirection(data.direction);
    if (arrowEnabled) drawArrow(data.direction);

    landmarkVisible = data.landmark_visible;
    faceEnabled     = data.face_enabled;
    syncToggleUI();
});

// ===== UI更新 =====

function updateGesture(gesture) {
    const el = document.getElementById("gesture-display");
    el.innerHTML = gesture
        ? `<span>${gesture}</span>`
        : `<span class="gesture-waiting">手をかざしてください</span>`;
}

function updateOrientation(orientation) {
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

function updateDirection(direction) {
    if (!direction) {
        document.getElementById("val-h").textContent = "—";
        document.getElementById("val-v").textContent = "—";
        document.getElementById("val-d").textContent = "—";
        return;
    }
    document.getElementById("val-h").textContent = formatDeg(direction.horizontal);
    document.getElementById("val-v").textContent = formatDeg(direction.vertical);
    document.getElementById("val-d").textContent = formatDeg(direction.depth);
}

function formatDeg(val) {
    return (val >= 0 ? "+" : "") + val.toFixed(1);
}

function setStatus(connected) {
    const dot  = document.getElementById("status-dot");
    const text = document.getElementById("status-text");
    dot.classList.toggle("connected", connected);
    text.textContent = connected ? "connected" : "disconnected";
}

function syncToggleUI() {
    document.getElementById("btn-landmark").classList.toggle("active", landmarkVisible);
    document.getElementById("btn-face").classList.toggle("active", faceEnabled);
    document.getElementById("btn-arrow").classList.toggle("active", arrowEnabled);

    document.getElementById("orientation-panel").classList.toggle("active", faceEnabled);
}

// ===== 矢印描画 =====

function drawArrow(direction) {
    resizeCanvas();
    ctx.clearRect(0, 0, arrowCanvas.width, arrowCanvas.height);

    if (!direction) return;

    const cx = arrowCanvas.width  / 2;
    const cy = arrowCanvas.height / 2;
    const len = Math.min(arrowCanvas.width, arrowCanvas.height) * 0.3;

    // dx・dyは正規化済みベクトル（画像座標系なのでdyは反転不要）
    const ex = cx + direction.dx * len;
    const ey = cy + direction.dy * len;

    // 矢印の線
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(ex, ey);
    ctx.strokeStyle = "rgba(255, 200, 50, 0.9)";
    ctx.lineWidth   = 4;
    ctx.lineCap     = "round";
    ctx.stroke();

    // 矢印の先端
    const angle  = Math.atan2(ey - cy, ex - cx);
    const headLen = 20;
    ctx.beginPath();
    ctx.moveTo(ex, ey);
    ctx.lineTo(
        ex - headLen * Math.cos(angle - Math.PI / 6),
        ey - headLen * Math.sin(angle - Math.PI / 6)
    );
    ctx.moveTo(ex, ey);
    ctx.lineTo(
        ex - headLen * Math.cos(angle + Math.PI / 6),
        ey - headLen * Math.sin(angle + Math.PI / 6)
    );
    ctx.strokeStyle = "rgba(255, 200, 50, 0.9)";
    ctx.lineWidth   = 3;
    ctx.lineCap     = "round";
    ctx.stroke();

    // 中心点
    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255, 200, 50, 0.9)";
    ctx.fill();
}

function clearArrow() {
    ctx.clearRect(0, 0, arrowCanvas.width, arrowCanvas.height);
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

function toggleArrow() {
    arrowEnabled = !arrowEnabled;
    arrowCanvas.classList.toggle("active", arrowEnabled);
    document.getElementById("btn-arrow").classList.toggle("active", arrowEnabled);
    if (!arrowEnabled) clearArrow();
}