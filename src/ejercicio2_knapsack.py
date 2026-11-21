from pathlib import Path

import matplotlib.pyplot as plt

def greedy_knapsack_density(items: list[str], values: list[int], weights: list[int], capacity: int):
    """Método 1: Prioriza mayor relación valor/peso (densidad)."""
    # Empaquetamos cada objeto en una tupla: (nombre, valor, peso, densidad)
    packaged = [(items[i], values[i], weights[i], values[i] / weights[i]) for i in range(len(items))]
    
    # Ordenamos de mayor a menor densidad (reverse=True)
    packaged.sort(key=lambda x: x[3], reverse=True)
    
    chosen = []
    total_weight = 0
    total_value = 0
    
    for name, v, w, _ in packaged:
        if total_weight + w <= capacity:
            chosen.append(name)
            total_weight += w
            total_value += v
            
    return chosen, total_weight, total_value


def greedy_knapsack_min_weight(items: list[str], values: list[int], weights: list[int], capacity: int):
    """Método 2: Prioriza menor peso primero."""
    packaged = [(items[i], values[i], weights[i]) for i in range(len(items))]
    
    # Ordenamos de menor a mayor peso (reverse=False por defecto)
    packaged.sort(key=lambda x: x[2])
    
    chosen = []
    total_weight = 0
    total_value = 0
    
    for name, v, w in packaged:
        if total_weight + w <= capacity:
            chosen.append(name)
            total_weight += w
            total_value += v
            
    return chosen, total_weight, total_value


if __name__ == "__main__":
    # Instancia pequeña diseñada para que "Menor Peso" falle frente a "Valor/Peso"
    items = ["A", "B", "C", "D"]
    weights = [2, 3, 4, 9]
    values = [3, 4, 5, 100]
    W = 10

    chosen_dens, w_dens, val_dens = greedy_knapsack_density(items, values, weights, W)
    chosen_minw, w_minw, val_minw = greedy_knapsack_min_weight(items, values, weights, W)

    # Imprimir tabla comparativa en consola
    print(f"{'Método':<22} | {'Objetos':<15} | {'Capacidad Usada':<18} | {'Valor Total'}")
    print("-" * 72)
    print(f"{'Valor / Peso':<22} | {str(chosen_dens):<15} | {f'{w_dens} / {W}':<18} | {val_dens}")
    print(f"{'Menor Peso Primero':<22} | {str(chosen_minw):<15} | {f'{w_minw} / {W}':<18} | {val_minw}")

    # Generación de gráfica de barras comparativa
    methods = ['Greedy: Valor / Peso', 'Greedy: Menor Peso']
    used_capacities = [w_dens, w_minw]
    total_values = [val_dens, val_minw]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Subgráfica 1: Valor total obtenido
    bars1 = ax1.bar(methods, total_values, color=['seagreen', 'indianred'], width=0.5)
    ax1.set_title('Valor Total Obtenido')
    ax1.set_ylabel('Valor ($)')
    ax1.set_ylim(0, max(total_values) * 1.2)
    ax1.grid(axis='y', linestyle=':', alpha=0.7)
    for bar, objs in zip(bars1, [chosen_dens, chosen_minw]):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 f"{bar.get_height()}\n({','.join(objs)})", ha='center', va='bottom', fontweight='bold')

    # Subgráfica 2: Capacidad utilizada
    bars2 = ax2.bar(methods, used_capacities, color=['royalblue', 'goldenrod'], width=0.5)
    ax2.axhline(W, color='red', linestyle='--', label=f'Capacidad Máxima ({W})')
    ax2.set_title('Capacidad Utilizada')
    ax2.set_ylabel('Peso (kg)')
    ax2.set_ylim(0, W * 1.25)
    ax2.legend()
    ax2.grid(axis='y', linestyle=':', alpha=0.7)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{bar.get_height()} / {W}", ha='center', va='bottom', fontweight='bold')

    plt.suptitle('Comparación Greedy Knapsack (Instancia Contraejemplo)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'graficas'
    out_dir.mkdir(exist_ok=True)
    plt.savefig(out_dir / 'ejercicio2_knapsack.png', dpi=300)
    plt.show()