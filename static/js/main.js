let currentGameMode = null;
let timerInterval = null;
let currentWord = null;
let timerDuration = 60;

document.addEventListener('DOMContentLoaded', () => {
    loadScores();
    updateTimerDisplay(timerDuration);
});

function toggleSelectionMethod(method) {
    const wheelView = document.getElementById('wheel-view');
    const manualView = document.getElementById('manual-view');
    
    if (method === 'wheel') {
        wheelView.classList.remove('hidden');
        manualView.classList.add('hidden');
    } else {
        wheelView.classList.add('hidden');
        manualView.classList.remove('hidden');
    }
}

function spinWheel() {
    const wheel = document.getElementById('wheel');
    // Random rotation between 5 and 10 full circles + random offset
    const rotation = 1800 + Math.floor(Math.random() * 360); 
    wheel.style.transform = `rotate(${rotation}deg)`;
    
    // Disable button during spin
    const btn = document.querySelector('button[onclick="spinWheel()"]');
    btn.disabled = true;

    setTimeout(() => {
        // Determine result based on rotation
        // Normalize rotation to 0-360
        const degrees = rotation % 360;
        // Pictionary is 0-180 (orange), Mimic is 180-360 (purple)
        // Note: The wheel css conic gradient starts at 0 (top? no, 0 is usually top or right depending on browser, 
        // but css gradient 0deg is top).
        // Let's simplify: if degrees < 180, it's one, else other.
        // Actually, let's just randomize the logic in JS for simplicity as visuals are just for show
        const result = Math.random() < 0.5 ? 'pictionary' : 'mimic';
        
        selectMode(result);
        
        // Reset wheel for next time (remove transition to reset instantly if needed, but here we just leave it)
        // wheel.style.transition = 'none';
        // wheel.style.transform = 'rotate(0deg)';
        
        btn.disabled = false;
    }, 3000);
}

function selectMode(mode) {
    currentGameMode = mode;
    const selectionArea = document.getElementById('selection-area');
    const gameArea = document.getElementById('game-area');
    const modeDisplay = document.getElementById('game-mode-display');
    
    selectionArea.classList.add('hidden');
    gameArea.classList.remove('hidden');
    
    const modeText = mode === 'pictionary' ? "🎨 DIBUJAR" : "🎭 MÍMICA";
    modeDisplay.innerHTML = `<h2>Modo actual: ${modeText}</h2>`;
    modeDisplay.style.background = mode === 'pictionary' ? 'rgba(255, 102, 0, 0.2)' : 'rgba(102, 0, 204, 0.2)';
    
    // Clear previous word
    document.querySelector('#word-container span').textContent = 'Haz clic en "Generar Palabra"';
    stopTimer();
}

function resetGameSelection() {
    document.getElementById('selection-area').classList.remove('hidden');
    document.getElementById('game-area').classList.add('hidden');
    currentGameMode = null;
    stopTimer();
}

async function generateWord() {
    if (!currentGameMode) return;
    
    try {
        const response = await fetch(`/api/words/${currentGameMode}`);
        const data = await response.json();
        
        if (data.word) {
            currentWord = data.word;
            document.querySelector('#word-container span').textContent = `🎯 ${currentWord.toUpperCase()}`;
            stopTimer(); // Reset timer for new word
        } else {
            alert('Error al obtener palabra');
        }
    } catch (e) {
        console.error(e);
        alert('Error de conexión');
    }
}

function updateTimerDisplay(val) {
    timerDuration = parseInt(val);
    document.getElementById('timer-setting-val').textContent = val;
    const minutes = Math.floor(timerDuration / 60);
    const seconds = timerDuration % 60;
    document.getElementById('timer-val').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
    stopTimer();
    let remaining = timerDuration;
    const display = document.getElementById('timer-val');
    const container = document.getElementById('timer-container');
    
    container.classList.remove('hidden');
    
    // Initial display
    updateDisplay(remaining);
    
    timerInterval = setInterval(() => {
        remaining--;
        updateDisplay(remaining);
        
        if (remaining <= 0) {
            stopTimer();
            display.textContent = "¡TIEMPO AGOTADO!";
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
            // Play sound if available
            try {
                document.getElementById('sound-alarm').play();
            } catch(e) {}
        }
    }, 1000);
    
    function updateDisplay(t) {
        const m = Math.floor(t / 60);
        const s = t % 60;
        display.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    // Don't hide container, just stop
}

// Scoreboard functions
async function loadScores() {
    try {
        const response = await fetch('/api/scores');
        const scores = await response.json();
        renderScores(scores);
    } catch (e) {
        console.error(e);
    }
}

function renderScores(scores) {
    const list = document.getElementById('teams-list');
    list.innerHTML = '';
    
    for (const [team, score] of Object.entries(scores)) {
        const div = document.createElement('div');
        div.className = 'scoreboard-item';
        div.innerHTML = `
            <div>
                <strong>${team}</strong>: <span id="score-${team}">${score}</span>
            </div>
            <div class="score-controls">
                <button class="btn score-btn" onclick="updateScore('${team}', -1)">-</button>
                <button class="btn score-btn" onclick="updateScore('${team}', 1)">+</button>
                <button class="btn score-btn btn-danger" onclick="deleteTeam('${team}')" title="Eliminar equipo">×</button>
            </div>
        `;
        list.appendChild(div);
    }
}

async function addTeam() {
    const input = document.getElementById('new-team-name');
    const name = input.value.trim();
    if (!name) return;
    
    try {
        const response = await fetch('/api/teams', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team: name })
        });
        const data = await response.json();
        if (data.success) {
            renderScores(data.scores);
            input.value = '';
        } else {
            alert(data.error);
        }
    } catch (e) {
        console.error(e);
    }
}

async function deleteTeam(name) {
    if (!confirm(`¿Eliminar equipo ${name}?`)) return;
    
    try {
        const response = await fetch('/api/teams', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team: name })
        });
        const data = await response.json();
        if (data.success) {
            renderScores(data.scores);
        }
    } catch (e) {
        console.error(e);
    }
}

async function updateScore(team, change) {
    try {
        // Optimistic update
        const scoreSpan = document.getElementById(`score-${team}`);
        let currentScore = parseInt(scoreSpan.textContent);
        let newScore = Math.max(0, currentScore + change);
        
        // Get current scores first to update properly
        const getRes = await fetch('/api/scores');
        let scores = await getRes.json();
        
        scores[team] = Math.max(0, scores[team] + change);
        
        const response = await fetch('/api/scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scores)
        });
        
        const data = await response.json();
        if (data.success) {
            renderScores(data.scores);
        }
    } catch (e) {
        console.error(e);
    }
}

async function resetScores() {
    if (!confirm('¿Estás seguro de reiniciar todas las puntuaciones?')) return;
    
    try {
        const response = await fetch('/api/reset', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            renderScores(data.scores);
        }
    } catch (e) {
        console.error(e);
    }
}
