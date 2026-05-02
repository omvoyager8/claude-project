import numpy as np
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense
import joblib

MODEL_PATH = "models/saved_models/autoencoder.h5"
SCALER_PATH = "models/saved_models/ae_scaler.pkl"

def train_autoencoder(X):

    # normalize input (NEW)
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0) + 1e-8

# save scaler
    joblib.dump((mean, std), SCALER_PATH)

    X = (X - mean) / std

    input_layer = Input(shape=(X.shape[1],))

    encoded = Dense(64, activation='relu')(input_layer)
    encoded = Dense(32, activation='relu')(encoded)

    decoded = Dense(64, activation='relu')(encoded)
    decoded = Dense(X.shape[1], activation='linear')(decoded)

    autoencoder = Model(input_layer, decoded)

    autoencoder.compile(optimizer='adam', loss='mse')

    print("Training Autoencoder...")

    autoencoder.fit(X, X,
                    epochs=20,
                    batch_size=256,
                    shuffle=True,
                    validation_split=0.1)

    autoencoder.save(MODEL_PATH)

    print("Model saved at:", MODEL_PATH)


def load_autoencoder():

    print("Loading trained Autoencoder...")

    model = load_model(MODEL_PATH, compile=False)

    return model

def detect_anomaly(model, X):
    
    mean, std = joblib.load(SCALER_PATH)

    X = (X - mean) / std

    reconstructed = model.predict(X, verbose=0)

    error = np.mean((X - reconstructed) ** 2, axis=1)

    return error