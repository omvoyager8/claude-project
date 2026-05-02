from utils.load_mat import load_hsi
from utils.preprocess import normalize
from models.pca_rf_svm import get_pca_rf_svm_output
from models.LRaSMD import lrasmd_decomposition
from models.autoencoder_model import train_autoencoder
from scipy.signal import resample
import numpy as np

# ---------------- LOAD DATA ----------------
cube = load_hsi(r"C:\Users\ACER\Desktop\abu-airport-2.mat")

h, w, b = cube.shape

# Flatten
X = cube.reshape(-1, b)

# ---------------- SAME PREPROCESS AS PIPELINE ----------------
X = normalize(X)
X = resample(X, 200, axis=1)

# ---------------- STEP 1 ----------------
combined_features = get_pca_rf_svm_output(X)

# ---------------- STEP 2 ----------------
sparse_output = lrasmd_decomposition(combined_features)

print("Training AE on shape:", sparse_output.shape)

# ---------------- TRAIN AE ----------------
train_autoencoder(sparse_output)