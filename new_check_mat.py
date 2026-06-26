import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import os

def load_hyperspectral(file_path):
    
    ext = os.path.splitext(file_path)[1].lower()

    # ---------------- LOAD ----------------
    if ext == ".mat":
        data = sio.loadmat(file_path)
        print("MAT Keys:", data.keys())

        # auto-pick correct key
        cube = None
        for key in data:
            if not key.startswith("__"):
                cube = data[key]
                print("Using key:", key)
                break

        if cube is None:
            raise ValueError("No valid data found in .mat file")

    elif ext == ".npy":
        cube = np.load(file_path)
        print("Loaded NPY file")

    else:
        raise ValueError("Unsupported file format")

    # ---------------- SHAPE FIX ----------------
    print("Original shape:", cube.shape)

    # if shape is (Bands, H, W) → convert to (H, W, Bands)
    if cube.shape[0] < 20:  # heuristic
        cube = np.transpose(cube, (1, 2, 0))
        print("Transposed to (H, W, Bands)")

    print("Final shape:", cube.shape)

    return cube


def visualize_hsi(cube):

    # ---------------- AUTO RGB ----------------
    variances = np.var(cube, axis=(0,1))
    top3 = np.argsort(variances)[-3:]

    rgb = cube[:, :, top3]

    # normalize
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-8)

    plt.imshow(rgb)
    plt.title(f"Auto RGB Bands: {top3}")
    plt.axis("off")
    plt.show()

    # ---------------- SINGLE BAND ----------------
    plt.imshow(cube[:, :, cube.shape[2]//2], cmap="gray")
    plt.title("Middle Band")
    plt.colorbar()
    plt.show()


# ---------------- MAIN ----------------
file_path = r"C:\Users\ACER\Desktop\Mokasha Test\abu-airport-3.mat"   # change path

cube = load_hyperspectral(file_path)

print("Dataset shape:", cube.shape)

visualize_hsi(cube)