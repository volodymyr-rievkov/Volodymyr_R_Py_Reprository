"""
Lab Work #6 — Time Series Forecasting: RNN / LSTM / GRU
Course: "Design of Deep Learning Systems"
Lecturer: Prof. D. Peleshko

Case 1: Signal forecasting (sin, cos, sin+cos combination)
Case 2: NY Stock Price Prediction (prices-split-adjusted.csv)
        Models: LSTM baseline, LSTM improved, GRU

Requirements:
    pip install tensorflow numpy pandas scikit-learn matplotlib
"""

import logging
import sys
import zipfile
from pathlib import Path
from typing import Optional

import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.preprocessing
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import Dense, Dropout, GRU, Input, LSTM, SimpleRNN
from keras.models import Sequential
from keras.optimizers import Adam

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("lab6.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

DATA_ZIP  = Path("prices-split-adjusted_csv.zip")
DATA_CSV  = Path("prices-split-adjusted.csv")
STOCK_SYM = "EQIX"                 # stock to predict

# Split ratios
VALID_PCT = 10
TEST_PCT  = 10

# Sequence length (look-back window)
SEQ_LEN   = 20

# Training
EPOCHS     = 50
BATCH_SIZE = 64


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def get_callbacks(patience_es: int = 5, patience_lr: int = 3) -> list:
    return [
        EarlyStopping(
            monitor="val_loss", patience=patience_es,
            restore_best_weights=True, verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=patience_lr, min_lr=1e-6, verbose=1,
        ),
    ]


def save_plot(fig: plt.Figure, name: str) -> None:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    logger.info("Plot saved → %s", path)


def make_sequences(data: np.ndarray, seq_len: int,
                   valid_pct: int, test_pct: int) -> tuple:
    """
    Slide a window of seq_len over data.
    Returns x (features) and y (next-step target) split into train/valid/test.
    """
    sequences = []
    for i in range(len(data) - seq_len):
        sequences.append(data[i: i + seq_len])
    sequences = np.array(sequences)

    n       = sequences.shape[0]
    n_test  = int(np.round(test_pct  / 100 * n))
    n_valid = int(np.round(valid_pct / 100 * n))
    n_train = n - n_valid - n_test

    def split(arr):
        tr = arr[:n_train]
        va = arr[n_train: n_train + n_valid]
        te = arr[n_train + n_valid:]
        return tr, va, te

    x_tr, x_va, x_te = split(sequences[:, :-1, :])
    y_tr, y_va, y_te = split(sequences[:, -1,  :])
    return x_tr, y_tr, x_va, y_va, x_te, y_te


def direction_accuracy(y_true: np.ndarray, y_pred: np.ndarray,
                       open_col: int = 0, close_col: int = 1) -> float:
    """Fraction of correctly predicted close > open directions."""
    true_dir = np.sign(y_true[:, close_col] - y_true[:, open_col])
    pred_dir = np.sign(y_pred[:, close_col] - y_pred[:, open_col])
    return float(np.mean(true_dir == pred_dir))


# ═════════════════════════════════════════════
# CASE 1 — SIGNAL FORECASTING
# ═════════════════════════════════════════════
def generate_signals(n: int = 5000) -> dict[str, np.ndarray]:
    """Generate sin, cos, and sin+cos composite signals."""
    t = np.linspace(0, 10 * np.pi, n)
    return {
        "sin":         np.sin(t),
        "cos":         np.cos(t),
        "sin_plus_cos": np.sin(t) + np.cos(2 * t),   # composite
    }


def prepare_signal_data(signal: np.ndarray, window: int = 50,
                        test_ratio: float = 0.1) -> tuple:
    """
    Create supervised learning sequences from 1-D signal.
    x shape: (samples, window, 1)  y shape: (samples,)
    """
    xs, ys = [], []
    for i in range(len(signal) - window):
        xs.append(signal[i: i + window])
        ys.append(signal[i + window])
    xs, ys = np.array(xs)[..., np.newaxis], np.array(ys)

    split = int(len(xs) * (1 - test_ratio))
    return xs[:split], ys[:split], xs[split:], ys[split:]


def build_signal_model(window: int, cell: str = "LSTM") -> Sequential:
    """
    Two-layer stacked RNN for signal forecasting.
    cell: 'LSTM' | 'GRU' | 'RNN'
    """
    cell_map = {"LSTM": LSTM, "GRU": GRU, "RNN": SimpleRNN}
    CellClass = cell_map[cell]

    m = Sequential(name=f"Signal_{cell}")
    m.add(Input(shape=(window, 1)))
    m.add(CellClass(50, return_sequences=True))
    m.add(Dropout(0.2))
    m.add(CellClass(100))
    m.add(Dropout(0.2))
    m.add(Dense(1, activation="linear"))
    return m


def run_signal_case() -> None:
    logger.info("\n%s\nCASE 1 — Signal Forecasting\n%s", "="*55, "="*55)

    WINDOW    = 50
    signals   = generate_signals(n=5000)
    sig_names = list(signals.keys())

    # Plot all 3 signals
    fig, axes = plt.subplots(3, 1, figsize=(14, 8))
    fig.suptitle("Generated Signals", fontsize=13, fontweight="bold")
    for ax, name in zip(axes, sig_names):
        ax.plot(signals[name][:500], linewidth=0.8)
        ax.set_title(name); ax.set_xlabel("t"); ax.grid(alpha=0.3)
    plt.tight_layout()
    save_plot(fig, "case1_signals.png"); plt.show()

    results = {}

    for sig_name in sig_names:
        signal = signals[sig_name]
        x_tr, y_tr, x_te, y_te = prepare_signal_data(signal, window=WINDOW)

        for cell in ["LSTM", "GRU"]:
            run_name = f"{sig_name}_{cell}"
            logger.info("--- Signal: %-15s | Cell: %s ---", sig_name, cell)

            model = build_signal_model(WINDOW, cell)
            model.compile(loss="mse", optimizer=Adam(1e-3))

            history = model.fit(
                x_tr, y_tr,
                validation_split=0.1,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                callbacks=get_callbacks(patience_es=5),
                verbose=0,
            )

            preds = model.predict(x_te, verbose=0).flatten()
            mse   = float(np.mean((preds - y_te) ** 2))
            results[run_name] = mse
            logger.info("  [%s] Test MSE: %.6f", run_name, mse)

            # Prediction plot
            fig, ax = plt.subplots(figsize=(13, 4))
            ax.plot(y_te, label="True", linewidth=1.5)
            ax.plot(preds, label="Predicted", linewidth=1.5, linestyle="--", alpha=0.85)
            ax.set_title(f"Signal: {sig_name} | {cell}  (MSE={mse:.5f})")
            ax.set_xlabel("Time steps"); ax.legend(); ax.grid(alpha=0.3)
            plt.tight_layout()
            save_plot(fig, f"case1_{run_name}.png"); plt.show()

            del model; K.clear_session()

    # Summary bar chart
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(results.keys(), results.values(), color="steelblue")
    ax.set_title("Signal Forecasting — Test MSE Comparison")
    ax.set_ylabel("MSE"); plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    save_plot(fig, "case1_comparison.png"); plt.show()


# ═════════════════════════════════════════════
# CASE 2 — STOCK PRICE PREDICTION
# ═════════════════════════════════════════════
def load_stock_data(symbol: str = STOCK_SYM) -> pd.DataFrame:
    """Load CSV (unzipping if needed), filter by symbol, drop volume & symbol cols."""
    csv_path = DATA_CSV
    if not csv_path.exists():
        if DATA_ZIP.exists():
            logger.info("Extracting %s …", DATA_ZIP)
            with zipfile.ZipFile(DATA_ZIP) as z:
                z.extractall(".")
        else:
            raise FileNotFoundError(
                f"Neither {DATA_CSV} nor {DATA_ZIP} found in working directory."
            )

    logger.info("Loading %s stock data …", symbol)
    df = pd.read_csv(csv_path, index_col=0)
    logger.info("Full dataset: %s  |  unique symbols: %d", df.shape, df["symbol"].nunique())

    df_stock = df[df["symbol"] == symbol].copy()
    df_stock.drop(columns=["symbol", "volume"], inplace=True)
    df_stock.sort_index(inplace=True)

    logger.info("%s: %d trading days | columns: %s",
                symbol, len(df_stock), list(df_stock.columns))
    return df_stock


def normalize_stock(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """MinMax-normalize each column independently; return df + scalers."""
    scalers = {}
    df_norm = df.copy()
    for col in df.columns:
        scaler = sklearn.preprocessing.MinMaxScaler()
        df_norm[col] = scaler.fit_transform(df[[col]])
        scalers[col] = scaler
    return df_norm, scalers


def plot_stock_eda(df: pd.DataFrame, df_norm: pd.DataFrame, symbol: str) -> None:
    """EDA: raw price + normalized price."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 4))
    fig.suptitle(f"{symbol} Stock — EDA", fontsize=13, fontweight="bold")

    for col, color in zip(["open", "close", "low", "high"],
                          ["red", "green", "blue", "black"]):
        axes[0].plot(df[col].values, color=color, label=col, linewidth=0.8)
        axes[1].plot(df_norm[col].values, color=color, label=col, linewidth=0.8)

    for ax, title in zip(axes, ["Raw Price (USD)", "Normalized [0, 1]"]):
        ax.set_title(title); ax.set_xlabel("Time [days]")
        ax.legend(loc="best"); ax.grid(alpha=0.3)

    plt.tight_layout()
    save_plot(fig, f"case2_{symbol.lower()}_eda.png")
    plt.show()


# ── Model builders ────────────────────────────
def build_lstm_baseline(n_steps: int, n_features: int) -> Sequential:
    """Baseline stacked LSTM (from lab instructions)."""
    m = Sequential(name="LSTM_Baseline")
    m.add(Input(shape=(n_steps, n_features)))
    m.add(LSTM(50, return_sequences=True))
    m.add(Dropout(0.2))
    m.add(LSTM(100))
    m.add(Dropout(0.2))
    m.add(Dense(n_features, activation="linear"))
    return m


def build_lstm_improved(n_steps: int, n_features: int) -> Sequential:
    """
    Improved LSTM:
      - 3 stacked layers (deeper temporal memory)
      - 128 → 64 → 32 units (pyramid shape)
      - Lower dropout (0.1) to preserve gradient flow
      - Extra Dense(16) before output
    """
    m = Sequential(name="LSTM_Improved")
    m.add(Input(shape=(n_steps, n_features)))
    m.add(LSTM(128, return_sequences=True))
    m.add(Dropout(0.1))
    m.add(LSTM(64, return_sequences=True))
    m.add(Dropout(0.1))
    m.add(LSTM(32))
    m.add(Dropout(0.1))
    m.add(Dense(16, activation="relu"))
    m.add(Dense(n_features, activation="linear"))
    return m


def build_gru_model(n_steps: int, n_features: int) -> Sequential:
    """
    GRU — fewer parameters than LSTM (no output gate),
    often converges faster on financial data.
    """
    m = Sequential(name="GRU_Model")
    m.add(Input(shape=(n_steps, n_features)))
    m.add(GRU(64, return_sequences=True))
    m.add(Dropout(0.2))
    m.add(GRU(64))
    m.add(Dropout(0.2))
    m.add(Dense(n_features, activation="linear"))
    return m


STOCK_MODELS = {
    "LSTM_Baseline": build_lstm_baseline,
    "LSTM_Improved": build_lstm_improved,
    "GRU":           build_gru_model,
}


def plot_stock_predictions(y_tr, y_va, y_te,
                           y_tr_pred, y_va_pred, y_te_pred,
                           model_name: str, symbol: str,
                           feature_idx: int = 1) -> None:  # 1 = close price
    """Plot train/valid/test predictions vs actual."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(f"{symbol} — {model_name}", fontsize=13, fontweight="bold")

    n_tr = y_tr.shape[0]
    n_va = y_va.shape[0]
    n_te = y_te.shape[0]

    # Full timeline
    ax1.plot(np.arange(n_tr),                y_tr[:, feature_idx],      color="blue",   label="train target",  lw=0.8)
    ax1.plot(np.arange(n_tr, n_tr+n_va),     y_va[:, feature_idx],      color="gray",   label="valid target",  lw=0.8)
    ax1.plot(np.arange(n_tr+n_va, n_tr+n_va+n_te), y_te[:, feature_idx], color="black", label="test target",   lw=0.8)
    ax1.plot(np.arange(n_tr),                y_tr_pred[:, feature_idx], color="red",    label="train pred",    lw=0.8, linestyle="--")
    ax1.plot(np.arange(n_tr, n_tr+n_va),     y_va_pred[:, feature_idx], color="orange", label="valid pred",    lw=0.8, linestyle="--")
    ax1.plot(np.arange(n_tr+n_va, n_tr+n_va+n_te), y_te_pred[:, feature_idx], color="green", label="test pred", lw=0.8, linestyle="--")
    ax1.set_title("Full timeline"); ax1.set_xlabel("Days"); ax1.set_ylabel("Normalized price")
    ax1.legend(loc="best", fontsize=7); ax1.grid(alpha=0.3)

    # Test only
    ax2.plot(y_te[:, feature_idx],      color="black", label="test target", lw=1.2)
    ax2.plot(y_te_pred[:, feature_idx], color="green", label="test pred",   lw=1.2, linestyle="--")
    ax2.set_title("Test set zoom"); ax2.set_xlabel("Days")
    ax2.legend(loc="best"); ax2.grid(alpha=0.3)

    plt.tight_layout()
    slug = model_name.lower().replace(" ", "_")
    save_plot(fig, f"case2_{symbol.lower()}_{slug}.png")
    plt.show()


def run_stock_case() -> dict:
    logger.info("\n%s\nCASE 2 — Stock Price Prediction\n%s", "="*55, "="*55)

    df_stock         = load_stock_data(STOCK_SYM)
    df_norm, scalers = normalize_stock(df_stock)
    plot_stock_eda(df_stock, df_norm, STOCK_SYM)

    data_np = df_norm.values.astype("float32")
    x_tr, y_tr, x_va, y_va, x_te, y_te = make_sequences(
        data_np, SEQ_LEN, VALID_PCT, TEST_PCT
    )

    logger.info("Shapes: x_train=%s y_train=%s x_valid=%s y_valid=%s x_test=%s y_test=%s",
                x_tr.shape, y_tr.shape, x_va.shape, y_va.shape, x_te.shape, y_te.shape)

    n_steps, n_features = x_tr.shape[1], x_tr.shape[2]
    stock_results = {}

    for name, build_fn in STOCK_MODELS.items():
        logger.info("\n--- Model: %s ---", name)

        model = build_fn(n_steps, n_features)
        model.compile(loss="mse", optimizer=Adam(1e-3))
        model.summary(print_fn=logger.info)

        history = model.fit(
            x_tr, y_tr,
            validation_data=(x_va, y_va),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=get_callbacks(patience_es=7, patience_lr=3),
            verbose=1,
        )

        y_tr_pred = model.predict(x_tr, verbose=0)
        y_va_pred = model.predict(x_va, verbose=0)
        y_te_pred = model.predict(x_te, verbose=0)

        mse_test = float(np.mean((y_te_pred - y_te) ** 2))
        dir_acc  = direction_accuracy(y_te, y_te_pred, open_col=0, close_col=1)

        logger.info("[%s] Test MSE: %.6f | Direction accuracy: %.2f%%",
                    name, mse_test, dir_acc * 100)

        stock_results[name] = {"mse": mse_test, "dir_acc": dir_acc}

        # Training loss plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(history.history["loss"],     label="Train loss", linewidth=2)
        ax.plot(history.history["val_loss"], label="Val loss",   linewidth=2, linestyle="--")
        ax.set_title(f"Training History — {name}")
        ax.set_xlabel("Epoch"); ax.set_ylabel("MSE Loss")
        ax.legend(); ax.grid(alpha=0.3); plt.tight_layout()
        save_plot(fig, f"case2_{name.lower()}_history.png"); plt.show()

        plot_stock_predictions(y_tr, y_va, y_te,
                               y_tr_pred, y_va_pred, y_te_pred,
                               name, STOCK_SYM)

        model.save(str(OUTPUT_DIR / f"stock_{name.lower()}.keras"))
        del model; K.clear_session()
        logger.info("Session cleared after %s\n", name)

    return stock_results


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 60)
    logger.info("Lab 6 — Time Series Forecasting: RNN / LSTM / GRU")
    logger.info("=" * 60)

    run_signal_case()
    stock_results = run_stock_case()

    # Final summary
    logger.info("\n%s\nFINAL SUMMARY — Stock Prediction\n%s", "="*60, "="*60)
    logger.info("  %-20s  %s     %s", "Model", "Test MSE", "Direction Acc")
    logger.info("  " + "-"*50)
    for name, r in stock_results.items():
        logger.info("  %-20s  %.6f   %.2f%%", name, r["mse"], r["dir_acc"] * 100)

    best = min(stock_results, key=lambda k: stock_results[k]["mse"])
    logger.info("\n  Best model (MSE): %s → %.6f", best, stock_results[best]["mse"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()