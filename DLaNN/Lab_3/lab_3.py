import logging
import sys
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from keras.datasets import cifar10
from keras.layers import (
    BatchNormalization,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    MaxPooling2D,
)
from keras.models import Sequential, load_model
from keras.optimizers import Adam
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from skimage.transform import resize


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lab3.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

CLASS_NAMES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]
NUM_CLASSES = len(CLASS_NAMES)
IMAGE_SHAPE = (32, 32, 3)
BASELINE_ACCURACY = 0.7043  # threshold to beat

BATCH_SIZE = 256
EPOCHS = 30
VALIDATION_SPLIT = 0.2

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_explore_data() -> tuple:
    """Load and explore the CIFAR-10 dataset."""
    logger.info("Loading CIFAR-10 dataset …")
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    logger.info("Dataset loaded successfully.")
    logger.info("--- Data types ---")
    logger.info("x_train: %s | y_train: %s", type(x_train), type(y_train))
    logger.info("x_test:  %s | y_test:  %s", type(x_test),  type(y_test))

    logger.info("--- Shapes ---")
    logger.info("x_train: %s  y_train: %s", x_train.shape, y_train.shape)
    logger.info("x_test:  %s  y_test:  %s", x_test.shape,  y_test.shape)

    logger.info("--- Pixel value range ---")
    logger.info("min=%d  max=%d", x_train.min(), x_train.max())

    return x_train, y_train, x_test, y_test


