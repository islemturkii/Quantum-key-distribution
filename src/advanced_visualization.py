import csv
import os
import matplotlib.pyplot as plt


def load_results(csv_path="results/evaluation_results.csv"):
    results = []

    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            results.append({
                "noise_rate": float(row["noise_rate"]),
                "interception_rate": float(row["interception_rate"]),
                "average_qber": float(row["average_qber"]),
                "average_sifted_length": float(row["average_sifted_length"]),
                "acceptance_rate": float(row["acceptance_rate"]),
            })

    return results


def plot_qber_vs_interception(results, save_path="results/figures/qber_vs_interception.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    noise_levels = sorted(set(row["noise_rate"] for row in results))

    plt.figure(figsize=(9, 5))

    for noise in noise_levels:
        filtered = [row for row in results if row["noise_rate"] == noise]
        filtered.sort(key=lambda x: x["interception_rate"])

        x = [row["interception_rate"] for row in filtered]
        y = [row["average_qber"] for row in filtered]

        plt.plot(x, y, marker="o", label=f"Noise={noise:.2f}")

    plt.axhline(y=0.11, linestyle="--", label="Security threshold")
    plt.xlabel("Eve Interception Rate")
    plt.ylabel("Average QBER")
    plt.title("QBER vs Eve Interception Rate")
    plt.ylim(0, 0.35)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_acceptance_vs_interception(results, save_path="results/figures/acceptance_vs_interception.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    noise_levels = sorted(set(row["noise_rate"] for row in results))

    plt.figure(figsize=(9, 5))

    for noise in noise_levels:
        filtered = [row for row in results if row["noise_rate"] == noise]
        filtered.sort(key=lambda x: x["interception_rate"])

        x = [row["interception_rate"] for row in filtered]
        y = [row["acceptance_rate"] for row in filtered]

        plt.plot(x, y, marker="o", label=f"Noise={noise:.2f}")

    plt.xlabel("Eve Interception Rate")
    plt.ylabel("Acceptance Rate")
    plt.title("Key Acceptance Rate vs Eve Interception Rate")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_qber_heatmap(results, save_path="results/figures/qber_heatmap.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    noise_levels = sorted(set(row["noise_rate"] for row in results))
    interception_levels = sorted(set(row["interception_rate"] for row in results))

    matrix = []

    for noise in noise_levels:
        row_values = []

        for interception in interception_levels:
            match = next(
                row for row in results
                if row["noise_rate"] == noise and row["interception_rate"] == interception
            )
            row_values.append(match["average_qber"])

        matrix.append(row_values)

    plt.figure(figsize=(8, 5))
    plt.imshow(matrix, aspect="auto", origin="lower")

    plt.colorbar(label="Average QBER")
    plt.xticks(range(len(interception_levels)), [f"{x:.2f}" for x in interception_levels])
    plt.yticks(range(len(noise_levels)), [f"{y:.2f}" for y in noise_levels])

    plt.xlabel("Eve Interception Rate")
    plt.ylabel("Noise Rate")
    plt.title("QBER Heatmap under Noise and Eavesdropping")

    for i, noise in enumerate(noise_levels):
        for j, interception in enumerate(interception_levels):
            plt.text(j, i, f"{matrix[i][j]:.3f}", ha="center", va="center")

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def generate_advanced_graphs():
    results = load_results()

    plot_qber_vs_interception(results)
    plot_acceptance_vs_interception(results)
    plot_qber_heatmap(results)

    print("\nAdvanced graphs saved in results/figures/")