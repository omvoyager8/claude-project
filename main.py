from utils.load_mat import load_hsi
from pipeline.anomaly_pipeline import run_pipeline
import matplotlib.pyplot as plt

cube = load_hsi("data/input/indian_pines_corrected (2).mat")

anomaly_map = run_pipeline(cube)

anomaly_map = (anomaly_map - anomaly_map.min()) / (anomaly_map.max() - anomaly_map.min())

# Optional threshold (makes anomalies bright white)
threshold = 0.9
anomaly_map = (anomaly_map > threshold).astype(int)

plt.imshow(anomaly_map, cmap="gray")
plt.title("Final Anomaly Map")
plt.colorbar()
plt.show()