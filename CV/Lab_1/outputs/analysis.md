# Lab 1, variant 2: 2D linear filtering, comparative analysis

Student number 17 → variant 2. Every filter is `lab_1.py::convolve2d` (hand-written padding and convolution, numpy only).
Numbers come from `metrics.md`. Figures: `<image>_grid.jpg` (all kernels per image), `metrics.png`, `padding_comparison.jpg`.

## Setup
- Images (256x256, grayscale for processing, sources in `../input/SOURCES.md`):
  `detail_high` (street, many small edges), `detail_low` (jellyfish on plain water),
  `contrast_high` (snow vs dark rock and sky), `contrast_low` (white laptop on white desk).
- Kernels: identity, box 3x3 / 7x7, Gaussian 5x5 σ=1 / 9x9 σ=2, horizontal motion blur 1x9, sharpen, Laplacian (8-neighbour), emboss.
- Padding: reflect by default. PSNR is measured against the original, "sharpness" is the mean gradient magnitude of the output.
- Caveat: the four images are not independent. `contrast_low` is also low-detail (its gradient, 4.6, is close to `detail_low`, 4.9),
  and `contrast_high` is also textured. Detail and contrast effects below are therefore only partly separable.

## Smoothing kernels (box, Gaussian, motion)
- Detail decides how much a blur costs. Box 3x3 gives PSNR 24.6 dB on `detail_high` but 34.4 dB on `detail_low`; box 7x7 gives 20.7 vs 30.7 dB.
  Blur removes high frequencies, and the detailed street scene has far more of them to lose.
- Sharpness falls with kernel size: on `detail_high` the gradient goes 21.0 → 9.9 (box 3) → 5.0 (box 7), a loss of about 76 %.
  On `detail_low` it goes 4.9 → 2.3 → 1.3, so the absolute loss is small because there was little to remove.
- Contrast: `contrast_high` loses the most fidelity (22.7 dB for box 3, 19.8 dB for box 7) because the blur smears large intensity steps.
- Box vs Gaussian: at similar blur strength the results are close in numbers (box 7: 20.7 dB / gradient 4.98, Gaussian 9x9 σ=2: 21.6 dB / 5.04
  on `detail_high`). The Gaussian scores slightly higher PSNR because its centre weighting changes each pixel less. Box blur looks blockier in the grids.
  Larger σ or size blurs more (Gaussian 5x5 σ=1: 24.8 dB, 9x9 σ=2: 21.6 dB).
- Motion blur 1x9 is directional: on `detail_high` PSNR (20.7 dB) matches box 7, but the gradient (7.5) stays above box 7 (5.0),
  since horizontal structure survives while vertical edges are smeared (visible in the grid).

## Sharpening and derivative kernels
- Sharpen raises the gradient by 4x (`detail_high` 21.0 → 86.2) and 4.9x on `contrast_high` (30.2 → 147.8). On `contrast_high` many pixels clip to 0/255
  (speckled look in the grid), so PSNR drops to 10.3 dB. On `contrast_low` the effect is mild (4.6 → 16.4): there is little local contrast to amplify.
- Laplacian output is near zero in flat areas, so PSNR against the original is meaningless (0.9–8.7 dB). Its response is a good detail indicator:
  mean magnitude 237 on `contrast_high`, 157 on `detail_high`, 36 on `detail_low`, 30 on `contrast_low`.
  It also amplifies fine texture and noise, so the high-detail outputs look busy.
- Emboss is a diagonal derivative plus a unit offset, giving a relief look along the 45° direction. Strong edges and texture dominate
  (gradient 96–112 on the two textured images, about 22 on the two smooth ones).
- Zero-sum kernels (Laplacian, emboss) are shown centred on mid-gray and scaled symmetrically, otherwise negative responses are clipped away.

## Padding
`padding_comparison.jpg` blurs `detail_high` with box 7x7. Zero padding mixes black into the 3-pixel border, which darkens it. Edge replication and
reflection keep the border brightness. Reflection follows local structure best. Use reflect (or edge) unless the border must be treated as black.

## Conclusions
1. Smoothing hurts detailed images far more than flat ones, and the loss grows with kernel size (and σ).
2. Gaussian smoothing is gentler than box smoothing of equal extent and avoids blocky artifacts. Motion blur only degrades one direction.
3. Sharpen and Laplacian react in proportion to local contrast and detail, so they matter most on `detail_high` / `contrast_high` and little on
   `detail_low` / `contrast_low`. Sharpening a high-contrast image clips.
4. Padding only affects a border of kernel_size//2 pixels, but zero padding visibly darkens it.

## Verification done
`convolve2d` matched a naive four-loop reference for all kernels and the three padding modes on a random array. `pad_image` matched
`numpy.pad`. Identity returned the input, box and Gaussian kernels summed to 1, and a constant image stayed constant after Gaussian smoothing.
`ruff check`, `ruff format --diff` and `mypy` pass on `lab_1.py`.
