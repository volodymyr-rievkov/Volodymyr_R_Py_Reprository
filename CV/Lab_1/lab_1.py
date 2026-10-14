"""Lab 1, variant 2: 2D linear filtering (convolution) with different kernels.

Only numpy does the work; matplotlib is used to read, show and save images.
"""

import itertools
import logging
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

Image = NDArray[np.float64]

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "outputs"

IMAGES = ("detail_high", "detail_low", "contrast_high", "contrast_low")
IMAGE_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED_INK = "#52514e"

MAX_PIXEL = 255.0
GRAY_WEIGHTS = np.array([0.299, 0.587, 0.114])
FIGURE_DPI = 70
JPEG_QUALITY = 60
GRID_COLUMNS = 5
CORNER_SIZE = 40
BAR_WIDTH = 0.2


def box_kernel(size: int) -> Image:
    return np.full((size, size), 1.0 / size**2)


def gaussian_kernel(size: int, sigma: float) -> Image:
    """Sampled Gaussian, outer product of two 1D profiles, normalised to sum 1."""
    x = np.arange(size) - size // 2
    profile = np.exp(-(x**2) / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))
    kernel = np.outer(profile, profile)
    return kernel / kernel.sum()


def motion_kernel(length: int) -> Image:
    return np.full((1, length), 1.0 / length)


KERNELS: dict[str, Image] = {
    "identity": np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]),
    "box_3": box_kernel(3),
    "box_7": box_kernel(7),
    "gauss_5_s1": gaussian_kernel(5, 1.0),
    "gauss_9_s2": gaussian_kernel(9, 2.0),
    "motion_9": motion_kernel(9),
    "sharpen": np.array([[0.0, -1.0, 0.0], [-1.0, 5.0, -1.0], [0.0, -1.0, 0.0]]),
    "laplacian": np.array([[1.0, 1.0, 1.0], [1.0, -8.0, 1.0], [1.0, 1.0, 1.0]]),
    "emboss": np.array([[-2.0, -1.0, 0.0], [-1.0, 1.0, 1.0], [0.0, 1.0, 2.0]]),
}
SIGNED_KERNELS = frozenset({"laplacian", "emboss"})


def load_gray(path: Path) -> Image:
    """Read an RGB image and convert it to grayscale in [0, 255]."""
    raw = mpimg.imread(path)
    scale = 1.0 if raw.dtype == np.uint8 else MAX_PIXEL
    return raw[..., :3].astype(np.float64) * scale @ GRAY_WEIGHTS


def _border_index(size: int, pad: int, mode: str) -> NDArray[np.intp]:
    """Source index for every padded position along one axis."""
    index = np.arange(-pad, size + pad)
    if mode == "edge":
        return np.clip(index, 0, size - 1)
    if mode == "reflect":
        period = 2 * (size - 1)
        index = np.abs(index) % period
        return np.where(index >= size, period - index, index)
    msg = f"unknown padding mode: {mode}"
    raise ValueError(msg)


def pad_image(img: Image, pad_h: int, pad_w: int, mode: str = "reflect") -> Image:
    """Pad with zeros, replicated edge pixels, or a mirror (without repeating the edge)."""
    h, w = img.shape
    if mode == "zero":
        out = np.zeros((h + 2 * pad_h, w + 2 * pad_w))
        out[pad_h : pad_h + h, pad_w : pad_w + w] = img
        return out
    rows = _border_index(h, pad_h, mode)
    cols = _border_index(w, pad_w, mode)
    return img[np.ix_(rows, cols)]


