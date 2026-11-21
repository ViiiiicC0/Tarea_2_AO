import math
import random
import time
from pathlib import Path

import matplotlib.pyplot as plt

def tour_length(points: list[tuple[float, float]], route: list[int]) -> float:
    """Calcula la distancia euclidiana total de un tour cerrado."""
    n = len(route)
    return sum(math.dist(points[route[i]], points[route[(i + 1) % n]]) for i in range(n))

def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    """Invierte el subsegmento route[i..k]."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def simulated_annealing(
    points: list[tuple[float, float]],
    initial_route: list[int],
    schedule_type: str,
    T0: float = 100.0,
    max_iter: int = 5000
) -> tuple[list[int], float, list[float], float]:
    """
    Ejecuta Recocido Simulado usando 2-opt aleatorio como operador de vecindad.
    Retorna: (mejor_ruta, mejor_costo, historial_costos, tiempo_ejecucion)
    """
    t_start = time.perf_counter()
    n = len(initial_route)
    
    current_route = initial_route[:]
    current_cost = tour_length(points, current_route)
    
    best_route = current_route[:]
    best_cost = current_cost
    
    cost_history = [current_cost]

    for t in range(1, max_iter + 1):
        # 1. Calcular temperatura T según el esquema elegido
        if schedule_type == "exponencial":
            T = T0 * (0.9985 ** t)
        elif schedule_type == "lineal":
            T = max(0.01, T0 * (1.0 - t / max_iter))
        elif schedule_type == "logaritmico":
            T = T0 / (1.0 + 1.5 * math.log(1 + t))
        else:
            raise ValueError("Esquema no reconocido")

        # Si la temperatura llega prácticamente a cero, detenemos
        if T <= 1e-4:
            break

        # 2. Generar un vecino 2-opt ALEATORIO (elegir dos índices de corte i < k al azar)
        i, k = sorted(random.sample(range(1, n), 2))
        candidate_route = two_opt_move(current_route, i, k)
        candidate_cost = tour_length(points, candidate_route)

        # 3. Criterio de aceptación de Metropolis
        delta = candidate_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_route = candidate_route
            current_cost = candidate_cost
            
            # Guardar el récord histórico global encontrado hasta el momento
            if current_cost < best_cost:
                best_route = current_route[:]
                best_cost = current_cost

        cost_history.append(current_cost)

    elapsed = time.perf_counter() - t_start
    return best_route, best_cost, cost_history, elapsed


if __name__ == "__main__":
    # Mapa fijo de 25 ciudades
    random.seed(42)
    num_cities = 25
    cities = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_cities)]

    # Misma ruta inicial aleatoria para que la comparación sea justa
    base_route = list(range(num_cities))
    random.shuffle(base_route)
    initial_cost = tour_length(cities, base_route)
    print(f"Costo inicial aleatorio: {initial_cost:.2f}\n")

    schedules = ["exponencial", "lineal", "logaritmico"]
    histories = {}
    final_costs = []
    exec_times = []

    # Ejecutamos 15 corridas por esquema para obtener promedios estables de tiempo y calidad
    runs = 15
    for sched in schedules:
        costs_runs = []
        times_runs = []
        for r in range(runs):
            random.seed(100 + r)
            _, b_cost, hist, t_elap = simulated_annealing(cities, base_route, sched, T0=50.0, max_iter=6000)
            costs_runs.append(b_cost)
            times_runs.append(t_elap * 1000)  # Convertir a milisegundos
            if r == 0:
                histories[sched] = hist  # Guardamos la primera curva para graficar convergencia

        avg_cost = sum(costs_runs) / runs
        avg_time = sum(times_runs) / runs
        final_costs.append(avg_cost)
        exec_times.append(avg_time)
        print(f"Esquema {sched:<12} -> Costo Final Promedio: {avg_cost:.2f} | Tiempo Promedio: {avg_time:.2f} ms")

    # --- GRÁFICA 1: Curvas de Convergencia (Costo vs Iteraciones) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    colors = {'exponencial': 'royalblue', 'lineal': 'darkorange', 'logaritmico': 'seagreen'}
    for sched in schedules:
        ax1.plot(histories[sched], label=f'Enfriamiento {sched.capitalize()}', color=colors[sched], alpha=0.85, linewidth=1.3)

    ax1.set_title('Curvas de Convergencia (Costo vs. Iteraciones)')
    ax1.set_xlabel('Iteración ($t$)')
    ax1.set_ylabel('Costo del Tour Actual')
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.7)

    # --- GRÁFICA 2: Tiempo de Ejecución vs Calidad de la Solución Final ---
    for idx, sched in enumerate(schedules):
        ax2.scatter(exec_times[idx], final_costs[idx], color=colors[sched], s=150, zorder=5, label=sched.capitalize())
        ax2.annotate(f"{sched.capitalize()}\n({exec_times[idx]:.1f} ms, {final_costs[idx]:.1f})",
                     (exec_times[idx], final_costs[idx]),
                     textcoords="offset points", xytext=(0, 12), ha='center', fontweight='bold')

    ax2.set_title('Tiempo de Ejecución vs. Calidad Final (Promedio)')
    ax2.set_xlabel('Tiempo de Cómputo Promedio (ms)')
    ax2.set_ylabel('Costo Final del Tour (menor es mejor)')
    ax2.margins(0.25)
    ax2.grid(True, linestyle=':', alpha=0.7)

    plt.suptitle('Análisis de Esquemas de Enfriamiento en Simulated Annealing', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'graficas'
    out_dir.mkdir(exist_ok=True)
    plt.savefig(out_dir / 'ejercicio4_sa.png', dpi=300)
    plt.show()