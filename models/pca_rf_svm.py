import joblib
import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

PCA_PATH = "models/saved_models/pca.pkl"
RF_PATH = "models/saved_models/rf.pkl"
SVM_PATH = "models/saved_models/svm.pkl"


# ---------------- TRAIN ----------------
def train_pca_rf_svm(X, y):

    print("Training PCA...")
    pca = PCA(n_components=30)
    X_pca = pca.fit_transform(X)

    print("Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42
    )
    rf.fit(X_pca, y)

    print("Training SVM...")
    svm = SVC(kernel='rbf', probability=True)
    svm.fit(X_pca, y)

    # Save models
    joblib.dump(pca, PCA_PATH)
    joblib.dump(rf, RF_PATH)
    joblib.dump(svm, SVM_PATH)

    print("Models saved:")
    print(PCA_PATH, RF_PATH, SVM_PATH)


# ---------------- TEST ----------------
def test_pca_rf_svm(X_test, y_test):

    pca, rf, svm = load_models()

    X_test_pca = pca.transform(X_test)

    # Predictions
    rf_pred = rf.predict(X_test_pca)
    svm_pred = svm.predict(X_test_pca)

    # Ensemble (majority voting)
    final_pred = (rf_pred + svm_pred) / 2
    final_pred = (final_pred > 0.5).astype(int)

    print("\n--- Random Forest ---")
    print(f"Accuracy: {accuracy_score(y_test, rf_pred):.2%}")

    print("\n--- SVM ---")
    print(f"Accuracy: {accuracy_score(y_test, svm_pred):.2%}")

    print("\n--- Combined Model ---")
    acc = accuracy_score(y_test, final_pred)
    print(f"Accuracy: {acc:.2%}")
    print("\nDetailed Report:")
    print(classification_report(y_test, final_pred))


# ---------------- LOAD ----------------
def load_models():
    print("Loading PCA + RF + SVM models...")
    pca = joblib.load(PCA_PATH)
    rf = joblib.load(RF_PATH)
    svm = joblib.load(SVM_PATH)
    return pca, rf, svm

def get_pca_rf_svm_output(X):

    pca, rf, svm = load_models()

    X_pca = pca.transform(X)

    # RF probability
    rf_probs = rf.predict_proba(X_pca)[:, 1].reshape(-1, 1)

    # SVM decision score
    svm_scores = svm.decision_function(X_pca).reshape(-1, 1)

    final_features = np.hstack((X_pca, rf_probs, svm_scores))

    return final_features
