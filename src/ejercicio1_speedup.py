import multiprocessing as mp
import random
import time
from pathlib import Path


def estimate_pi(seed: int, samples: int = 1_000_000) -> float:
    """Monte Carlo: fracción de puntos aleatorios dentro del cuarto de círculo unitario."""
    rng = random.Random(seed)
    inside = sum(rng.random()**2 + rng.random()**2 <= 1.0 for _ in range(samples))
    return 4 * inside / samples

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    seeds = list(range(8))
    process_counts = [1, 2, 4, 8]
    times = {}
    speedups = []

    print("Ejecutando experimentos de aceleración paralela...\n")

    for p in process_counts:
        t0 = time.perf_counter()
        with mp.Pool(processes=p) as pool:
            results = pool.map(estimate_pi, seeds)
        t_elapsed = time.perf_counter() - t0
        
        times[p] = t_elapsed
        sp = times[1] / t_elapsed
        speedups.append(sp)
        
        pi_avg = sum(results) / len(results)
        print(f"Procesos (p={p}): Tiempo Tp = {t_elapsed:.4f} s | Speedup Sp = {sp:.2f}x | Pi ~ {pi_avg:.5f}")

    # Generación de la gráfica
    plt.figure(figsize=(8, 5))
    plt.plot(process_counts, speedups, marker='o', linewidth=2, color='royalblue', label='Speedup Real ($S_p = T_1 / T_p$)')
    plt.plot(process_counts, process_counts, linestyle='--', color='gray', label='Speedup Ideal ($S_p = p$)')
    
    plt.title(r'Aceleración Paralela (Parallel Speedup) - Estimación de $\pi$')
    plt.xlabel('Número de Procesos ($p$)')
    plt.ylabel('Speedup ($S_p$)')
    plt.xticks(process_counts)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'graficas'
    out_dir.mkdir(exist_ok=True)
    plt.savefig(out_dir / 'ejercicio1_speedup.png', dpi=300)
    plt.show()