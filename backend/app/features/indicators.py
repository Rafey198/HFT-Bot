"""Technical indicators implemented with pandas/numpy (no hard pandas-ta dependency)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(period, min_periods=1).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def wma(series: pd.Series, period: int) -> pd.Series:
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def true_range(df: pd.DataFrame) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / period, adjust=False).mean()


def adx(df: pd.DataFrame, period: int = 14):
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr = true_range(df)
    atr_ = tr.ewm(alpha=1 / period, adjust=False).mean().replace(0, np.nan)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean() / atr_
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean() / atr_
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx_ = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx_.fillna(0), plus_di.fillna(0), minus_di.fillna(0)


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def stochastic(df: pd.DataFrame, k: int = 14, d: int = 3):
    low_k = df["low"].rolling(k).min()
    high_k = df["high"].rolling(k).max()
    k_line = 100 * (df["close"] - low_k) / (high_k - low_k).replace(0, np.nan)
    d_line = k_line.rolling(d).mean()
    return k_line.fillna(50), d_line.fillna(50)


def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    ma = tp.rolling(period).mean()
    md = (tp - ma).abs().rolling(period).mean()
    return ((tp - ma) / (0.015 * md.replace(0, np.nan))).fillna(0)


def roc(series: pd.Series, period: int = 12) -> pd.Series:
    return (series.pct_change(period) * 100).fillna(0)


def williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"].rolling(period).max()
    low = df["low"].rolling(period).min()
    return (-100 * (high - df["close"]) / (high - low).replace(0, np.nan)).fillna(-50)


def bollinger(series: pd.Series, period: int = 20, mult: float = 2.0):
    mid = sma(series, period)
    std = series.rolling(period).std()
    upper = mid + mult * std
    lower = mid - mult * std
    bandwidth = (upper - lower) / mid.replace(0, np.nan)
    return upper, mid, lower, bandwidth.fillna(0)


def keltner(df: pd.DataFrame, period: int = 20, mult: float = 2.0):
    mid = ema(df["close"], period)
    rng = atr(df, period)
    return mid + mult * rng, mid, mid - mult * rng


def donchian(df: pd.DataFrame, period: int = 20):
    upper = df["high"].rolling(period).max()
    lower = df["low"].rolling(period).min()
    mid = (upper + lower) / 2
    return upper, mid, lower


def supertrend(df: pd.DataFrame, period: int = 10, mult: float = 3.0):
    atr_ = atr(df, period)
    hl2 = (df["high"] + df["low"]) / 2
    upper = hl2 + mult * atr_
    lower = hl2 - mult * atr_
    n = len(df)
    st = np.zeros(n)
    direction = np.ones(n)
    close = df["close"].to_numpy()
    up = upper.to_numpy().copy()
    lo = lower.to_numpy().copy()
    for i in range(1, n):
        if close[i] > up[i - 1]:
            direction[i] = 1
        elif close[i] < lo[i - 1]:
            direction[i] = -1
        else:
            direction[i] = direction[i - 1]
            if direction[i] > 0 and lo[i] < lo[i - 1]:
                lo[i] = lo[i - 1]
            if direction[i] < 0 and up[i] > up[i - 1]:
                up[i] = up[i - 1]
        st[i] = lo[i] if direction[i] > 0 else up[i]
    return pd.Series(st, index=df.index), pd.Series(direction, index=df.index)


def ichimoku(df: pd.DataFrame):
    high, low = df["high"], df["low"]
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    return tenkan, kijun, span_a, span_b


def obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["close"].diff().fillna(0))
    return (direction * df["volume"]).cumsum()


def vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    cum_vol = df["volume"].cumsum().replace(0, np.nan)
    return (tp * df["volume"]).cumsum() / cum_vol


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add the full trend/momentum/volatility/volume indicator set."""
    out = df.copy()
    c = out["close"]
    out["sma_20"] = sma(c, 20)
    out["sma_50"] = sma(c, 50)
    out["ema_9"] = ema(c, 9)
    out["ema_21"] = ema(c, 21)
    out["ema_50"] = ema(c, 50)
    out["ema_200"] = ema(c, 200)
    out["wma_20"] = wma(c, 20)
    macd_line, signal_line, hist = macd(c)
    out["macd"] = macd_line
    out["macd_signal"] = signal_line
    out["macd_hist"] = hist
    adx_, plus_di, minus_di = adx(out)
    out["adx"] = adx_
    out["plus_di"] = plus_di
    out["minus_di"] = minus_di
    st, st_dir = supertrend(out)
    out["supertrend"] = st
    out["supertrend_dir"] = st_dir
    tenkan, kijun, span_a, span_b = ichimoku(out)
    out["ichimoku_tenkan"] = tenkan
    out["ichimoku_kijun"] = kijun
    out["ichimoku_span_a"] = span_a
    out["ichimoku_span_b"] = span_b

    out["rsi"] = rsi(c)
    k_line, d_line = stochastic(out)
    out["stoch_k"] = k_line
    out["stoch_d"] = d_line
    out["cci"] = cci(out)
    out["roc"] = roc(c)
    out["williams_r"] = williams_r(out)

    out["atr"] = atr(out)
    bb_u, bb_m, bb_l, bb_w = bollinger(c)
    out["bb_upper"] = bb_u
    out["bb_mid"] = bb_m
    out["bb_lower"] = bb_l
    out["bb_bandwidth"] = bb_w
    kc_u, kc_m, kc_l = keltner(out)
    out["kc_upper"] = kc_u
    out["kc_mid"] = kc_m
    out["kc_lower"] = kc_l
    dc_u, dc_m, dc_l = donchian(out)
    out["donchian_upper"] = dc_u
    out["donchian_mid"] = dc_m
    out["donchian_lower"] = dc_l

    out["obv"] = obv(out)
    out["vol_ma_20"] = sma(out["volume"], 20)
    out["vwap"] = vwap(out)
    return out
