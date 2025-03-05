let grid = [];
const rows = 50, cols = 50;
let cellSize = 10;
let socket = io();

function setup() {
    let canvas = createCanvas(cols * cellSize, rows * cellSize);
    canvas.parent('canvas-container');
    noStroke();
}

function draw() {
    background(255);
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            fill(grid[y][x] === 1 ? 'black' : 'white');
            rect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }
}

socket.on('update_grid', function(data) {
    grid = data.grid;
    redraw();
});

// Controla el slider de temperatura
document.getElementById('temperatureSlider').addEventListener('input', function(event) {
    let temp = parseFloat(event.target.value);
    socket.emit('change_temperature', { temperature: temp });
});

function restartSimulation() {
    socket.emit('restart');
}

let isPaused = false;  // Estado de la simulación

function togglePause() {
    isPaused = !isPaused;
    socket.emit('toggle_pause');  // Enviar evento al servidor
    document.getElementById("pause-btn").innerText = isPaused ? "Reanudar" : "Pausa";
}

// Escuchar cambios desde el servidor
socket.on("pause_state", (data) => {
    isPaused = data.paused;
    document.getElementById("pause-btn").innerText = isPaused ? "Reanudar" : "Pausa";
});
