// Periodically fetch telemetry from Python vision engine
const earEl = document.getElementById('val-ear');
const marEl = document.getElementById('val-mar');
const pitchEl = document.getElementById('val-pitch');
const alertBox = document.getElementById('alert-box');
const badge = document.getElementById('driver-badge');
const logBody = document.getElementById('log-body');

let lastState = 'ATTENTIVE';

function playWebBeep() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(800, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    } catch(e) {}
}

async function fetchTelemetry() {
    try {
        const res = await fetch('http://localhost:5000/telemetry');
        if (!res.ok) return;
        const data = await res.json();

        earEl.textContent = data.ear.toFixed(2);
        marEl.textContent = data.mar.toFixed(2);
        pitchEl.textContent = data.pitch.toFixed(1) + '°';

        if (data.drowsy) {
            alertBox.style.background = '#7f1d1d';
            alertBox.style.borderColor = '#ef4444';
            alertBox.style.color = '#fca5a5';
            alertBox.textContent = 'CRITICAL WARNING: DROWSINESS / MICROSLEEP DETECTED!';
            badge.style.background = '#ef4444';
            badge.textContent = 'DROWSY';
            playWebBeep();

            if (lastState !== 'DROWSY') {
                addLog('MICROSLEEP', 'CRITICAL', '2.0s');
                lastState = 'DROWSY';
            }
        } else if (data.distracted) {
            alertBox.style.background = '#7c2d12';
            alertBox.style.borderColor = '#f97316';
            alertBox.style.color = '#fed7aa';
            alertBox.textContent = 'WARNING: DRIVER DISTRACTED (HEAD TILT / PHONE)!';
            badge.style.background = '#f97316';
            badge.textContent = 'DISTRACTED';

            if (lastState !== 'DISTRACTED') {
                addLog('DISTRACTION', 'WARNING', '1.5s');
                lastState = 'DISTRACTED';
            }
        } else if (data.yawning) {
            alertBox.style.background = '#713f12';
            alertBox.style.borderColor = '#eab308';
            alertBox.style.color = '#fef08a';
            alertBox.textContent = 'WARNING: FREQUENT YAWNING DETECTED';
            badge.style.background = '#eab308';
            badge.textContent = 'YAWNING';

            if (lastState !== 'YAWNING') {
                addLog('YAWN', 'WARNING', '3.0s');
                lastState = 'YAWNING';
            }
        } else {
            alertBox.style.background = '#064e3b';
            alertBox.style.borderColor = '#059669';
            alertBox.style.color = '#6ee7b7';
            alertBox.textContent = 'STATE: ATTENTIVE (SAFE TO DRIVE)';
            badge.style.background = '#10b981';
            badge.textContent = 'ATTENTIVE';
            lastState = 'ATTENTIVE';
        }
    } catch(err) {
        // Python server not yet started
    }
}

function addLog(type, sev, dur) {
    const tr = document.createElement('tr');
    const now = new Date().toLocaleTimeString();
    const badgeClass = sev === 'CRITICAL' ? 'critical' : 'warning';
    tr.innerHTML = `<td>${now}</td><td>${type}</td><td><span class="badge ${badgeClass}">${sev}</span></td><td>${dur}</td>`;
    logBody.insertBefore(tr, logBody.firstChild);
}

setInterval(fetchTelemetry, 150);
