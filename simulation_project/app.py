from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Configuración inicial de la simulación
grid_size = (50, 50)
temperature = 2.0  # Parámetro del modelo de Ising
grid = np.random.choice([-1, 1], size=grid_size)  # Estado inicial: -1 o 1

paused = False  # Estado de la simulación

def metropolis_step():
    """Aplica la regla de actualización del modelo de Ising."""
    global grid
    for _ in range(1000):  # 1000 iteraciones por frame
        i, j = np.random.randint(0, grid_size[0]), np.random.randint(0, grid_size[1])
        spin = grid[i, j]
        neighbors = (
            grid[(i + 1) % grid_size[0], j]
            + grid[(i - 1) % grid_size[0], j]
            + grid[i, (j + 1) % grid_size[1]]
            + grid[i, (j - 1) % grid_size[1]]
        )
        delta_E = 2 * spin * neighbors
        if delta_E < 0 or np.random.rand() < np.exp(-delta_E / temperature):
            grid[i, j] *= -1  # Cambio de estado

def update_simulation():
    """Genera la evolución del sistema y la envía en tiempo real."""
    global paused
    while True:
        if not paused:  # Solo actualizar cuando no esté en pausa
            metropolis_step()  # Aplica un paso de simulación
            socketio.emit("update_grid", {"grid": grid.tolist()})
        time.sleep(0.1)  # Cada 100ms

@socketio.on("connect")
def on_connect():
    """Inicia la simulación cuando un cliente se conecta."""
    socketio.start_background_task(update_simulation)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("change_temperature")
def change_temperature(data):
    """Cambia la temperatura del sistema en tiempo real."""
    global temperature
    temperature = float(data["temperature"])

@socketio.on("restart")
def restart_simulation():
    """Reinicia la simulación con un nuevo estado inicial aleatorio."""
    global grid
    grid = np.random.choice([-1, 1], size=grid_size)  # Nueva matriz aleatoria
    socketio.emit("update_grid", {"grid": grid.tolist()})  # Enviar nuevo estado

@socketio.on("toggle_pause")
def toggle_pause():
    """Activa o desactiva la pausa de la simulación."""
    global paused
    paused = not paused
    socketio.emit("pause_state", {"paused": paused})  # Enviar estado actual

if __name__ == "__main__":
    socketio.run(app, debug=True)
