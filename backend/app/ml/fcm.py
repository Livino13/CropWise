"""Fuzzy C-Means clustering + Xie-Beni index."""
import numpy as np


class FCM:
    def __init__(self, n_clusters=5, m=2.0, max_iter=100, tol=1e-4, seed=42):
        self.n_clusters = n_clusters
        self.m = m
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed
        self.centers_ = None
        self.U_ = None

    def fit(self, X: np.ndarray, n_clusters=None, m=None, max_iter=None, tol=None):
        # allow spec-style overrides: fit(X, n_clusters=5, m=2.0, max_iter=100, tol=1e-4)
        if n_clusters is not None:
            self.n_clusters = n_clusters
        if m is not None:
            self.m = m
        if max_iter is not None:
            self.max_iter = max_iter
        if tol is not None:
            self.tol = tol

        rng = np.random.default_rng(self.seed)
        n, d = X.shape
        c = self.n_clusters
        U = rng.random((c, n))
        U /= U.sum(axis=0, keepdims=True)

        for _ in range(self.max_iter):
            Um = U ** self.m
            centers = (Um @ X) / Um.sum(axis=1, keepdims=True)
            dist = np.linalg.norm(X[None, :, :] - centers[:, None, :], axis=2)
            dist = np.maximum(dist, 1e-10)
            exp = 2.0 / (self.m - 1)
            inv = dist ** (-exp)
            U_new = inv / inv.sum(axis=0, keepdims=True)
            if np.linalg.norm(U_new - U) < self.tol:
                U = U_new
                break
            U = U_new

        Um = U ** self.m
        centers = (Um @ X) / Um.sum(axis=1, keepdims=True)
        self.centers_ = centers
        self.U_ = U
        return centers, U


def membership(X: np.ndarray, centers: np.ndarray, m: float = 2.0) -> np.ndarray:
    """Soft membership of rows of X w.r.t. fitted cluster centers.

    Used at inference time so FCM cluster structure trained on the weighted
    feature space becomes extra features for the classifier.
    Returns U with shape (n_clusters, n_samples), column-normalized.
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    dist = np.linalg.norm(X[None, :, :] - centers[:, None, :], axis=2)
    dist = np.maximum(dist, 1e-10)
    inv = dist ** (-2.0 / (m - 1))
    return inv / inv.sum(axis=0, keepdims=True)


def xie_beni(X: np.ndarray, centers: np.ndarray, U: np.ndarray, m: float = 2.0) -> float:
    n = X.shape[0]
    c = centers.shape[0]
    Um = U ** m
    dist2 = np.linalg.norm(X[None, :, :] - centers[:, None, :], axis=2) ** 2
    compact = (Um * dist2).sum()
    sep = float("inf")
    for i in range(c):
        for j in range(i + 1, c):
            d2 = np.sum((centers[i] - centers[j]) ** 2)
            sep = min(sep, d2)
    if sep < 1e-10:
        return float("inf")
    return compact / (n * sep)


# spec name
compute_xie_beni = xie_beni
