import argparse
import logging
import sys
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = '0'
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from keras.models import load_model
from skimage.transform import resize


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


CLASS_NAMES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]
IMAGE_SHAPE = (32, 32, 3)
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_and_preprocess_image(image_path: Path) -> np.ndarray:
    """Read an image from disk and resize it to 32×32×3."""
    raw = plt.imread(str(image_path))

    # Convert RGBA → RGB if needed
    if raw.ndim == 2:
        raw = np.stack([raw] * 3, axis=-1)
    elif raw.shape[2] == 4:
        raw = raw[:, :, :3]

    resized = resize(raw, IMAGE_SHAPE, anti_aliasing=True)

    # Ensure float32 in [0, 1]
    if resized.max() > 1.0:
        resized = resized.astype("float32") / 255.0

    return resized.astype("float32")


def predict_single(model, image_path: Path, top_k: int = 5) -> dict:
    """Run inference on a single image and return a result dict."""
    image = load_and_preprocess_image(image_path)
    tensor = np.expand_dims(image, axis=0)  # (1, 32, 32, 3)
    probs = model.predict(tensor, verbose=0)[0]
    ranked = np.argsort(probs)[::-1]

    result = {
        "image_path": image_path,
        "image_array": image,
        "top_label": CLASS_NAMES[ranked[0]],
        "top_confidence": float(probs[ranked[0]]),
        "top_k": [
            {"class": CLASS_NAMES[i], "confidence": float(probs[i])}
            for i in ranked[:top_k]
        ],
    }

    logger.info("%-30s → %-12s (%.1f%%)",
                image_path.name,
                result["top_label"],
                result["top_confidence"] * 100)
    return result


def visualize_batch_results(results: list, save_path: Path | None = None) -> None:
    """Display a compact grid of images with their top predictions."""
    n = len(results)
    cols = min(n, 5)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3.5))
    axes = np.array(axes).reshape(-1)  # flatten for easy iteration
    fig.suptitle("Custom Image Predictions", fontsize=14, fontweight="bold")

    for ax, res in zip(axes, results):
        ax.imshow(res["image_array"])
        label = f'{res["top_label"]}\n{res["top_confidence"]*100:.1f}%'
        ax.set_title(label, fontsize=9)
        ax.axis("off")

    # Hide unused axes
    for ax in axes[n:]:
        ax.set_visible(False)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Batch prediction grid saved → %s", save_path)
    plt.show()


def predict_batch(model, image_paths: list[Path], output_dir: Path) -> None:
    """Run inference on a list of image paths and visualise results."""
    if not image_paths:
        logger.warning("No images to predict.")
        return

    results = []
    for path in image_paths:
        try:
            results.append(predict_single(model, path))
        except Exception as exc:
            logger.error("Failed to process %s: %s", path.name, exc)

    output_dir.mkdir(parents=True, exist_ok=True)
    visualize_batch_results(results, save_path=output_dir / "batch_predictions.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CIFAR-10 custom image inference")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("outputs/improved_model.keras"),
        help="Path to the saved .keras model file",
    )
    parser.add_argument(
        "--images",
        nargs="*",
        type=Path,
        default=[],
        help="One or more image file paths",
    )
    parser.add_argument(
        "--images_dir",
        type=Path,
        default=None,
        help="Directory of images to classify",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("outputs"),
        help="Where to save the prediction plot",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Collect image paths
    image_paths: list[Path] = list(args.images)
    if args.images_dir and args.images_dir.is_dir():
        image_paths += [
            p for p in args.images_dir.iterdir()
            if p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    if not image_paths:
        logger.error("No images provided. Use --images or --images_dir.")
        sys.exit(1)

    # Load model
    if not args.model.exists():
        logger.error("Model file not found: %s", args.model)
        sys.exit(1)

    logger.info("Loading model from %s …", args.model)
    model = load_model(str(args.model))
    logger.info("Model loaded.")

    # Run inference
    predict_batch(model, image_paths, args.output_dir)


if __name__ == "__main__":
    main()