def visualize_samples(
    x: np.ndarray,
    y: np.ndarray,
    n: int = 10,
    save_path: Optional[Path] = None,
) -> None:
    """Display a grid of n random training samples with their class labels."""
    indices = np.random.choice(len(x), n, replace=False)
    fig, axes = plt.subplots(2, n // 2, figsize=(14, 6))
    fig.suptitle("Random CIFAR-10 Samples", fontsize=14, fontweight="bold")

    for ax, idx in zip(axes.flat, indices):
        ax.imshow(x[idx])
        ax.set_title(CLASS_NAMES[y[idx][0]], fontsize=9)
        ax.axis("off")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Sample grid saved → %s", save_path)
    plt.show()


def preprocess(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
) -> tuple:
    """Normalize pixel values and apply one-hot encoding to labels."""
    logger.info("Normalizing pixel values to [0, 1] …")
    x_train = x_train.astype("float32") / 255.0
    x_test  = x_test.astype("float32") / 255.0

    logger.info("Applying one-hot encoding (num_classes=%d) …", NUM_CLASSES)
    y_train_ohe = to_categorical(y_train, NUM_CLASSES)
    y_test_ohe  = to_categorical(y_test,  NUM_CLASSES)

    logger.info("Example label mapping: %d → %s", y_train[0][0], y_train_ohe[0])
    return x_train, y_train_ohe, x_test, y_test_ohe


def build_baseline_model() -> Sequential:
    """
    Baseline CNN as described in the lab instructions.
    Expected accuracy: ~70.43%.
    """
    model = Sequential(name="Baseline_CNN")

    model.add(Conv2D(32, (5, 5), activation="relu", input_shape=IMAGE_SHAPE))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (5, 5), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(1000, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(500, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(250, activation="relu"))
    model.add(Dense(NUM_CLASSES, activation="softmax"))

    return model


def build_improved_model() -> Sequential:
    """
    Improved CNN with:
      - More convolutional blocks (3 instead of 2)
      - Smaller 3×3 kernels (more expressive than 5×5)
      - BatchNormalization after each Conv2D (faster convergence, less overfitting)
      - Reduced Dropout rates (0.3 instead of 0.5)
      - Fewer Dense neurons (avoids overfitting on small images)

    Target accuracy: > 70.43%.
    """
    model = Sequential(name="Improved_CNN")

    model.add(Conv2D(32, (3, 3), activation="relu", padding="same", input_shape=IMAGE_SHAPE))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3, 3), activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))

    model.add(Conv2D(64, (3, 3), activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.3))

    model.add(Conv2D(128, (3, 3), activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3, 3), activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.4))

    model.add(Flatten())
    model.add(Dense(512, activation="relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation="softmax"))

    return model


def compile_model(model: Sequential, learning_rate: float = 1e-3) -> None:
    """Compile the model with Adam optimizer and categorical cross-entropy loss."""
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    logger.info("Model '%s' compiled. Summary:", model.name)
    model.summary(print_fn=logger.info)


def get_callbacks(model_name: str) -> list:
    """Return standard training callbacks."""
    checkpoint_path = OUTPUT_DIR / f"{model_name}_best.keras"
    return [
        EarlyStopping(
            monitor="val_accuracy",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]


def train_model(
    model: Sequential,
    x_train: np.ndarray,
    y_train: np.ndarray,
) -> dict:
    """Train the model and return the history object."""
    logger.info("Starting training: epochs=%d  batch_size=%d", EPOCHS, BATCH_SIZE)
    history = model.fit(
        x_train,
        y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_split=VALIDATION_SPLIT,
        callbacks=get_callbacks(model.name),
        verbose=1,
    )
    logger.info("Training complete.")
    return history.history


def evaluate_model(
    model: Sequential,
    x_test: np.ndarray,
    y_test: np.ndarray,
    label: str = "",
) -> float:
    """Evaluate model on the test set and log accuracy."""
    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    logger.info("[%s] Test loss: %.4f | Test accuracy: %.4f (%.2f%%)",
                label, loss, accuracy, accuracy * 100)
    if accuracy > BASELINE_ACCURACY:
        logger.info("✅ Baseline accuracy beaten! (%.2f%% > %.2f%%)",
                    accuracy * 100, BASELINE_ACCURACY * 100)
    else:
        logger.warning("❌ Did not beat baseline (%.2f%% ≤ %.2f%%)",
                       accuracy * 100, BASELINE_ACCURACY * 100)
    return accuracy


def plot_training_history(
    history: dict,
    model_name: str,
    save_path: Optional[Path] = None,
) -> None:
    """
    Plot accuracy and loss curves for training and validation.
    Helps identify overfitting.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Training History — {model_name}", fontsize=14, fontweight="bold")

    # Accuracy
    ax1.plot(history["accuracy"],     label="Train", linewidth=2)
    ax1.plot(history["val_accuracy"], label="Validation", linewidth=2, linestyle="--")
    ax1.set_title("Model Accuracy")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.legend(loc="lower right")
    ax1.grid(alpha=0.3)

    # Loss
    ax2.plot(history["loss"],     label="Train", linewidth=2)
    ax2.plot(history["val_loss"], label="Validation", linewidth=2, linestyle="--")
    ax2.set_title("Model Loss")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Training history plot saved → %s", save_path)
    plt.show()


def check_overfitting(history: dict, model_name: str) -> None:
    """Analyse training history and log whether overfitting is detected."""
    train_acc = history["accuracy"][-1]
    val_acc   = history["val_accuracy"][-1]
    gap = train_acc - val_acc

    logger.info("--- Overfitting analysis [%s] ---", model_name)
    logger.info("Final train accuracy:      %.4f", train_acc)
    logger.info("Final validation accuracy: %.4f", val_acc)
    logger.info("Gap (train − val):         %.4f", gap)

    if gap > 0.10:
        logger.warning("⚠️  Likely OVERFITTING detected (gap > 10%%). "
                       "Consider: more Dropout, data augmentation, fewer parameters.")
    elif gap > 0.05:
        logger.warning("⚠️  Mild overfitting (gap 5–10%%). Monitor closely.")
    else:
        logger.info("✅ No significant overfitting detected (gap ≤ 5%%).")


def save_model(model: Sequential, filename: str) -> None:
    path = OUTPUT_DIR / filename
    model.save(str(path))
    logger.info("Model saved → %s", path)


def load_saved_model(filename: str) -> Sequential:
    path = OUTPUT_DIR / filename
    logger.info("Loading model from %s …", path)
    return load_model(str(path))


def main() -> None:
    x_train, y_train, x_test, y_test = load_and_explore_data()
    visualize_samples(
        x_train, y_train, n=10,
        save_path=OUTPUT_DIR / "sample_grid.png",
    )

    x_train, y_train_ohe, x_test, y_test_ohe = preprocess(
        x_train, y_train, x_test, y_test
    )

    logger.info("\n%s\nTraining BASELINE model …\n%s", "─"*40, "─"*40)
    baseline = build_baseline_model()
    compile_model(baseline, learning_rate=1e-3)
    baseline_history = train_model(baseline, x_train, y_train_ohe)
    baseline_acc = evaluate_model(baseline, x_test, y_test_ohe, label="Baseline")
    plot_training_history(
        baseline_history,
        model_name="Baseline CNN",
        save_path=OUTPUT_DIR / "baseline_history.png",
    )
    check_overfitting(baseline_history, "Baseline CNN")
    save_model(baseline, "baseline_model.keras")

    logger.info("\n%s\nTraining IMPROVED model …\n%s", "─"*40, "─"*40)
    improved = build_improved_model()
    compile_model(improved, learning_rate=1e-3)
    improved_history = train_model(improved, x_train, y_train_ohe)
    improved_acc = evaluate_model(improved, x_test, y_test_ohe, label="Improved")
    plot_training_history(
        improved_history,
        model_name="Improved CNN",
        save_path=OUTPUT_DIR / "improved_history.png",
    )
    check_overfitting(improved_history, "Improved CNN")
    save_model(improved, "improved_model.keras")

    logger.info("\n%s", "=" * 60)
    logger.info("SUMMARY")
    logger.info("  Baseline accuracy : %.2f%%", baseline_acc * 100)
    logger.info("  Improved accuracy : %.2f%%", improved_acc * 100)
    logger.info("  Improvement       : +%.2f pp", (improved_acc - baseline_acc) * 100)
    logger.info("%s", "=" * 60)


if __name__ == "__main__":
    main()