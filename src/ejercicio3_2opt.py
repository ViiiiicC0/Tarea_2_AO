import math
import random
from pathlib import Path

import matplotlib.pyplot as plt

def tour_length(points: list[tuple[float, float]], route: list[int]) -> float:
    """Calcula la distancia euclidiana total de un tour cerrado."""
    n = len(route)
    return sum(math.dist(points[route[i]], points[route[(i + 1) % n]]) for i in range(n))

def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    """Invierte el subsegmento route[i..k] (elimina cruces entre dos aristas)."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def local_search_2opt(points: list[tuple[float, float]], initial_route: list[int]) -> tuple[list[int], float, int]:
    """
    Aplica búsqueda local (First-Improvement) con 2-opt hasta alcanzar un óptimo local.
    Retorna: (mejor_ruta, costo_final, numero_de_mejoras)
    """
    best_route = initial_route[:]  # Copia de la ruta inicial
    best_cost = tour_length(points, best_route)
    improvements = 0
    n = len(best_route)
    improved = True

    while improved:
        improved = False
        # Probar todos los pares de cortes posibles (i, k)
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                candidate = two_opt_move(best_route, i, k)
                candidate_cost = tour_length(points, candidate)
                
                # Si mejora (con tolerancia numérica 1e-9 para evitar ciclos por flotantes)
                if candidate_cost < best_cost - 1e-9:
                    best_route = candidate
                    best_cost = candidate_cost
                    improvements += 1
                    improved = True
                    break  # First-improvement: aplicamos la mejora de inmediato y reiniciamos
            if improved:
                break

    return best_route, best_cost, improvements

def nearest_neighbor_tour(points: list[tuple[float, float]], start_node: int) -> list[int]:
    """Construye una ruta inicial yendo siempre a la ciudad no visitada más cercana."""
    n = len(points)
    unvisited = set(range(n))
    unvisited.remove(start_node)
    route = [start_node]
    current = start_node

    while unvisited:
        # Buscar la ciudad en 'unvisited' con menor distancia euclidiana a 'current'
        next_city = min(unvisited, key=lambda city: math.dist(points[current], points[city]))
        route.append(next_city)
        unvisited.remove(next_city)
        current = next_city

    return route

if __name__ == "__main__":
    # Generar un mapa fijo de 20 ciudades en un cuadrado de 100x100
    random.seed(42)
    num_cities = 20
    cities = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_cities)]
    
    trials = 40  # Número de repeticiones del experimento
    
    random_improvements, random_costs = [], []
    nn_improvements, nn_costs = [], []

    for t in range(trials):
        # Escenario 1: Inicio aleatorio
        rand_init = list(range(num_cities))
        random.shuffle(rand_init)
        _, cost_r, imp_r = local_search_2opt(cities, rand_init)
        random_improvements.append(imp_r)
        random_costs.append(cost_r)

        # Escenario 2: Inicio con Vecino Más Cercano desde un nodo aleatorio
        start_node = random.randrange(num_cities)
        nn_init = nearest_neighbor_tour(cities, start_node)
        _, cost_nn, imp_nn = local_search_2opt(cities, nn_init)
        nn_improvements.append(imp_nn)
        nn_costs.append(cost_nn)

    # Resumen estadístico en consola
    print(f"--- Resultados tras {trials} ejecuciones ({num_cities} ciudades) ---")
    print(f"Inicio Aleatorio      -> Mejoras promedio: {sum(random_improvements)/trials:.2f} | Costo promedio: {sum(random_costs)/trials:.2f}")
    print(f"Vecino Más Cercano    -> Mejoras promedio: {sum(nn_improvements)/trials:.2f} | Costo promedio: {sum(nn_costs)/trials:.2f}")

    # Generación de diagramas de caja (Boxplots)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    # Boxplot 1: Número de mejoras necesarias
    
    ax1.boxplot([random_improvements, nn_improvements], tick_labels=['Inicio Aleatorio', 'Vecino Más Cercano'],
                patch_artist=True, boxprops=dict(facecolor='lightblue', color='navy'))
    ax1.set_title('Número de Mejoras (2-opt) hasta Converger')
    ax1.set_ylabel('Cantidad de movimientos 2-opt')
    ax1.grid(axis='y', linestyle=':', alpha=0.7)

    # Boxplot 2: Calidad de la solución final (Costo / Distancia)
  
  
    ax2.boxplot([random_costs, nn_costs], tick_labels=['Inicio Aleatorio', 'Vecino Más Cercano'],
                patch_artist=True, boxprops=dict(facecolor='lightgreen', color='darkgreen'))
    ax2.set_title('Calidad del Óptimo Local Alcanzado')
    ax2.set_ylabel('Distancia Total del Tour (menor es mejor)')
    ax2.grid(axis='y', linestyle=':', alpha=0.7)

    plt.suptitle('Comparación Búsqueda Local 2-opt: Aleatorio vs. Vecino Más Cercano', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'graficas'
    out_dir.mkdir(exist_ok=True)
    plt.savefig(out_dir / 'ejercicio3_2opt.png', dpi=300)
    plt.show()