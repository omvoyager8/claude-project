import numpy as np
import matplotlib.pyplot as plt

def show_input_output(hsi, anomaly_map):

    # choose 3 spectral bands for RGB visualization
    r = hsi[:,:,30]
    g = hsi[:,:,60]
    b = hsi[:,:,90]

    rgb = np.stack((r,g,b), axis=2)

    # normalize
    rgb = (rgb - rgb.min())/(rgb.max()-rgb.min())

    # plot images
    plt.figure(figsize=(10,5))

    plt.subplot(1,2,1)
    plt.title("Input Hyperspectral Image (RGB)")
    plt.imshow(rgb)
    plt.axis("off")

    plt.subplot(1,2,2)
    plt.title("Anomaly Detection Output")
    plt.imshow(anomaly_map, cmap="hot")
    plt.axis("off")

    plt.show()