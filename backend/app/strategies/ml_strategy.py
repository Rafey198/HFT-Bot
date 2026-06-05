"""Machine-learning classifier strategy (logistic regression on indicator features).

Trained on the first portion of the data and applied out-of-sample to reduce
in-sample look-ahead. This is a research demo, not a production model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, to_dir

_FEATURES = ["rsi", "macd_hist", "adx", "roc", "cci", "stoch_k", "bb_bandwidth",
             "williams_r", "supertrend_dir"]


class MlClassifierStrategy(Strategy):
    key = "ml_classifier"
    name = "ML Classifier Strategy"
    category = "ml"
    description = (
        "Logistic-regression classifier predicting next-bar direction from "
        "indicator features. Trained on the first 50% of data, applied forward."
    )
    default_params = {"threshold": 0.58, "train_frac": 0.5}
    sl_atr = 1.5
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        feats = [f for f in _FEATURES if f in df.columns]
        if len(df) < 300 or not feats:
            return pd.Series(0, index=df.index)
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
        except Exception:
            return pd.Series(0, index=df.index)

        X = df[feats].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
        future_ret = df["close"].shift(-1) / df["close"] - 1
        y = (future_ret > 0).astype(int).to_numpy()

        split = int(len(df) * self.params["train_frac"])
        split = max(200, min(split, len(df) - 50))
        scaler = StandardScaler()
        try:
            Xtr = scaler.fit_transform(X[:split])
            model = LogisticRegression(max_iter=500)
            model.fit(Xtr, y[:split])
            proba = model.predict_proba(scaler.transform(X))[:, 1]
        except Exception:
            return pd.Series(0, index=df.index)

        thr = self.params["threshold"]
        proba_s = pd.Series(proba, index=df.index)
        up = proba_s > thr
        dn = proba_s < (1 - thr)
        # Only act out-of-sample (after training split) and on changes.
        oos = pd.Series(False, index=df.index)
        oos.iloc[split:] = True
        up = up & oos
        dn = dn & oos
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        self._proba = proba_s
        return to_dir(up, dn)

    def confidence(self, df: pd.DataFrame, direction: pd.Series) -> pd.Series:
        proba = getattr(self, "_proba", None)
        if proba is None:
            return super().confidence(df, direction)
        conf = (np.abs(proba - 0.5) * 200).clip(0, 100)
        return conf.where(direction != 0, 0.0)

    def _reason(self, df, i, side):
        proba = getattr(self, "_proba", None)
        p = float(proba.iloc[i]) if proba is not None else 0.5
        return f"ML model probability of up-move = {p:.2f} (out-of-sample window)."
