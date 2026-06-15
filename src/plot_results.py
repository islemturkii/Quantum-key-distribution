import matplotlib.pyplot as plt


def plot_error_rates(error_without_eve, error_with_eve):
    """
    Plot a comparison of error rates for two BB84 scenarios:
    1. Normal transmission
    2. Transmission under Eve's intercept-resend attack
    """
    scenarios = ["Without Eve", "With Eve"]
    error_rates = [error_without_eve, error_with_eve]

    plt.figure(figsize=(8, 5))
    plt.bar(scenarios, error_rates)
    plt.ylabel("Error Rate")
    plt.ylim(0, 1)
    plt.title("BB84 Error Rate Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.show()