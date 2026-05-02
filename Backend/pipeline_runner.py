import sys
import os
import numpy as np
from scipy.ndimage import label
from scipy.ndimage import gaussian_filter
# allow backend to access project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt

from utils.load_mat import load_hsi
from pipeline.anomaly_pipeline import run_pipeline


INPUT_DIR = "data/input"
OUTPUT_DIR = "static/output"


os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_hyperspectral(file_path):

    print("Loading hyperspectral image")

    cube = load_hsi(file_path)

    print("Cube shape:", cube.shape)

    print("Running anomaly detection pipeline")

    anomaly_map = run_pipeline(cube)

    # ---------------- NORMALIZE + CONTRAST ----------------
    anomaly_map = (anomaly_map - anomaly_map.min()) / (anomaly_map.max() - anomaly_map.min() + 1e-8)

    # stronger percentile stretch
    p_low = np.percentile(anomaly_map, 2)
    p_high = np.percentile(anomaly_map, 98)

    anomaly_map = np.clip((anomaly_map - p_low) / (p_high - p_low + 1e-8), 0, 1)
    anomaly_map = gaussian_filter(anomaly_map, sigma=1)
    # stronger amplification
    anomaly_map = anomaly_map ** 4

    # ---------------- CREATE RGB IMAGE ----------------
    r = cube[:, :, cube.shape[2]//2]
    g = cube[:, :, cube.shape[2]//3]
    b = cube[:, :, cube.shape[2]//4]

    rgb = np.stack((r, g, b), axis=2)
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-8)

    # ---------------- CREATE HEATMAP ----------------
    import matplotlib.cm as cm

    heatmap = cm.inferno(anomaly_map)[:, :, :3]

        # ---------------- HIGHLIGHT STRONG ANOMALIES ----------------
    threshold = anomaly_map.mean() + 1.2 * anomaly_map.std()

    mask = anomaly_map > threshold

    labeled, num = label(mask)

    # remove small regions
    for i in range(1, num + 1):
        if np.sum(labeled == i) < 30:
            mask[labeled == i] = 0

    # keep only anomaly regions
    heatmap[~mask] *= 0.2

    # ---------------- OVERLAY ----------------
    alpha = 0.6
    overlay = (1 - alpha) * rgb + alpha * heatmap

    # ---------------- SAVE ----------------
    output_path = os.path.join(OUTPUT_DIR, "anomaly_output.png")

    print("Saving anomaly overlay image")

    plt.imsave(output_path, overlay)

    print("Pipeline completed")
    print("min:", anomaly_map.min(), "max:", anomaly_map.max(), "std:", anomaly_map.std())

    return output_path