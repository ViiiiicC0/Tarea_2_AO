import itertools
import math
import random
from pathlib import Path

import matplotlib.pyplot as plt

# --- Funciones base del Problema 5 (Prim y Preorden) ---
def mst_prim(points: list[tuple[float, float]]) -> dict[int, list[int]]:
    """Algoritmo de Prim desde la ciudad 0; retorna el árbol como {nodo: hijos}."""
    best = {v: (math.dist(points[0], points[v]), 0) for v in range(1, len(points))}
    children = {v: [] for v in range(len(points))}
    while best:
        v = min(best, key=lambda u: best[u][0])
        children[best.pop(v)[1]].append(v)
        for u in best:
            d = math.dist(points[v], points[u])
            if d < best[u][0]:
                best[u] = (d, v)
    return children

def preorder(children: dict[int, list[int]], root: int = 0) -> list[int]:
    """Recorre el árbol en preorden; visitar cada ciudad una vez aplica atajos (shortcutting)."""
    return [root] + [c for child in children[root] for c in preorder(children, child)]

def tour_length(points: list[tuple[float, float]], tour: list[int] | tuple[int, ...]) -> float:
    """Calcula la distancia total del ciclo cerrado."""
    n = len(tour)
    return sum(math.dist(points[tour[i]], points[tour[(i + 1) % n]]) for i in range(n))

# --- Algoritmos previos (Ejercicios 3 y 4) para comparar ---
def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def local_search_2opt(points: list[tuple[float, float]], initial_route: list[int]) -> float:
    """Búsqueda local 2-opt; retorna el costo del óptimo local alcanzado."""
    best_route = initial_route[:]
    best_cost = tour_length(points, best_route)
    n = len(best_route)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                candidate = two_opt_move(best_route, i, k)
                candidate_cost = tour_length(points, candidate)
                if candidate_cost < best_cost - 1e-9:
                    best_route = candidate
                    best_cost = candidate_cost
                    improved = True
                    break
            if improved:
                break
    return best_cost

def simulated_annealing_fast(points: list[tuple[float, float]], initial_route: list[int], T0: float = 20.0, max_iter: int = 1500) -> float:
    """Recocido Simulado (enfriamiento exponencial) adaptado a instancias de 9 ciudades."""
    n = len(initial_route)
    current_route = initial_route[:]
    current_cost = tour_length(points, current_route)
    best_cost = current_cost

    for t in range(1, max_iter + 1):
        T = T0 * (0.995 ** t)
        if T <= 1e-4:
            break
        i, k = sorted(random.sample(range(1, n), 2))
        candidate = two_opt_move(current_route, i, k)
        candidate_cost = tour_length(points, candidate)
        delta = candidate_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_route = candidate
            current_cost = candidate_cost
            if current_cost < best_cost:
                best_cost = current_cost
    return best_cost


if __name__ == "__main__":
    random.seed(2026)
    num_instances = 100
    num_cities = 9

    ratios_mst = []
    costs_opt = []
    costs_mst = []
    costs_mst_2opt = []
    costs_ls_random = []
    costs_sa = []

    print(f"Evaluando {num_instances} instancias aleatorias de {num_cities} ciudades...")

    for inst in range(num_instances):
        # 1. Generar 9 puntos aleatorios en un plano de 10x10
        points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(num_cities)]

        # 2. Óptimo exacto por fuerza bruta (fijando ciudad 0: 8! = 40,320 rutas)
        optimal_tour = min(
            ((0,) + p for p in itertools.permutations(range(1, num_cities))),
            key=lambda t: tour_length(points, t)
        )
        c_opt = tour_length(points, optimal_tour)

        # 3. MST puro (Prim + Preorden)
        mst_tour = preorder(mst_prim(points))
        c_mst = tour_length(points, mst_tour)

        # 4. MST + 2-opt (Post-procesamiento)
        c_mst_2opt = local_search_2opt(points, mst_tour)

        # 5. Búsqueda Local 2-opt desde inicio aleatorio
        rand_tour = list(range(num_cities))
        random.shuffle(rand_tour)
        c_ls = local_search_2opt(points, rand_tour)

        # 6. Simulated Annealing desde inicio aleatorio
        c_sa = simulated_annealing_fast(points, rand_tour)

        # Guardar métricas
        ratios_mst.append(c_mst / c_opt)
        costs_opt.append(c_opt)
        costs_mst.append(c_mst)
        costs_mst_2opt.append(c_mst_2opt)
        costs_ls_random.append(c_ls)
        costs_sa.append(c_sa)

    # Resumen estadístico en consola
    print("\n--- Resultados Promedio (100 Instancias) ---")
    print(f"Razón MST (C_mst / C_opt) -> Media: {sum(ratios_mst)/num_instances:.3f} | Máx: {max(ratios_mst):.3f} | Mín: {min(ratios_mst):.3f}")
    print(f"Costo Óptimo Real         -> {sum(costs_opt)/num_instances:.3f}")
    print(f"Costo MST Puro            -> {sum(costs_mst)/num_instances:.3f}")
    print(f"Costo MST + 2-opt         -> {sum(costs_mst_2opt)/num_instances:.3f}")
    print(f"Costo 2-opt (Aleatorio)   -> {sum(costs_ls_random)/num_instances:.3f}")
    print(f"Costo Simulated Annealing -> {sum(costs_sa)/num_instances:.3f}")

    # --- GENERACIÓN DE GRÁFICAS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Gráfica 1: Histograma de la razón de aproximación con línea en 2.0
    ax1.hist(ratios_mst, bins=15, color='cornflowerblue', edgecolor='black', alpha=0.8)
    ax1.axvline(2.0, color='red', linestyle='--', linewidth=2, label='Límite Teórico (Razón = 2.0)')
    ax1.axvline(sum(ratios_mst)/num_instances, color='darkgreen', linestyle='-.', linewidth=1.8,
                label=f'Media Observada ({sum(ratios_mst)/num_instances:.2f})')
    ax1.set_title('Distribución de la Razón de Aproximación ($C_{MST} / C_{óptimo}$)')
    ax1.set_xlabel('Razón de Aproximación')
    ax1.set_ylabel('Frecuencia (de 100 instancias)')
    ax1.set_xlim(1.0, 2.15)
    ax1.legend()
    ax1.grid(axis='y', linestyle=':', alpha=0.7)

    # Gráfica 2: Boxplot comparativo de costos obtenidos
    data_box = [costs_mst, costs_mst_2opt, costs_ls_random, costs_sa, costs_opt]
    labels_box = ['MST Puro', 'MST + 2-opt', '2-opt\n(Aleatorio)', 'Simulated\nAnnealing', 'Óptimo\n(Fuerza Bruta)']
    
    bp = ax2.boxplot(data_box, tick_labels=labels_box, patch_artist=True)
    box_colors = ['lightcoral', 'lightgreen', 'lightblue', 'khaki', 'lightgray']
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)

    ax2.set_title('Comparación de Costos por Método (100 Instancias)')
    ax2.set_ylabel('Longitud Total del Tour (menor es mejor)')
    ax2.grid(axis='y', linestyle=':', alpha=0.7)

    plt.suptitle('Evaluación de Aproximación MST y Post-Procesamiento (9 Ciudades)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'graficas'
    out_dir.mkdir(exist_ok=True)
    plt.savefig(out_dir / 'ejercicio5_mst.png', dpi=300)
    plt.show()