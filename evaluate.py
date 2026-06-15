"""
evaluate.py — Systematic BB84 evaluation across noise × interception grid
"""
import os, csv, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bit_generator import generate_bits
from src.basis_generator import generate_bases
from src.eve_attack import intercept_resend_attack
from src.noise import apply_channel_noise
from src.measurement import measure_bits
from src.sifting import sift_key
from src.error_analysis import calculate_error_rate
from src.information_reconciliation import reconcile_keys
from src.privacy_amplification import privacy_amplification

N_BITS  = 256
N_TRIALS = 20
QBER_THRESHOLD = 0.11
NOISE_LEVELS       = [0.00, 0.02, 0.05, 0.08, 0.10]
INTERCEPTION_RATES = [0.00, 0.25, 0.50, 0.75, 1.00]
RESULTS_CSV = "results/evaluation_results.csv"
FIG_DIR     = "results/figures"
os.makedirs(FIG_DIR, exist_ok=True)
PALETTE = ["#2196F3","#FF9800","#4CAF50","#F44336","#9C27B0"]

def single_trial(n_bits, noise_rate, interception_rate):
    bits  = generate_bits(n_bits)
    bases = generate_bases(n_bits)
    tx, _ = intercept_resend_attack(bits, bases, interception_rate)
    noisy  = apply_channel_noise(tx, noise_rate)
    bob_b  = generate_bases(n_bits)
    bob_r  = measure_bits(noisy, bases, bob_b)
    a, b, _ = sift_key(bits, bases, bob_b, bob_r)
    qber, _ = calculate_error_rate(a, b)
    return qber, len(a), qber <= QBER_THRESHOLD

