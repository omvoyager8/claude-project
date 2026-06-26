from scipy.io import loadmat
import numpy as np

file_path = r"C:\Users\ACER\Desktop\Mokasha Test\abu-airport-3.mat"   # change to your file

data = loadmat(file_path)

print("\nVariables inside the .mat file:\n")

for key, value in data.items():

    if key.startswith("__"):
        continue

    if isinstance(value, np.ndarray):

        print(f"Variable: {key}")
        print(f"Shape: {value.shape}")

        if len(value.shape) == 3:
            print("Type: 3D Hyperspectral Cube\n")

        elif len(value.shape) == 2:
            print("Type: 2D Image / Ground Truth\n")

        else:
            print("Other structure\n")