import numpy as np

def normalize(hsi):

    hsi = hsi.astype("float32")

    min_val = hsi.min()
    max_val = hsi.max()

    normalized = (hsi - min_val) / (max_val - min_val)

    return normalized