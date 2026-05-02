import numpy as np


def lrasmd_decomposition(X):

    """
    Low Rank and Sparse Matrix Decomposition
    Used to separate background and anomalies
    """

    print("Running LRaSMD decomposition")

    # compute covariance
    mean_vec = np.mean(X, axis=0)

    centered = X - mean_vec

    # compute SVD
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)

    # choose low-rank approximation
    rank = min(10, X.shape[1])

    low_rank = np.dot(U[:, :rank], np.dot(np.diag(S[:rank]), Vt[:rank, :]))

    sparse = centered - low_rank
   

    print("LRaSMD finished")

    return sparse