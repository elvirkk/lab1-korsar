"""
Построение графиков для лабораторной работы №1:
    1) Q(s)          — абсолютная расходная характеристика
    2) Q_отн(s)      — относительная расходная характеристика
    3) Kv_отн(s)     — пропускная характеристика (теоретическая)
    4) Q_отн и Kv_отн — на одних осях (сравнение)
    5) ζ(s)          — КГС от положения РО

Использование:
    py plot_Q_zeta.py result\out\_sensor_1.dat
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------- Параметры задачи -------
RHO_WATER = 998.2
ZETA_1    = 6.13
R_RANGE   = 30.0

def load_data(path):
    data = pd.read_csv(path, sep=r"\s+", encoding="utf-8-sig")
    required = {"TAU", "d1", "s_valve"}
    if not required.issubset(data.columns):
        raise ValueError(f"Нужны колонки {required}. Нашли: {set(data.columns)}")
    for col in required:
        data[col] = pd.to_numeric(data[col], errors="raise")
    return data

def steady_state_by_step(data):
    s_values = sorted(data["s_valve"].unique())
    Q_ss = []
    for s in s_values:
        mask = np.isclose(data["s_valve"], s)
        sub = data[mask]
        n = max(1, int(len(sub) * 0.4))
        Q_ss.append(sub["d1"].iloc[-n:].mean())
    return np.array(s_values), np.array(Q_ss)

def main():
    if len(sys.argv) < 2:
        print("Использование: py plot_Q_zeta.py <путь_к__sensor_1.dat>")
        sys.exit(1)

    data_path = Path(sys.argv[1]).resolve()
    out_dir = data_path.parent.parent.parent / "pic"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_data(data_path)
    s_vals, Q_kgs = steady_state_by_step(data)

    # Абсолютный расход, м³/ч
    Q_m3h = Q_kgs / RHO_WATER * 3600.0
    Q_max = Q_m3h[-1]  # при s = 1.0
    Q_rel = Q_m3h / Q_max

    # Пропускная характеристика (равнопроцентная, R=30)
    Kv_rel = R_RANGE ** (s_vals - 1.0)

    # КГС
    zeta = ZETA_1 / Kv_rel**2

    # 1. Q(s) — абсолютный расход
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.plot(s_vals, Q_m3h, "o-", color="tab:blue", linewidth=2, markersize=7,
            label="Расчёт КОРСАР")
    ax.set_xlabel("s — относительное положение штока")
    ax.set_ylabel("Q, м³/ч")
    ax.set_title("Абсолютная расходная характеристика Q(s)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(out_dir / "Q_of_s.png", dpi=180)
    plt.close(fig)
    print(f"Сохранено: {out_dir / 'Q_of_s.png'}")

    # 2. Q_отн(s) — относительный расход
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.plot(s_vals, Q_rel, "o-", color="tab:green", linewidth=2, markersize=7,
            label=r"$Q_{отн}(s)$ — из КОРСАР")
    ax.set_xlabel("s — относительное положение штока")
    ax.set_ylabel(r"$Q_{отн} = Q/Q_{max}$")
    ax.set_title("Относительная расходная характеристика")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(out_dir / "Q_rel.png", dpi=180)
    plt.close(fig)
    print(f"Сохранено: {out_dir / 'Q_rel.png'}")

    # 3. Сравнение Q_отн и Kv_отн (главный график ЛР)
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    ax.plot(s_vals, Kv_rel, "s--", color="tab:red", linewidth=2, markersize=7,
            label=r"Пропускная $Kv_{отн}(s) = 30^{s-1}$ (теория)")
    ax.plot(s_vals, Q_rel, "o-", color="tab:blue", linewidth=2, markersize=7,
            label=r"Расходная $Q_{отн}(s)$ (КОРСАР)")
    ax.set_xlabel("s — относительное положение штока")
    ax.set_ylabel("Относительная величина")
    ax.set_title("Сравнение пропускной и расходной характеристик")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(out_dir / "compare_Q_Kv.png", dpi=180)
    plt.close(fig)
    print(f"Сохранено: {out_dir / 'compare_Q_Kv.png'}")

    # 4. ζ(s) — КГС
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.semilogy(s_vals, zeta, "d-", color="tab:purple", linewidth=2, markersize=7,
                label=r"$\zeta(s) = \zeta_1/f^2(s)$")
    ax.set_xlabel("s — относительное положение штока")
    ax.set_ylabel(r"КГС $\zeta$")
    ax.set_title("Зависимость КГС от положения РО")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.savefig(out_dir / "zeta_of_s.png", dpi=180)
    plt.close(fig)
    print(f"Сохранено: {out_dir / 'zeta_of_s.png'}")

    # Таблица в консоль
    print()
    print(f"{'s':>6} | {'Q, кг/с':>10} | {'Q, м³/ч':>10} | "
          f"{'Q_отн':>8} | {'Kv_отн':>8} | {'ζ':>8}")
    print("-" * 70)
    for s, qk, qm, qr, kr, z in zip(s_vals, Q_kgs, Q_m3h, Q_rel, Kv_rel, zeta):
        print(f"{s:>6.2f} | {qk:>10.3f} | {qm:>10.2f} | "
              f"{qr:>8.3f} | {kr:>8.3f} | {z:>8.1f}")

if __name__ == "__main__":
    main()