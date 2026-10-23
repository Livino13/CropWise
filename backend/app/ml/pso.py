"""PSO for feature weight optimization.

Supervised mode (default): maximize stratified CV accuracy of a small
Random Forest on the weighted features. The old unsupervised objective
(Xie-Beni cluster compactness) is still available via `optimize_unsupervised`
and is reported as a diagnostic by the training pipeline.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

from .fcm import FCM, xie_beni


class PSO:
    def __init__(self, n_particles=12, n_iterations=20, w=0.7, c1=1.5, c2=1.5,
                 cv_folds=3, est_trees=60, seed=42):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.cv_folds = cv_folds
        self.est_trees = est_trees
        self.seed = seed

    def optimize(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Maximize mean stratified CV accuracy. X must already be scaled."""
        rng = np.random.default_rng(self.seed)
        n, d = X.shape
        pos = rng.uniform(0.1, 3.0, (self.n_particles, d))
        vel = rng.uniform(-0.5, 0.5, (self.n_particles, d))
        pbest_pos = pos.copy()
        pbest_val = np.full(self.n_particles, float("inf"))
        gbest_pos = pos[0].copy()
        gbest_val = float("inf")

        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.seed)

        def objective(weights):
            est = RandomForestClassifier(
                n_estimators=self.est_trees, random_state=self.seed, n_jobs=1
            )
            scores = cross_val_score(est, X * weights, y, cv=cv, scoring="accuracy", n_jobs=-1)
            return 1.0 - float(scores.mean())  # minimize error == maximize accuracy

        for i in range(self.n_particles):
            v = objective(pos[i])
            pbest_val[i] = v
            if v < gbest_val:
                gbest_val = v
                gbest_pos = pos[i].copy()

        for _ in range(self.n_iterations):
            for i in range(self.n_particles):
                r1, r2 = rng.random(d), rng.random(d)
                vel[i] = self.w * vel[i] + self.c1 * r1 * (pbest_pos[i] - pos[i]) + self.c2 * r2 * (gbest_pos - pos[i])
                vel[i] = np.clip(vel[i], -1.0, 1.0)
                pos[i] = np.clip(pos[i] + vel[i], 0.1, 3.0)
                v = objective(pos[i])
                if v < pbest_val[i]:
                    pbest_val[i] = v
                    pbest_pos[i] = pos[i].copy()
                    if v < gbest_val:
                        gbest_val = v
                        gbest_pos = pos[i].copy()

        self.best_weights_ = gbest_pos
        self.best_value_ = gbest_val
        self.best_cv_accuracy_ = 1.0 - gbest_val
        return gbest_pos

    def optimize_unsupervised(self, X: np.ndarray, n_clusters=5, m=2.0) -> np.ndarray:
        """Legacy objective: minimize Xie-Beni index (cluster compactness). Kept
        so the FCM+PSO story in the report has a reproducible baseline."""
        rng = np.random.default_rng(self.seed)
        n, d = X.shape
        pos = rng.uniform(0.1, 3.0, (self.n_particles, d))
        vel = rng.uniform(-0.5, 0.5, (self.n_particles, d))
        pbest_pos = pos.copy()
        pbest_val = np.full(self.n_particles, float("inf"))
        gbest_pos = pos[0].copy()
        gbest_val = float("inf")

        def objective(weights):
            Xw = X * weights
            fcm = FCM(n_clusters=n_clusters, m=m, max_iter=50, seed=0)
            centers, U = fcm.fit(Xw)
            return xie_beni(Xw, centers, U, m)

        for i in range(self.n_particles):
            v = objective(pos[i])
            pbest_val[i] = v
            if v < gbest_val:
                gbest_val = v
                gbest_pos = pos[i].copy()
        for _ in range(self.n_iterations):
            for i in range(self.n_particles):
                r1, r2 = rng.random(d), rng.random(d)
                vel[i] = self.w * vel[i] + self.c1 * r1 * (pbest_pos[i] - pos[i]) + self.c2 * r2 * (gbest_pos - pos[i])
                vel[i] = np.clip(vel[i], -1.0, 1.0)
                pos[i] = np.clip(pos[i] + vel[i], 0.1, 3.0)
                v = objective(pos[i])
                if v < pbest_val[i]:
                    pbest_val[i] = v
                    pbest_pos[i] = pos[i].copy()
                    if v < gbest_val:
                        gbest_val = v
                        gbest_pos = pos[i].copy()
        self.best_weights_ = gbest_pos
        self.best_value_ = gbest_val
        return gbest_pos

    @property
    def best_weights(self):
        return getattr(self, "best_weights_", None)