def run_evaluation():
    rows = []
    total = len(NOISE_LEVELS)*len(INTERCEPTION_RATES)
    done  = 0
    print(f"Running {total} combos × {N_TRIALS} trials…")
    for noise in NOISE_LEVELS:
        for interception in INTERCEPTION_RATES:
            qbers,lengths,accepts=[],[],[]
            for _ in range(N_TRIALS):
                q,l,a=single_trial(N_BITS,noise,interception)
                qbers.append(q); lengths.append(l); accepts.append(int(a))
            rows.append({"noise_rate":noise,"interception_rate":interception,
                "average_qber":np.mean(qbers),"average_sifted_length":np.mean(lengths),
                "acceptance_rate":np.mean(accepts)})
            done+=1
            print(f"  [{done:02d}/{total}] noise={noise:.2f} eve={interception:.2f} QBER={np.mean(qbers):.4f} accept={np.mean(accepts):.2f}")
    with open(RESULTS_CSV,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(f"Saved {RESULTS_CSV}")
    return rows

def plot_qber_vs_interception(rows):
    fig,ax=plt.subplots(figsize=(9,5))
    for idx,noise in enumerate(NOISE_LEVELS):
        sub=sorted([r for r in rows if r["noise_rate"]==noise],key=lambda r:r["interception_rate"])
        ax.plot([r["interception_rate"] for r in sub],[r["average_qber"] for r in sub],
                marker="o",color=PALETTE[idx],label=f"Noise={noise:.2f}")
    ax.axhline(QBER_THRESHOLD,linestyle="--",color="#2196F3",linewidth=1.4,label=f"Threshold ({QBER_THRESHOLD})")
    ax.set(xlabel="Eve Interception Rate",ylabel="Average QBER",title="QBER vs Eve Interception Rate",ylim=(0,0.35))
    ax.grid(True,linestyle="--",alpha=0.5); ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/qber_vs_interception.png",dpi=150); plt.close(fig)
    print(f"  Saved qber_vs_interception.png")

def plot_acceptance_vs_interception(rows):
    fig,ax=plt.subplots(figsize=(9,5))
    for idx,noise in enumerate(NOISE_LEVELS):
        sub=sorted([r for r in rows if r["noise_rate"]==noise],key=lambda r:r["interception_rate"])
        ax.plot([r["interception_rate"] for r in sub],[r["acceptance_rate"] for r in sub],
                marker="o",color=PALETTE[idx],label=f"Noise={noise:.2f}")
    ax.set(xlabel="Eve Interception Rate",ylabel="Acceptance Rate",
           title="Key Acceptance Rate vs Eve Interception Rate",ylim=(0,1.05))
    ax.grid(True,linestyle="--",alpha=0.5); ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/acceptance_vs_interception.png",dpi=150); plt.close(fig)
    print(f"  Saved acceptance_vs_interception.png")

def plot_qber_heatmap(rows):
    matrix=[[next(r["average_qber"] for r in rows if r["noise_rate"]==noise and r["interception_rate"]==inter)
              for inter in INTERCEPTION_RATES] for noise in NOISE_LEVELS]
    fig,ax=plt.subplots(figsize=(8,5))
    im=ax.imshow(matrix,aspect="auto",origin="lower",cmap="viridis")
    fig.colorbar(im,ax=ax,label="Average QBER")
    ax.set_xticks(range(len(INTERCEPTION_RATES))); ax.set_xticklabels([f"{x:.2f}" for x in INTERCEPTION_RATES])
    ax.set_yticks(range(len(NOISE_LEVELS)));       ax.set_yticklabels([f"{y:.2f}" for y in NOISE_LEVELS])
    ax.set(xlabel="Eve Interception Rate",ylabel="Noise Rate",title="QBER Heatmap — Noise × Eavesdropping")
    for i in range(len(NOISE_LEVELS)):
        for j in range(len(INTERCEPTION_RATES)):
            ax.text(j,i,f"{matrix[i][j]:.3f}",ha="center",va="center",
                    color="white" if matrix[i][j]<0.18 else "black",fontsize=8)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/qber_heatmap.png",dpi=150); plt.close(fig)
    print(f"  Saved qber_heatmap.png")

def _run_scenario(noise,eve,n=512):
    bits=generate_bits(n); bases=generate_bases(n)
    tx,_=intercept_resend_attack(bits,bases,eve)
    noisy=apply_channel_noise(tx,noise)
    bob_b=generate_bases(n); bob_r=measure_bits(noisy,bases,bob_b)
    a,b,_=sift_key(bits,bases,bob_b,bob_r)
    qber,_=calculate_error_rate(a,b)
    return qber

def plot_bb84_error_comparison():
    e0=_run_scenario(0.0,0.0); e1=_run_scenario(0.0,1.0)
    fig,ax=plt.subplots(figsize=(7,4))
    bars=ax.bar(["Without Eve","With Eve"],[e0,e1],color=["#4CAF50","#F44336"],width=0.4)
    for bar,val in zip(bars,[e0,e1]):
        ax.text(bar.get_x()+bar.get_width()/2,val+0.01,f"{val:.3f}",ha="center",fontsize=11,fontweight="bold")
    ax.axhline(QBER_THRESHOLD,linestyle="--",color="#2196F3",linewidth=1.4,label=f"Threshold={QBER_THRESHOLD}")
    ax.set(ylabel="Error Rate / QBER",ylim=(0,0.45),title="BB84 Error Rate Comparison")
    ax.legend(fontsize=9); ax.grid(axis="y",linestyle="--",alpha=0.5)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/bb84_error_comparison.png",dpi=150); plt.close(fig)
    print(f"  Saved bb84_error_comparison.png")

def plot_bb84_full_comparison():
    scenarios={"Baseline\n(no noise,\nno Eve)":_run_scenario(0.0,0.0),
               "Noise only\n(5%)":_run_scenario(0.05,0.0),
               "Full Eve\n(100%)":_run_scenario(0.0,1.0),
               "Partial Eve\n(25%)":_run_scenario(0.0,0.25)}
    colors=["#4CAF50","#FF9800","#F44336","#9C27B0"]
    fig,ax=plt.subplots(figsize=(10,5))
    bars=ax.bar(list(scenarios.keys()),list(scenarios.values()),color=colors,width=0.5)
    for bar,val in zip(bars,scenarios.values()):
        ax.text(bar.get_x()+bar.get_width()/2,val+0.008,f"{val:.3f}",ha="center",fontsize=10,fontweight="bold")
    ax.axhline(QBER_THRESHOLD,linestyle="--",color="#2196F3",linewidth=1.4,label=f"Threshold={QBER_THRESHOLD}")
    ax.set(ylabel="Error Rate / QBER",ylim=(0,0.45),title="BB84 Multi-Scenario QBER Comparison")
    ax.legend(fontsize=9); ax.grid(axis="y",linestyle="--",alpha=0.5)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/bb84_full_comparison.png",dpi=150); plt.close(fig)
    print(f"  Saved bb84_full_comparison.png")

def plot_reconciliation_effectiveness():
    before_vals,after_vals,labels=[],[],[]
    for noise in NOISE_LEVELS:
        bits=generate_bits(512); bases=generate_bases(512)
        tx,_=intercept_resend_attack(bits,bases,0.0)
        noisy=apply_channel_noise(tx,noise)
        bob_b=generate_bases(512); bob_r=measure_bits(noisy,bases,bob_b)
        a,b,_=sift_key(bits,bases,bob_b,bob_r)
        q_before,_=calculate_error_rate(a,b)
        ar,br,_=reconcile_keys(a,b)
        q_after,_=calculate_error_rate(ar,br)
        before_vals.append(q_before); after_vals.append(q_after)
        labels.append(f"Noise={noise:.2f}")
    x=np.arange(len(labels)); w=0.35
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(x-w/2,before_vals,w,label="Before Reconciliation",color="#F44336",alpha=0.85)
    ax.bar(x+w/2,after_vals, w,label="After Reconciliation",color="#4CAF50",alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(labels,fontsize=10)
    ax.set(ylabel="QBER",title="CASCADE Reconciliation Effectiveness")
    ax.legend(fontsize=10); ax.grid(axis="y",linestyle="--",alpha=0.5)
    fig.tight_layout(); fig.savefig(f"{FIG_DIR}/reconciliation_effectiveness.png",dpi=150); plt.close(fig)
    print(f"  Saved reconciliation_effectiveness.png")

if __name__=="__main__":
    rows=run_evaluation()
    print("\nGenerating figures…")
    plot_qber_vs_interception(rows)
    plot_acceptance_vs_interception(rows)
    plot_qber_heatmap(rows)
    plot_bb84_error_comparison()
    plot_bb84_full_comparison()
    plot_reconciliation_effectiveness()
    print("\n✓ Done. All figures in results/figures/")
