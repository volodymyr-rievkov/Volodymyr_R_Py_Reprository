import logging
import sys
from pathlib import Path

import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.datasets import imdb
from keras.layers import (
    Activation, Conv1D, Dense, Dropout,
    Embedding, Input, LSTM, MaxPooling1D,
)
from keras.models import Model, Sequential
from keras.optimizers import Adam, RMSprop
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("lab5.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Use Case 1 — Spam
SPAM_CSV        = Path("spam.csv")
SPAM_MAX_WORDS  = 1000
SPAM_MAX_LEN    = 150
SPAM_EMBED_DIM  = 50
SPAM_TEST_SPLIT = 0.15
SPAM_EPOCHS     = 15
SPAM_BATCH      = 128

# Use Case 2 — IMDB (reduced for CPU speed)
IMDB_TOP_WORDS  = 3000   # lab uses 5000
IMDB_MAX_LEN    = 200    # lab uses 500 — biggest speedup factor
IMDB_EMBED_DIM  = 32
IMDB_EPOCHS     = 5
IMDB_BATCH      = 64


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────
def get_callbacks(patience_es: int = 2, patience_lr: int = 1) -> list:
    return [
        EarlyStopping(
            monitor="val_loss", min_delta=1e-4,
            patience=patience_es, restore_best_weights=True, verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=patience_lr, min_lr=1e-6, verbose=1,
        ),
    ]


def compile_and_train(model, x_tr, y_tr, x_val, y_val,
                      epochs, batch_size, optimizer=None) -> dict:
    if optimizer is None:
        optimizer = Adam(learning_rate=1e-3)
    model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    # Build model before summary/count_params (required in Keras 3.x)
    model.build(input_shape=(None, x_tr.shape[1]))
    model.summary(print_fn=logger.info)
    try:
        param_str = f"{model.count_params():,}"
    except Exception:
        param_str = "n/a"
    logger.info("Training '%s': %s params | train=%d val=%d",
                model.name, param_str, len(x_tr), len(x_val))
    h = model.fit(
        x_tr, y_tr,
        validation_data=(x_val, y_val),
        epochs=epochs, batch_size=batch_size,
        callbacks=get_callbacks(), verbose=1,
    )
    return h.history


def evaluate(model, x_test, y_test, label: str) -> tuple:
    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    logger.info("[%s]  loss=%.4f  accuracy=%.4f (%.2f%%)", label, loss, acc, acc * 100)
    return loss, acc


def plot_history(history: dict, title: str, save_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(title, fontsize=12, fontweight="bold")
    ax1.plot(history["accuracy"],     label="Train", linewidth=2)
    ax1.plot(history["val_accuracy"], label="Val",   linewidth=2, linestyle="--")
    ax1.set_title("Accuracy"); ax1.set_xlabel("Epoch"); ax1.legend(); ax1.grid(alpha=0.3)
    ax2.plot(history["loss"],     label="Train", linewidth=2)
    ax2.plot(history["val_loss"], label="Val",   linewidth=2, linestyle="--")
    ax2.set_title("Loss"); ax2.set_xlabel("Epoch"); ax2.legend(); ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    logger.info("Plot saved → %s", save_path)
    plt.show()


def plot_comparison(results: dict, title: str, save_path: Path) -> None:
    names = list(results.keys())
    accs  = [results[n]["accuracy"] * 100 for n in names]
    fig, ax = plt.subplots(figsize=(max(8, len(names) * 2), 5))
    bars = ax.bar(names, accs, color="steelblue", edgecolor="white")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel("Test Accuracy (%)"); ax.set_ylim(min(accs) - 5, 102)
    ax.grid(axis="y", alpha=0.3); plt.xticks(rotation=20, ha="right")
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{acc:.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    logger.info("Comparison chart saved → %s", save_path)
    plt.show()


# ═════════════════════════════════════════════
# USE CASE 1 — SPAM DETECTION
# ═════════════════════════════════════════════
def load_spam() -> tuple:
    logger.info("Loading spam dataset from '%s' …", SPAM_CSV)
    df = pd.read_csv(SPAM_CSV, encoding="latin-1")[["v1", "v2"]]
    df.columns = ["label", "text"]
    logger.info("Rows: %d\n%s", len(df), df["label"].value_counts().to_string())

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.countplot(x="label", data=df, ax=ax, palette="Blues_d")
    ax.set_title("Ham vs Spam count"); plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "spam_distribution.png", dpi=150, bbox_inches="tight")
    plt.show()

    le     = LabelEncoder()
    labels = le.fit_transform(df["label"])
    logger.info("Label mapping: %s", dict(zip(le.classes_, le.transform(le.classes_))))
    return df["text"].values, labels


def tokenize(x_tr, x_te, max_words, max_len) -> tuple:
    tok      = Tokenizer(num_words=max_words)
    tok.fit_on_texts(x_tr)
    tr_mat   = pad_sequences(tok.texts_to_sequences(x_tr), maxlen=max_len)
    te_mat   = pad_sequences(tok.texts_to_sequences(x_te), maxlen=max_len)
    logger.info("Tokenizer vocab=%d (cap=%d) | train=%s test=%s",
                len(tok.word_index), max_words, tr_mat.shape, te_mat.shape)
    return tr_mat, te_mat, tok


def spam_baseline() -> Model:
    """Baseline from lab instructions: Embedding → LSTM(64) → Dense(256) → sigmoid."""
    inp = Input(shape=(SPAM_MAX_LEN,), name="inputs")
    x   = Embedding(SPAM_MAX_WORDS, SPAM_EMBED_DIM, input_length=SPAM_MAX_LEN)(inp)
    x   = LSTM(64)(x)
    x   = Dense(256, name="FC1")(x)
    x   = Activation("relu")(x)
    x   = Dropout(0.5)(x)
    x   = Dense(1, name="output")(x)
    x   = Activation("sigmoid")(x)
    return Model(inp, x, name="SpamLSTM_Baseline")


def spam_improved() -> Model:
    """
    Improved spam LSTM.
    Changes vs baseline:
      - LSTM units 64→128 with recurrent_dropout
      - Smaller Dense head 256→128 (less overfitting)
      - Dropout 0.5→0.3
    """
    inp = Input(shape=(SPAM_MAX_LEN,), name="inputs")
    x   = Embedding(SPAM_MAX_WORDS, SPAM_EMBED_DIM, input_length=SPAM_MAX_LEN)(inp)
    x   = LSTM(128, dropout=0.2, recurrent_dropout=0.2)(x)
    x   = Dense(128, activation="relu", name="FC1")(x)
    x   = Dropout(0.3)(x)
    x   = Dense(1, activation="sigmoid", name="output")(x)
    return Model(inp, x, name="SpamLSTM_Improved")


def run_spam() -> dict:
    logger.info("\n%s\nUSE CASE 1 — Spam Detection\n%s", "="*55, "="*55)
    texts, labels = load_spam()

    x_tr, x_te, y_tr, y_te = train_test_split(
        texts, labels, test_size=SPAM_TEST_SPLIT, random_state=42, stratify=labels
    )
    tr_mat, te_mat, _ = tokenize(x_tr, x_te, SPAM_MAX_WORDS, SPAM_MAX_LEN)
    x_tr2, x_val, y_tr2, y_val = train_test_split(tr_mat, y_tr, test_size=0.2, random_state=42)

    results = {}
    for name, build_fn, opt in [
        ("SpamLSTM Baseline", spam_baseline, RMSprop()),
        ("SpamLSTM Improved", spam_improved, Adam(1e-3)),
    ]:
        logger.info("--- %s ---", name)
        model   = build_fn()
        history = compile_and_train(model, x_tr2, y_tr2, x_val, y_val,
                                    SPAM_EPOCHS, SPAM_BATCH, opt)
        loss, acc = evaluate(model, te_mat, y_te, name)
        results[name] = {"loss": loss, "accuracy": acc}

        slug = name.lower().replace(" ", "_")
        plot_history(history, name, OUTPUT_DIR / f"{slug}_history.png")
        model.save(str(OUTPUT_DIR / f"{slug}.keras"))
        del model; K.clear_session()
        logger.info("Session cleared after %s\n", name)

    return results


# ═════════════════════════════════════════════
# USE CASE 2 — IMDB SENTIMENT
# ═════════════════════════════════════════════
def load_imdb() -> tuple:
    logger.info("Loading IMDB (top_words=%d, max_len=%d) …", IMDB_TOP_WORDS, IMDB_MAX_LEN)
    (x_tr, y_tr), (x_te, y_te) = imdb.load_data(num_words=IMDB_TOP_WORDS)
    x_tr = pad_sequences(x_tr, maxlen=IMDB_MAX_LEN)
    x_te = pad_sequences(x_te, maxlen=IMDB_MAX_LEN)
    logger.info("IMDB shapes: train=%s test=%s", x_tr.shape, x_te.shape)
    return x_tr, y_tr, x_te, y_te


def imdb_simple_lstm() -> Sequential:
    """1 — Simple LSTM (baseline from lab)."""
    m = Sequential(name="1_SimpleLSTM")
    m.add(Embedding(IMDB_TOP_WORDS, IMDB_EMBED_DIM, input_length=IMDB_MAX_LEN))
    m.add(LSTM(100))
    m.add(Dense(1, activation="sigmoid"))
    return m


def imdb_lstm_dropout_layers() -> Sequential:
    """2 — LSTM with Dropout as separate layers."""
    m = Sequential(name="2_LSTM_DropoutLayers")
    m.add(Embedding(IMDB_TOP_WORDS, IMDB_EMBED_DIM, input_length=IMDB_MAX_LEN))
    m.add(Dropout(0.2))
    m.add(LSTM(100))
    m.add(Dropout(0.2))
    m.add(Dense(1, activation="sigmoid"))
    return m


def imdb_lstm_recurrent_dropout() -> Sequential:
    """3 — LSTM with built-in recurrent_dropout."""
    m = Sequential(name="3_LSTM_RecurrentDropout")
    m.add(Embedding(IMDB_TOP_WORDS, IMDB_EMBED_DIM, input_length=IMDB_MAX_LEN))
    m.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    m.add(Dense(1, activation="sigmoid"))
    return m


def imdb_cnn_lstm() -> Sequential:
    """4 — CNN + LSTM (from lab instructions)."""
    m = Sequential(name="4_CNN_LSTM")
    m.add(Embedding(IMDB_TOP_WORDS, IMDB_EMBED_DIM, input_length=IMDB_MAX_LEN))
    m.add(Conv1D(filters=32, kernel_size=3, padding="same", activation="relu"))
    m.add(MaxPooling1D(pool_size=2))
    m.add(LSTM(100))
    m.add(Dense(1, activation="sigmoid"))
    return m


def imdb_cnn_lstm_dropout() -> Sequential:
    """
    5 — CNN + LSTM + Dropout  (Task 4 — modified architecture).
    Dropout after Embedding, recurrent_dropout inside LSTM,
    Dropout before Dense → strongest regularisation.
    """
    m = Sequential(name="5_CNN_LSTM_Dropout")
    m.add(Embedding(IMDB_TOP_WORDS, IMDB_EMBED_DIM, input_length=IMDB_MAX_LEN))
    m.add(Dropout(0.2))
    m.add(Conv1D(filters=32, kernel_size=3, padding="same", activation="relu"))
    m.add(MaxPooling1D(pool_size=2))
    m.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    m.add(Dropout(0.2))
    m.add(Dense(1, activation="sigmoid"))
    return m


IMDB_MODELS = {
    "1_SimpleLSTM":            imdb_simple_lstm,
    "2_LSTM_DropoutLayers":    imdb_lstm_dropout_layers,
    "3_LSTM_RecurrentDropout": imdb_lstm_recurrent_dropout,
    "4_CNN_LSTM":              imdb_cnn_lstm,
    "5_CNN_LSTM_Dropout":      imdb_cnn_lstm_dropout,
}


def run_imdb() -> dict:
    logger.info("\n%s\nUSE CASE 2 — IMDB Sentiment\n%s", "="*55, "="*55)
    x_tr, y_tr, x_te, y_te = load_imdb()

    results = {}
    for name, build_fn in IMDB_MODELS.items():
        logger.info("\n--- %s ---", name)
        model   = build_fn()
        history = compile_and_train(model, x_tr, y_tr, x_te, y_te,
                                    IMDB_EPOCHS, IMDB_BATCH)
        loss, acc = evaluate(model, x_te, y_te, name)
        results[name] = {"loss": loss, "accuracy": acc}

        plot_history(history, name, OUTPUT_DIR / f"imdb_{name.lower()}_history.png")
        model.save(str(OUTPUT_DIR / f"imdb_{name.lower()}.keras"))
        del model; K.clear_session()
        logger.info("Session cleared after %s\n", name)

    return results


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 60)
    logger.info("Lab 5 — LSTM Networks for Text Classification")
    logger.info("=" * 60)

    spam_results = run_spam()
    imdb_results = run_imdb()

    plot_comparison(spam_results, "Spam Detection — Model Comparison",
                    OUTPUT_DIR / "spam_comparison.png")
    plot_comparison(imdb_results, "IMDB Sentiment — Model Comparison",
                    OUTPUT_DIR / "imdb_comparison.png")

    logger.info("\n%s\nFINAL SUMMARY\n%s", "="*60, "="*60)

    logger.info("\n[Use Case 1 — Spam]")
    for name, r in spam_results.items():
        logger.info("  %-30s  %.2f%%  (loss %.4f)", name, r["accuracy"]*100, r["loss"])

    logger.info("\n[Use Case 2 — IMDB]")
    for name, r in imdb_results.items():
        logger.info("  %-35s  %.2f%%  (loss %.4f)", name, r["accuracy"]*100, r["loss"])

    best = max(imdb_results, key=lambda k: imdb_results[k]["accuracy"])
    logger.info("\n  Best IMDB model: %s → %.2f%%", best, imdb_results[best]["accuracy"]*100)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()