def convolve2d(img: Image, kernel: Image, mode: str = "reflect") -> Image:
    """Same-size 2D convolution: sum of shifted copies of the image weighted by the flipped kernel."""
    kh, kw = kernel.shape
    if kh % 2 == 0 or kw % 2 == 0:
        msg = "kernel sides must be odd"
        raise ValueError(msg)
    h, w = img.shape
    padded = pad_image(img, kh // 2, kw // 2, mode)
    flipped = kernel[::-1, ::-1]
    out = np.zeros_like(img)
    for i, j in itertools.product(range(kh), range(kw)):
        out += flipped[i, j] * padded[i : i + h, j : j + w]
    return out


def to_display(img: Image, name: str) -> NDArray[np.uint8]:
    """Clip to [0, 255]; zero-sum kernels are centred on mid-gray and scaled symmetrically."""
    if name in SIGNED_KERNELS:
        peak = max(float(np.abs(img).max()), 1.0)
        img = 128.0 + img * (128.0 / peak)
    return np.rint(np.clip(img, 0.0, MAX_PIXEL)).astype(np.uint8)


def mse(a: Image, b: Image) -> float:
    return float(np.mean((a - b) ** 2))


def psnr(a: Image, b: Image) -> float:
    error = mse(a, b)
    return float("inf") if error == 0 else float(10 * np.log10(MAX_PIXEL**2 / error))


def sharpness(img: Image) -> float:
    """Mean gradient magnitude from forward differences."""
    gx = np.diff(img, axis=1)[:-1, :]
    gy = np.diff(img, axis=0)[:, :-1]
    return float(np.mean(np.hypot(gx, gy)))


class Result:
    def __init__(self, output: Image, reference: Image) -> None:
        self.output = output
        self.psnr = psnr(reference, output)
        self.sharpness = sharpness(output)


def run_kernels(img: Image) -> dict[str, Result]:
    return {name: Result(convolve2d(img, kernel), img) for name, kernel in KERNELS.items()}


def save_figure(fig: plt.Figure, path: Path) -> None:
    pil_kwargs = {"quality": JPEG_QUALITY} if path.suffix == ".jpg" else None
    fig.savefig(path, dpi=FIGURE_DPI, facecolor=SURFACE, pil_kwargs=pil_kwargs)
    plt.close(fig)
    logger.info("saved %s", path.name)


def show_panel(ax: Axes, img: NDArray[np.uint8], title: str) -> None:
    ax.imshow(img, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    ax.set_title(title, fontsize=8, color=INK)
    ax.axis("off")


def plot_grid(name: str, original: Image, results: dict[str, Result]) -> None:
    """Original plus every kernel result for one input image."""
    panels = [("original", original, "")]
    panels += [(k, r.output, f"\nPSNR {r.psnr:.1f} dB") for k, r in results.items()]
    rows = -(-len(panels) // GRID_COLUMNS)
    fig, axes = plt.subplots(rows, GRID_COLUMNS, figsize=(12, 3.0 * rows))
    fig.suptitle(f"{name}: 2D convolution with different kernels", color=INK)
    for ax, (label, img, note) in zip(axes.flat, panels, strict=False):
        show_panel(ax, to_display(img, label), label + note)
    fig.tight_layout(h_pad=2.0)
    save_figure(fig, OUTPUT_DIR / f"{name}_grid.jpg")


def draw_bars(ax: Axes, all_results: dict[str, dict[str, Result]], kernels: list[str], attr: str) -> None:
    x = np.arange(len(kernels))
    for idx, (image, color) in enumerate(zip(IMAGES, IMAGE_COLORS, strict=True)):
        values = [getattr(all_results[image][k], attr) for k in kernels]
        ax.bar(x + (idx - 1.5) * BAR_WIDTH, values, BAR_WIDTH, color=color, edgecolor=SURFACE, label=image)
    ax.set_xticks(x, kernels)
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color="#e6e5e1", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def plot_metrics(all_results: dict[str, dict[str, Result]]) -> None:
    """PSNR (identity excluded, it is infinite) and sharpness per kernel and image."""
    kernels = [k for k in KERNELS if k != "identity"]
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(11, 7.5))
    draw_bars(top, all_results, kernels, "psnr")
    top.set_ylabel("PSNR vs original (dB), higher = closer", color=MUTED_INK)
    top.legend(frameon=False, ncols=len(IMAGES))
    draw_bars(bottom, all_results, list(KERNELS), "sharpness")
    bottom.set_ylabel("Mean gradient magnitude", color=MUTED_INK)
    fig.suptitle("Effect of each kernel on fidelity and sharpness", color=INK)
    fig.tight_layout()
    save_figure(fig, OUTPUT_DIR / "metrics.png")


def plot_padding_comparison(img: Image) -> None:
    """7x7 box blur with each padding mode; second row zooms into the top-left corner."""
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.8))
    fig.suptitle("Border handling: box_7 with different padding", color=INK)
    for col, mode in enumerate(("zero", "edge", "reflect")):
        blurred = to_display(convolve2d(img, KERNELS["box_7"], mode), "box_7")
        show_panel(axes[0, col], blurred, f"{mode} padding")
        show_panel(axes[1, col], blurred[:CORNER_SIZE, :CORNER_SIZE], f"{mode}: top-left corner")
    fig.tight_layout()
    save_figure(fig, OUTPUT_DIR / "padding_comparison.jpg")


def write_metrics_md(all_results: dict[str, dict[str, Result]]) -> None:
    lines = ["# Metrics (generated by lab_1.py)", ""]
    for attr, title in (("psnr", "PSNR vs original (dB)"), ("sharpness", "Mean gradient magnitude")):
        lines += [f"## {title}", "", "| kernel | " + " | ".join(IMAGES) + " |", "|---|" + "---|" * len(IMAGES)]
        for kernel in KERNELS:
            cells = " | ".join(f"{getattr(all_results[i][kernel], attr):.2f}" for i in IMAGES)
            lines.append(f"| {kernel} | {cells} |")
        lines.append("")
    (OUTPUT_DIR / "metrics.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUTPUT_DIR.mkdir(exist_ok=True)
    all_results: dict[str, dict[str, Result]] = {}
    for name in IMAGES:
        original = load_gray(INPUT_DIR / f"{name}.jpg")
        all_results[name] = run_kernels(original)
        plot_grid(name, original, all_results[name])
    plot_metrics(all_results)
    plot_padding_comparison(load_gray(INPUT_DIR / "detail_high.jpg"))
    write_metrics_md(all_results)


if __name__ == "__main__":
    main()
