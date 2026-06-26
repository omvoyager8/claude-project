import sys
import os
import numpy as np
from scipy.ndimage import label, gaussian_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.load_mat import load_hsi
from pipeline.anomaly_pipeline import run_pipeline

INPUT_DIR = "data/input"
OUTPUT_DIR = "static/output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_hyperspectral(file_path):

    print("Loading hyperspectral image")
    cube, gt = load_hsi(file_path)
    print("Cube shape:", cube.shape)

    print("Running anomaly detection pipeline")
    anomaly_map = run_pipeline(cube)

    # ---------------- NORMALIZE + CONTRAST ----------------
    anomaly_map = (anomaly_map - anomaly_map.min()) / (anomaly_map.max() - anomaly_map.min() + 1e-8)
    p_low = np.percentile(anomaly_map, 2)
    p_high = np.percentile(anomaly_map, 98)
    anomaly_map = np.clip((anomaly_map - p_low) / (p_high - p_low + 1e-8), 0, 1)
    anomaly_map = gaussian_filter(anomaly_map, sigma=1)
    anomaly_map = anomaly_map ** 4

    # ---------------- CREATE RGB IMAGE ----------------
    r = cube[:, :, cube.shape[2] // 2]
    g = cube[:, :, cube.shape[2] // 3]
    b = cube[:, :, cube.shape[2] // 4]
    rgb = np.stack((r, g, b), axis=2)
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-8)

    # ---------------- HEATMAP + MASK ----------------
    import matplotlib.cm as cm
    heatmap = cm.inferno(anomaly_map)[:, :, :3]
    threshold = anomaly_map.mean() + 1.2 * anomaly_map.std()
    mask = anomaly_map > threshold
    labeled, num = label(mask)
    for i in range(1, num + 1):
        if np.sum(labeled == i) < 30:
            mask[labeled == i] = 0
    heatmap[~mask] *= 0.2

    # ---------------- OVERLAY ----------------
    alpha = 0.6
    overlay = (1 - alpha) * rgb + alpha * heatmap
    output_path = os.path.join(OUTPUT_DIR, "anomaly_output.png")
    plt.imsave(output_path, overlay)
    print("Saving anomaly overlay image")

    # ---------------- ROC CURVE ----------------
    roc_path = None
    cm_path = None
    roc_auc_val = None
    y_true_flat = None

    if gt is not None:
        y_true = (gt != 0).astype(int).flatten()
        y_score = anomaly_map.flatten()

        # make sure shapes match (gt might differ from cube spatial dims)
        if y_true.shape[0] == y_score.shape[0]:
            y_true_flat = y_true

            # ROC Curve
            fpr, tpr, thresholds = roc_curve(y_true, y_score)
            roc_auc_val = auc(fpr, tpr)

            fig, ax = plt.subplots(figsize=(6, 5))
            ax.plot(fpr, tpr, color="#003366", lw=2, label=f"ROC Curve (AUC = {roc_auc_val:.4f})")
            ax.plot([0, 1], [0, 1], color="#aaaaaa", lw=1.5, linestyle="--", label="Random Classifier")
            ax.fill_between(fpr, tpr, alpha=0.08, color="#003366")
            ax.set_xlabel("False Positive Rate", fontsize=11)
            ax.set_ylabel("True Positive Rate", fontsize=11)
            ax.set_title("ROC Curve — Anomaly Detection", fontsize=13, fontweight="bold")
            ax.legend(loc="lower right", fontsize=10)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            roc_path = os.path.join(OUTPUT_DIR, "roc_curve.png")
            fig.savefig(roc_path, dpi=150)
            plt.close(fig)

            # Confusion Matrix — threshold at optimal point (Youden's J)
            j_scores = tpr - fpr
            best_thresh = thresholds[np.argmax(j_scores)]
            y_pred = (y_score >= best_thresh).astype(int)

            cm_vals = confusion_matrix(y_true, y_pred)
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            disp = ConfusionMatrixDisplay(confusion_matrix=cm_vals, display_labels=["Background", "Anomaly"])
            disp.plot(ax=ax2, colorbar=False, cmap="Blues")
            ax2.set_title("Confusion Matrix", fontsize=13, fontweight="bold")
            fig2.tight_layout()
            cm_path = os.path.join(OUTPUT_DIR, "confusion_matrix.png")
            fig2.savefig(cm_path, dpi=150)
            plt.close(fig2)

            # derive metrics from confusion matrix
            tn, fp, fn, tp = cm_vals.ravel()
            precision = tp / (tp + fp + 1e-8)
            recall = tp / (tp + fn + 1e-8)
            f1 = 2 * precision * recall / (precision + recall + 1e-8)
        else:
            print(f"GT shape mismatch: gt={y_true.shape}, map={y_score.shape}, skipping ROC/CM")
            tn = fp = fn = tp = precision = recall = f1 = None
    else:
        tn = fp = fn = tp = precision = recall = f1 = None

    print("Pipeline completed")

    stats = {
        "shape": cube.shape,
        "bands": cube.shape[2],
        "total_pixels": cube.shape[0] * cube.shape[1],
        "anomaly_pixels": int(np.sum(mask)),
        "anomaly_percent": round(float(np.sum(mask)) / (cube.shape[0] * cube.shape[1]) * 100, 2),
        "anomaly_min": round(float(anomaly_map.min()), 6),
        "anomaly_max": round(float(anomaly_map.max()), 6),
        "anomaly_mean": round(float(anomaly_map.mean()), 6),
        "anomaly_std": round(float(anomaly_map.std()), 6),
        "roc_auc": round(float(roc_auc_val), 4) if roc_auc_val is not None else None,
        "tp": int(tp) if tp is not None else None,
        "fp": int(fp) if fp is not None else None,
        "tn": int(tn) if tn is not None else None,
        "fn": int(fn) if fn is not None else None,
        "precision": round(float(precision), 4) if precision is not None else None,
        "recall": round(float(recall), 4) if recall is not None else None,
        "f1_score": round(float(f1), 4) if f1 is not None else None,
        "roc_path": roc_path,
        "cm_path": cm_path,
    }

    return output_path, stats