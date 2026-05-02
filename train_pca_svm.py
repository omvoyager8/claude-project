from utils.load_mat import load_hsi
from models.pca_rf_svm import train_pca_rf_svm, test_pca_rf_svm
from utils.preprocess import normalize
from scipy.signal import resample
import scipy.io as sio
import numpy as np
from sklearn.model_selection import train_test_split

# ---------------- LOAD DATA ----------------
data_dict = sio.loadmat(r"C:\Users\ACER\Desktop\abu-airport-2.mat")

cube = data_dict["data"]   # ✅ hyperspectral data
gt   = data_dict["map"]    # ✅ ground truth

print("Cube shape:", cube.shape)
print("GT shape:", gt.shape)

h, w, b = cube.shape

# ---------------- FLATTEN ----------------
X = cube.reshape(-1, b)

# ---------------- PREPROCESS ----------------
X = normalize(X)
X = resample(X, 200, axis=1)

print("X shape after preprocessing:", X.shape)

# ---------------- LABELS ----------------
y = (gt != 0).astype(int).flatten()

print("y shape:", y.shape)

# ---------------- SAFETY CHECK ----------------
if len(y) != X.shape[0]:
    raise ValueError("Mismatch between X and y")

# ---------------- TRAIN TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------- TRAIN ----------------
train_pca_rf_svm(X_train, y_train)

# ---------------- TEST ----------------
test_pca_rf_svm(X_test, y_test)