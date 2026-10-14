import logging
import sys
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import (
    Conv2D,
    Dense,
    Input,
    MaxPool2D,
    UpSampling2D,
)
from keras.models import Model
from sklearn.model_selection import train_test_split

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("lab4_training.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
DATA_PATH   = Path("fashion-mnist_train.csv")
OUTPUT_DIR  = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

IMAGE_SIZE  = 28
FLAT_SIZE   = IMAGE_SIZE * IMAGE_SIZE   # 784
NUM_CLASSES = 10
CLASS_NAMES = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot",
]

BATCH_SIZE      = 256    # larger batches → fewer steps per epoch on CPU
EPOCHS          = 20     # EarlyStopping will stop earlier
VAL_SIZE        = 0.2
NOISE_FACTOR    = 0.1    # Salt-and-pepper probability / Gaussian sigma scale
TRAIN_SUBSET    = 15_000 # use a subset for faster CPU training (set None to use all)


# ─────────────────────────────────────────────
# 1. Data Loading & Preprocessing
# ─────────────────────────────────────────────
def load_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load Fashion-MNIST CSV, normalize pixels, split train/val."""
    logger.info("Loading dataset from '%s' …", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    labels = df["label"].values
    pixels = df.drop(columns=["label"]).values.astype("float32") / 255.0

    x_train, x_val, y_train, y_val = train_test_split(
        pixels, labels, test_size=VAL_SIZE, random_state=42, stratify=labels
    )

    # ── Optional subset for faster CPU training ──────────────────
    if TRAIN_SUBSET is not None and TRAIN_SUBSET < len(x_train):
        rng = np.random.default_rng(seed=42)
        idx = rng.choice(len(x_train), TRAIN_SUBSET, replace=False)
        x_train, y_train = x_train[idx], y_train[idx]
        logger.info("Using subset: train=%d  val=%d  (full train was %d)",
                    len(x_train), len(x_val), len(pixels) - len(x_val))
    else:
        logger.info("Dataset loaded: train=%d  val=%d  features=%d",
                    len(x_train), len(x_val), pixels.shape[1])

    return x_train, x_val, y_train, y_val


def to_images(x_flat: np.ndarray) -> np.ndarray:
    """Reshape flat (N, 784) → (N, 28, 28, 1) for CNN."""
    return x_flat.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 1)


# ─────────────────────────────────────────────
# 2. Noise Generators
# ─────────────────────────────────────────────
def add_salt_and_pepper(x: np.ndarray, prob: float = NOISE_FACTOR) -> np.ndarray:
    """
    Randomly set pixels to 0 (pepper) or 1 (salt).
    prob — fraction of pixels affected.
    """
    noisy = x.copy()
    rng   = np.random.default_rng(seed=0)
    mask_salt   = rng.random(x.shape) < prob / 2
    mask_pepper = rng.random(x.shape) < prob / 2
    noisy[mask_salt]   = 1.0
    noisy[mask_pepper] = 0.0
    return np.clip(noisy, 0.0, 1.0)


def add_gaussian_noise(x: np.ndarray, sigma: float = NOISE_FACTOR) -> np.ndarray:
    """Add zero-mean Gaussian noise with standard deviation sigma."""
    rng   = np.random.default_rng(seed=0)
    noise = rng.normal(loc=0.0, scale=sigma, size=x.shape).astype("float32")
    return np.clip(x + noise, 0.0, 1.0)


def add_speckle_noise(x: np.ndarray, sigma: float = NOISE_FACTOR) -> np.ndarray:
    """
    Speckle (multiplicative) noise: noisy = x + x * N(0, sigma).
    Common in radar / ultrasound imagery.
    """
    rng   = np.random.default_rng(seed=0)
    noise = rng.normal(loc=0.0, scale=sigma, size=x.shape).astype("float32")
    return np.clip(x + x * noise, 0.0, 1.0)


NOISE_FNS = {
    "salt_and_pepper": add_salt_and_pepper,
    "gaussian":        add_gaussian_noise,
    "speckle":         add_speckle_noise,
}


# ─────────────────────────────────────────────
# 3. Deep (Dense) Autoencoder
# ─────────────────────────────────────────────
def build_deep_autoencoder_baseline() -> tuple[Model, Model, Model]:
    """
    Baseline Deep Autoencoder from the lab instructions.
    Latent dim = 10.
    Returns: (autoencoder, encoder, decoder)
    """
    # ── Encoder ──────────────────────────────
    inp = Input(shape=(FLAT_SIZE,), name="input")
    x   = Dense(1500, activation="relu", name="enc_1")(inp)
    x   = Dense(1000, activation="relu", name="enc_2")(x)
    x   = Dense(500,  activation="relu", name="enc_3")(x)
    latent = Dense(10, activation="sigmoid", name="latent")(x)

    # ── Decoder ──────────────────────────────
    x   = Dense(500,      activation="relu", name="dec_1")(latent)
    x   = Dense(1000,     activation="relu", name="dec_2")(x)
    x   = Dense(1500,     activation="relu", name="dec_3")(x)
    out = Dense(FLAT_SIZE, activation="sigmoid", name="output")(x)

    autoencoder = Model(inp, out,    name="DeepAE_Baseline")
    encoder     = Model(inp, latent, name="Encoder_Baseline")

    # Standalone decoder
    dec_inp = Input(shape=(10,), name="latent_input")
    dec_out = autoencoder.layers[-4](dec_inp)
    dec_out = autoencoder.layers[-3](dec_out)
    dec_out = autoencoder.layers[-2](dec_out)
    dec_out = autoencoder.layers[-1](dec_out)
    decoder = Model(dec_inp, dec_out, name="Decoder_Baseline")

    return autoencoder, encoder, decoder


def build_deep_autoencoder_improved() -> tuple[Model, Model, Model]:
    """
    Improved Deep Autoencoder:
      - Larger latent dim (32) for better reconstruction
      - Additional hidden layers
      - Activation: relu in all layers, sigmoid on output
    """
    LATENT_DIM = 32

    inp = Input(shape=(FLAT_SIZE,), name="input")
    x   = Dense(1024, activation="relu", name="enc_1")(inp)
    x   = Dense(512,  activation="relu", name="enc_2")(x)
    x   = Dense(256,  activation="relu", name="enc_3")(x)
    x   = Dense(128,  activation="relu", name="enc_4")(x)
    latent = Dense(LATENT_DIM, activation="relu", name="latent")(x)

    x   = Dense(128,      activation="relu", name="dec_1")(latent)
    x   = Dense(256,      activation="relu", name="dec_2")(x)
    x   = Dense(512,      activation="relu", name="dec_3")(x)
    x   = Dense(1024,     activation="relu", name="dec_4")(x)
    out = Dense(FLAT_SIZE, activation="sigmoid", name="output")(x)

    autoencoder = Model(inp, out,    name="DeepAE_Improved")
    encoder     = Model(inp, latent, name="Encoder_Improved")

    dec_inp = Input(shape=(LATENT_DIM,), name="latent_input")
    dec_out = autoencoder.layers[-5](dec_inp)
    dec_out = autoencoder.layers[-4](dec_out)
    dec_out = autoencoder.layers[-3](dec_out)
    dec_out = autoencoder.layers[-2](dec_out)
    dec_out = autoencoder.layers[-1](dec_out)
    decoder = Model(dec_inp, dec_out, name="Decoder_Improved")

    return autoencoder, encoder, decoder


# ─────────────────────────────────────────────
# 4. Convolutional Autoencoder
# ─────────────────────────────────────────────
def build_conv_autoencoder_baseline() -> Model:
    """
    Baseline Convolutional Autoencoder from the lab instructions.
    Encoder: 3× (Conv2D + MaxPool2D)
    Decoder: 3× (Conv2D + UpSampling2D)
    """
    inp = Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 1), name="input")

    # Encoder
    x = Conv2D(64, (3, 3), activation="relu", padding="same", name="enc_conv1")(inp)
    x = MaxPool2D((2, 2), padding="same", name="enc_pool1")(x)
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="enc_conv2")(x)
    x = MaxPool2D((2, 2), padding="same", name="enc_pool2")(x)
    x = Conv2D(16, (3, 3), activation="relu", padding="same", name="enc_conv3")(x)
    latent = MaxPool2D((2, 2), padding="same", name="latent")(x)

    # Decoder
    x = Conv2D(16, (3, 3), activation="relu", padding="same", name="dec_conv1")(latent)
    x = UpSampling2D((2, 2), name="dec_up1")(x)
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="dec_conv2")(x)
    x = UpSampling2D((2, 2), name="dec_up2")(x)
    x = Conv2D(64, (3, 3), activation="relu", name="dec_conv3")(x)
    x = UpSampling2D((2, 2), name="dec_up3")(x)
    out = Conv2D(1, (3, 3), activation="sigmoid", padding="same", name="output")(x)

    return Model(inp, out, name="ConvAE_Baseline")


def build_conv_autoencoder_improved() -> Model:
    """
    Improved Convolutional Autoencoder — CPU-friendly version.
    Changes vs baseline:
      - 3 encoder blocks (same depth) but wider: 32→64→32 filters
      - Extra Conv2D before each pooling for richer feature maps
      - sigmoid on final Conv for stable [0,1] output
      - Total params ≈ 3× baseline but still fits comfortably in RAM
    """
    inp = Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 1), name="input")

    # ── Encoder ──────────────────────────────────────────────────
    # Block 1: 28×28 → 14×14
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="enc_conv1a")(inp)
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="enc_conv1b")(x)
    x = MaxPool2D((2, 2), padding="same", name="enc_pool1")(x)

    # Block 2: 14×14 → 7×7
    x = Conv2D(64, (3, 3), activation="relu", padding="same", name="enc_conv2a")(x)
    x = Conv2D(64, (3, 3), activation="relu", padding="same", name="enc_conv2b")(x)
    x = MaxPool2D((2, 2), padding="same", name="enc_pool2")(x)

    # Block 3 (latent): 7×7 → 4×4
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="enc_conv3")(x)
    latent = MaxPool2D((2, 2), padding="same", name="latent")(x)

    # ── Decoder ──────────────────────────────────────────────────
    # Block 1: 4×4 → 8×8
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="dec_conv1")(latent)
    x = UpSampling2D((2, 2), name="dec_up1")(x)

    # Block 2: 8×8 → 16×16
    x = Conv2D(64, (3, 3), activation="relu", padding="same", name="dec_conv2a")(x)
    x = Conv2D(64, (3, 3), activation="relu", padding="same", name="dec_conv2b")(x)
    x = UpSampling2D((2, 2), name="dec_up2")(x)

    # Block 3: 16×16 → 32×32
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="dec_conv3a")(x)
    x = Conv2D(32, (3, 3), activation="relu", padding="same", name="dec_conv3b")(x)
    x = UpSampling2D((2, 2), name="dec_up3")(x)

    # Final: crop 32→28 via valid padding on 5×5 kernel
    out = Conv2D(1, (5, 5), activation="sigmoid", padding="valid", name="output")(x)

    return Model(inp, out, name="ConvAE_Improved")


# ─────────────────────────────────────────────
# 5. Training
# ─────────────────────────────────────────────
def get_callbacks() -> list:
    return [
        EarlyStopping(
            monitor="val_loss",
            patience=4,              # stop sooner on CPU
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,              # reduce LR faster
            min_lr=1e-6,
            verbose=1,
        ),
    ]


def train_autoencoder(
    model: Model,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    learning_rate: float = 1e-3,
) -> dict:
    """
    Compile and train an autoencoder.
    x/y_train may differ for denoising (x=noisy, y=clean).
    """
    from keras.optimizers import Adam

    model.compile(optimizer=Adam(learning_rate=learning_rate), loss="mse")
    logger.info("Training '%s': params=%s  input=%s → target=%s",
                model.name,
                f"{model.count_params():,}",
                x_train.shape,
                y_train.shape)
    model.summary(print_fn=logger.info)

    history = model.fit(
        x_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(x_val, y_val),
        callbacks=get_callbacks(),
        verbose=1,
    )
    logger.info("Training complete. Best val_loss: %.6f",
                min(history.history["val_loss"]))
    return history.history


# ─────────────────────────────────────────────
# 6. Visualisation helpers
# ─────────────────────────────────────────────
def plot_training_history(
    histories: dict[str, dict],
    save_path: Optional[Path] = None,
) -> None:
    """Overlay val_loss curves for multiple models."""
    plt.figure(figsize=(10, 5))
    plt.title("Validation Loss Comparison", fontsize=13, fontweight="bold")
    for name, h in histories.items():
        plt.plot(h["val_loss"], label=name, linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Loss comparison saved → %s", save_path)
    plt.show()


def plot_reconstructions(
    originals: np.ndarray,
    reconstructions: np.ndarray,
    model_name: str,
    n: int = 8,
    noisy: Optional[np.ndarray] = None,
    save_path: Optional[Path] = None,
) -> None:
    """
    Display original vs reconstructed images.
    If noisy is provided, shows 3 rows: original | noisy | reconstructed.
    """
    rows = 3 if noisy is not None else 2
    fig, axes = plt.subplots(rows, n, figsize=(n * 1.8, rows * 2))
    fig.suptitle(f"Reconstructions — {model_name}", fontsize=13, fontweight="bold")

    titles = ["Original", "Noisy", "Reconstructed"] if noisy is not None else ["Original", "Reconstructed"]

    for col in range(n):
        img_orig  = originals[col].reshape(IMAGE_SIZE, IMAGE_SIZE)
        img_recon = reconstructions[col].reshape(IMAGE_SIZE, IMAGE_SIZE)

        axes[0, col].imshow(img_orig,  cmap="gray")
        axes[0, col].axis("off")
        if col == 0:
            axes[0, col].set_ylabel(titles[0], fontsize=9, rotation=0, labelpad=40)

        if noisy is not None:
            img_noisy = noisy[col].reshape(IMAGE_SIZE, IMAGE_SIZE)
            axes[1, col].imshow(img_noisy, cmap="gray")
            axes[1, col].axis("off")
            if col == 0:
                axes[1, col].set_ylabel(titles[1], fontsize=9, rotation=0, labelpad=40)

            axes[2, col].imshow(img_recon, cmap="gray")
            axes[2, col].axis("off")
            if col == 0:
                axes[2, col].set_ylabel(titles[2], fontsize=9, rotation=0, labelpad=40)
        else:
            axes[1, col].imshow(img_recon, cmap="gray")
            axes[1, col].axis("off")
            if col == 0:
                axes[1, col].set_ylabel(titles[1], fontsize=9, rotation=0, labelpad=40)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Reconstruction plot saved → %s", save_path)
    plt.show()


def plot_noise_comparison(
    clean: np.ndarray,
    denoised: dict[str, np.ndarray],
    n: int = 5,
    save_path: Optional[Path] = None,
) -> None:
    """Show clean vs denoised for all noise types side by side."""
    noise_types = list(denoised.keys())
    rows = 1 + len(noise_types)
    fig, axes = plt.subplots(rows, n, figsize=(n * 2, rows * 2.2))
    fig.suptitle("Denoising Comparison — Noise Types", fontsize=13, fontweight="bold")

    for col in range(n):
        axes[0, col].imshow(clean[col].reshape(IMAGE_SIZE, IMAGE_SIZE), cmap="gray")
        axes[0, col].axis("off")
        if col == 0:
            axes[0, col].set_ylabel("Clean", fontsize=9, rotation=0, labelpad=40)

        for row, ntype in enumerate(noise_types, start=1):
            axes[row, col].imshow(denoised[ntype][col].reshape(IMAGE_SIZE, IMAGE_SIZE), cmap="gray")
            axes[row, col].axis("off")
            if col == 0:
                axes[row, col].set_ylabel(ntype.replace("_", " ").title(),
                                          fontsize=9, rotation=0, labelpad=40)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Noise comparison saved → %s", save_path)
    plt.show()


def compute_mse(originals: np.ndarray, reconstructions: np.ndarray) -> float:
    """Pixel-level Mean Squared Error between originals and reconstructions."""
    return float(np.mean((originals - reconstructions) ** 2))


# ─────────────────────────────────────────────
# 7. Main Pipeline
# ─────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 60)
    logger.info("Lab 4 — Autoencoders (Fashion-MNIST)")
    logger.info("=" * 60)

    # ── Load data ─────────────────────────────
    x_train_flat, x_val_flat, _, _ = load_data()
    x_train_img = to_images(x_train_flat)   # (N, 28, 28, 1)
    x_val_img   = to_images(x_val_flat)

    histories = {}     # for comparison plot
    results   = {}     # val_loss summary

    # ══════════════════════════════════════════
    # USE CASE 1 — IMAGE RECONSTRUCTION
    # ══════════════════════════════════════════
    logger.info("\n%s\nUSE CASE 1 — Image Reconstruction\n%s", "─"*50, "─"*50)

    # ── 1a. Baseline Deep AE ──────────────────
    logger.info("--- Baseline Deep Autoencoder ---")
    deep_ae_base, _, _ = build_deep_autoencoder_baseline()
    h_deep_base = train_autoencoder(
        deep_ae_base,
        x_train_flat, x_train_flat,
        x_val_flat,   x_val_flat,
    )
    histories["DeepAE Baseline"] = h_deep_base
    preds_deep_base = deep_ae_base.predict(x_val_flat[:8], verbose=0)
    results["DeepAE Baseline"] = min(h_deep_base["val_loss"])
    plot_reconstructions(
        x_val_flat[:8], preds_deep_base,
        model_name="Deep AE Baseline",
        save_path=OUTPUT_DIR / "recon_deep_baseline.png",
    )
    deep_ae_base.save(str(OUTPUT_DIR / "deep_ae_baseline.keras"))

    # ── 1b. Improved Deep AE ─────────────────
    logger.info("--- Improved Deep Autoencoder ---")
    deep_ae_imp, _, _ = build_deep_autoencoder_improved()
    h_deep_imp = train_autoencoder(
        deep_ae_imp,
        x_train_flat, x_train_flat,
        x_val_flat,   x_val_flat,
    )
    histories["DeepAE Improved"] = h_deep_imp
    preds_deep_imp = deep_ae_imp.predict(x_val_flat[:8], verbose=0)
    results["DeepAE Improved"] = min(h_deep_imp["val_loss"])
    plot_reconstructions(
        x_val_flat[:8], preds_deep_imp,
        model_name="Deep AE Improved",
        save_path=OUTPUT_DIR / "recon_deep_improved.png",
    )
    deep_ae_imp.save(str(OUTPUT_DIR / "deep_ae_improved.keras"))

    # ══════════════════════════════════════════
    # USE CASE 2 — IMAGE DENOISING
    # ══════════════════════════════════════════
    logger.info("\n%s\nUSE CASE 2 — Image Denoising\n%s", "─"*50, "─"*50)

    # Apply Salt & Pepper noise (as in the lab)
    x_train_noisy_img = to_images(add_salt_and_pepper(x_train_flat))
    x_val_noisy_img   = to_images(add_salt_and_pepper(x_val_flat))

    # ── 2a. Baseline Conv AE ──────────────────
    logger.info("--- Baseline Convolutional Autoencoder ---")
    conv_ae_base = build_conv_autoencoder_baseline()
    h_conv_base = train_autoencoder(
        conv_ae_base,
        x_train_noisy_img, x_train_img,   # input=noisy, target=clean
        x_val_noisy_img,   x_val_img,
    )
    histories["ConvAE Baseline"] = h_conv_base
    preds_conv_base = conv_ae_base.predict(x_val_noisy_img[:8], verbose=0)
    results["ConvAE Baseline"] = min(h_conv_base["val_loss"])
    plot_reconstructions(
        x_val_img[:8], preds_conv_base,
        model_name="Conv AE Baseline (Salt&Pepper denoising)",
        noisy=x_val_noisy_img[:8],
        save_path=OUTPUT_DIR / "recon_conv_baseline.png",
    )
    conv_ae_base.save(str(OUTPUT_DIR / "conv_ae_baseline.keras"))

    # ── 2b. Improved Conv AE ─────────────────
    logger.info("--- Improved Convolutional Autoencoder ---")
    conv_ae_imp = build_conv_autoencoder_improved()
    h_conv_imp = train_autoencoder(
        conv_ae_imp,
        x_train_noisy_img, x_train_img,
        x_val_noisy_img,   x_val_img,
    )
    histories["ConvAE Improved"] = h_conv_imp
    preds_conv_imp = conv_ae_imp.predict(x_val_noisy_img[:8], verbose=0)
    results["ConvAE Improved"] = min(h_conv_imp["val_loss"])
    plot_reconstructions(
        x_val_img[:8], preds_conv_imp,
        model_name="Conv AE Improved (Salt&Pepper denoising)",
        noisy=x_val_noisy_img[:8],
        save_path=OUTPUT_DIR / "recon_conv_improved.png",
    )
    conv_ae_imp.save(str(OUTPUT_DIR / "conv_ae_improved.keras"))

    # ══════════════════════════════════════════
    # USE CASE 3 — NOISE TYPE COMPARISON (п.5)
    # ══════════════════════════════════════════
    logger.info("\n%s\nUSE CASE 3 — Noise Type Comparison\n%s", "─"*50, "─"*50)

    sample_clean = x_val_flat[:8]
    denoised_by_type: dict[str, np.ndarray] = {}

    for noise_name, noise_fn in NOISE_FNS.items():
        logger.info("Testing noise type: %s", noise_name)
        x_train_n = to_images(noise_fn(x_train_flat))
        x_val_n   = to_images(noise_fn(x_val_flat))

        # Train a fresh Conv AE for each noise type
        model = build_conv_autoencoder_improved()
        train_autoencoder(
            model,
            x_train_n, x_train_img,
            x_val_n,   x_val_img,
        )
        preds = model.predict(x_val_n[:8], verbose=0)  # shape (8,28,28,1)
        denoised_by_type[noise_name] = preds.reshape(8, -1)

        mse = compute_mse(sample_clean, denoised_by_type[noise_name])
        logger.info("  Noise: %-20s  Reconstruction MSE: %.6f", noise_name, mse)
        results[f"ConvAE {noise_name}"] = mse

    plot_noise_comparison(
        sample_clean,
        denoised_by_type,
        save_path=OUTPUT_DIR / "noise_comparison.png",
    )

    # ── Overlaid loss curves ──────────────────
    plot_training_history(
        histories,
        save_path=OUTPUT_DIR / "val_loss_comparison.png",
    )

    # ── Final summary ─────────────────────────
    logger.info("\n%s", "=" * 60)
    logger.info("FINAL SUMMARY (best val_loss / MSE)")
    logger.info("%-30s  %s", "Model", "Best val_loss")
    logger.info("-" * 50)
    for name, val in results.items():
        logger.info("  %-28s  %.6f", name, val)

    logger.info("\nKey insight:")
    deep_best = min(results["DeepAE Baseline"], results["DeepAE Improved"])
    conv_best = min(results["ConvAE Baseline"], results["ConvAE Improved"])
    if conv_best < deep_best:
        logger.info("  ConvAE outperforms DeepAE (%.6f < %.6f).", conv_best, deep_best)
        logger.info("  CNN captures local spatial features better → lower reconstruction error.")
    else:
        logger.info("  DeepAE outperforms ConvAE on this run (%.6f < %.6f).", deep_best, conv_best)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()