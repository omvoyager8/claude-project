import numpy as np
from scipy.io import loadmat
import os


def load_hsi(file_path):

    ext = os.path.splitext(file_path)[1]

    if ext == ".mat":

        data = loadmat(file_path)

        for key in data:
            if not key.startswith("__"):
                return data[key]

    elif ext == ".npy":

        cube = np.load(file_path)

        return cube

    else:
        raise ValueError("Unsupported file format")