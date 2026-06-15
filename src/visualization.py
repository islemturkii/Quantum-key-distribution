import os
import matplotlib.pyplot as plt


def plot_error_comparison(error_without_eve, error_with_eve, save_path=None):
    """
    Plot a simple two-scenario BB84 error comparison.
    """
    scenarios = ["Without Eve", "With Eve"]
    error_rates = [error_without_eve, error_with_eve]

    plt.figure(figsize=(8, 5))
    plt.bar(scenarios, error_rates)
    plt.ylabel("Error Rate / QBER")
    plt.ylim(0, 1)
    plt.title("BB84 Error Rate Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for i, value in enumerate(error_rates):
        plt.text(i, value + 0.02, f"{value:.3f}", ha="center")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_full_comparison(results_dict, save_path=None):
    """
    Plot multiple BB84 scenarios comparison.
    """
    scenarios = list(results_dict.keys())
    error_rates = list(results_dict.values())

    plt.figure(figsize=(10, 5))
    plt.bar(scenarios, error_rates)
    plt.ylabel("Error Rate / QBER")
    plt.ylim(0, 1)
    plt.title("BB84 Multi-Scenario QBER Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for i, value in enumerate(error_rates):
        plt.text(i, value + 0.02, f"{value:.3f}", ha="center")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()