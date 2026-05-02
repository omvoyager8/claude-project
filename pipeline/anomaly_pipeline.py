import numpy as np
from scipy.signal import resample
from utils.preprocess import normalize
from models.pca_rf_svm import get_pca_rf_svm_output
from models.LRaSMD import lrasmd_decomposition
from models.autoencoder_model import load_autoencoder, detect_anomaly


def run_pipeline(cube):

    print("Starting anomaly detection pipeline")

    h, w, bands = cube.shape

    # flatten hyperspectral cube
    X = cube.reshape(-1, bands)

    # preprocessing
    X = normalize(X)

    X = resample(X, 200, axis=1)
    
    if X.shape[1] != 200:
        raise ValueError("Band standardization failed")
    print("After band standardization:", X.shape)
        # ---------------- STEP 1 ----------------
    print("Running PCA + RF + SVM")

    combined_features = get_pca_rf_svm_output(X)
    print("Shape after ensemble:", combined_features.shape)  # (N,3)

    # ---------------- STEP 2 ----------------
    print("Running LRaSMD")

    sparse_output = lrasmd_decomposition(combined_features)
    print("Shape after LRaSMD:", sparse_output.shape)

    # ---------------- STEP 3 ----------------
    print("Loading Autoencoder")

    autoencoder = load_autoencoder()

    print("Running Autoencoder anomaly detection")

    errors = detect_anomaly(autoencoder, sparse_output)
    errors = np.nan_to_num(errors)

    anomaly_map = errors.reshape(h, w)

    print("Pipeline finished")

    return anomaly_map