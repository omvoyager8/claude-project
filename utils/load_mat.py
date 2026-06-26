import numpy as np
from scipy.io import loadmat
import os


def load_hsi(file_path):

    ext = os.path.splitext(file_path)[1]

    if ext == ".mat":

        data = loadmat(file_path)

        cube = None
        gt = None

        for key, value in data.items():
            if key.startswith("__") or not isinstance(value, np.ndarray):
                continue
            if len(value.shape) == 3:
                cube = value
            elif len(value.shape) == 2 and gt is None:
                gt = value

        if cube is None:
            # fallback: pick largest array
            for key, value in data.items():
                if key.startswith("__") or not isinstance(value, np.ndarray):
                    continue
                if cube is None or value.size > cube.size:
                    cube = value

        return cube, gt

    elif ext == ".npy":
        cube = np.load(file_path)
        return cube, None

    else:
        raise ValueError("Unsupported file format")