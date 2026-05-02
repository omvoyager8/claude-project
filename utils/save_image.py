import cv2
import numpy as np

def save_anomaly_image(anomaly_map, path):

    anomaly_map = (anomaly_map - anomaly_map.min()) / (anomaly_map.max() - anomaly_map.min())

    anomaly_map = (anomaly_map * 255).astype("uint8")

    cv2.imwrite(path, anomaly_map)