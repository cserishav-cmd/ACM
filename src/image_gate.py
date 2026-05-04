"""Image gate for routing uploads before model inference."""

import colorsys
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ImageGateResult:
    """Routing decision derived from image-level visual evidence."""

    route: str
    label: str
    confidence: float
    reason: str
    metrics: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "route": self.route,
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "reason": self.reason,
            "metrics": {key: round(value, 4) for key, value in self.metrics.items()},
        }


class ImageGateService:
    """Classifies uploads into reject, health-only, or full rice analysis routes.

    This is intentionally a conservative image gate. It rejects obvious invalid
    uploads before model inference and identifies field-like paddy scenes, but
    it does not try to prove rice variety by color heuristics alone.
    """

    NON_RICE = "non_rice"
    HEALTH_ONLY = "health_only"
    PADDY_ANALYSIS = "paddy_analysis"
    GRAIN_ANALYSIS = "grain_analysis"

    def analyze(self, image: np.ndarray) -> ImageGateResult:
        metrics = _compute_visual_metrics(image)

        invalid_score = _bounded(
            (0.05 - metrics["foreground_ratio"]) * 8.0
            + (0.03 - metrics["texture_density"]) * 8.0
            + (0.04 - metrics["saturation_ratio"]) * 5.0
        )

        plant_score = _bounded(
            metrics["vegetation_ratio"] * 1.65
            + metrics["yellow_brown_ratio"] * 0.55
            + metrics["saturation_ratio"] * 0.4
            + metrics["green_dominance"] * 0.8
            + metrics["texture_density"] * 0.7
        )

        crop_score = _bounded(
            metrics["vegetation_ratio"] * 1.05
            + metrics["elongated_green_texture"] * 1.15
            + metrics["yellow_brown_ratio"] * 0.65
            + metrics["field_pattern_score"] * 0.75
        )

        field_like_score = _bounded(
            metrics["vegetation_ratio"] * 0.95
            + metrics["field_pattern_score"] * 1.2
            + metrics["texture_density"] * 0.7
            - metrics["yellow_brown_ratio"] * 0.25
        )

        grain_score = _bounded(
            metrics["white_ratio"] * 1.5
            + metrics["yellow_brown_ratio"] * 0.5
            + metrics["texture_density"] * 1.5
            - metrics["vegetation_ratio"] * 3.0
        )

        if invalid_score >= 0.75 or (
            plant_score < 0.10
            and grain_score < 0.30
            and metrics["foreground_ratio"] < 0.05
            and metrics["texture_density"] < 0.02
        ):
            return ImageGateResult(
                route=self.NON_RICE,
                label="Invalid or non-plant image",
                confidence=max(invalid_score, 1.0 - max(plant_score, grain_score)),
                reason="The upload does not contain enough rice-like vegetation or crop texture for rice analysis.",
                metrics=metrics,
            )

        if grain_score >= 0.45 and metrics["vegetation_ratio"] < 0.15:
            return ImageGateResult(
                route=self.GRAIN_ANALYSIS,
                label="Rice grain sample",
                confidence=grain_score,
                reason="The image appears to be a sample of harvested rice grains, so only variety detection is appropriate.",
                metrics=metrics,
            )

        if field_like_score >= 0.72 and metrics["vegetation_ratio"] >= 0.35:
            return ImageGateResult(
                route=self.HEALTH_ONLY,
                label="Paddy or grass-type image",
                confidence=field_like_score,
                reason=(
                    "The image appears to be a paddy/grass-type crop scene, "
                    "so only health assessment is appropriate."
                ),
                metrics=metrics,
            )

        return ImageGateResult(
            route=self.PADDY_ANALYSIS,
            label="Crop image candidate",
            confidence=max(crop_score, plant_score),
            reason="The upload has enough plant/crop content for model-based routing.",
            metrics=metrics,
        )


def _compute_visual_metrics(image: np.ndarray) -> dict[str, float]:
    image = _sample_for_gate(image)
    pixels = np.clip(image.reshape(-1, 3), 0.0, 1.0)
    red = pixels[:, 0]
    green = pixels[:, 1]
    blue = pixels[:, 2]

    hsv = np.array([colorsys.rgb_to_hsv(float(r), float(g), float(b)) for r, g, b in pixels])
    hue = hsv[:, 0]
    saturation = hsv[:, 1]
    value = hsv[:, 2]

    green_mask = (
        (hue >= 0.17)
        & (hue <= 0.46)
        & (saturation >= 0.18)
        & (value >= 0.18)
        & (green > red * 0.9)
        & (green > blue * 0.9)
    )
    saturation_mask = (saturation >= 0.12) & (value >= 0.12)
    yellow_brown_mask = (
        (hue >= 0.06)
        & (hue <= 0.18)
        & (saturation >= 0.18)
        & (value >= 0.16)
    )
    white_mask = (saturation < 0.25) & (value > 0.35)

    gray = (
        image[:, :, 0] * 0.299
        + image[:, :, 1] * 0.587
        + image[:, :, 2] * 0.114
    )
    grad_y = np.abs(np.diff(gray, axis=0))
    grad_x = np.abs(np.diff(gray, axis=1))
    texture_density = float((np.mean(grad_x > 0.08) + np.mean(grad_y > 0.08)) / 2.0)
    vertical_bias = float(np.mean(grad_x) / (np.mean(grad_y) + 1e-6))

    vegetation_ratio = float(np.mean(green_mask))
    yellow_brown_ratio = float(np.mean(yellow_brown_mask))
    saturation_ratio = float(np.mean(saturation_mask))
    white_ratio = float(np.mean(white_mask))
    foreground_ratio = float(np.mean(saturation_mask | green_mask | yellow_brown_mask | white_mask))
    green_dominance = float(np.mean(np.maximum(green - np.maximum(red, blue), 0.0)))
    elongated_green_texture = _bounded(vegetation_ratio * min(vertical_bias, 2.0))
    field_pattern_score = _bounded(vegetation_ratio * 0.7 + texture_density * 1.1)

    return {
        "vegetation_ratio": vegetation_ratio,
        "yellow_brown_ratio": yellow_brown_ratio,
        "saturation_ratio": saturation_ratio,
        "white_ratio": white_ratio,
        "foreground_ratio": foreground_ratio,
        "green_dominance": green_dominance,
        "texture_density": texture_density,
        "vertical_texture_bias": vertical_bias,
        "elongated_green_texture": elongated_green_texture,
        "field_pattern_score": field_pattern_score,
    }


def _bounded(value: float) -> float:
    return float(max(0.0, min(1.0, value)))


def _sample_for_gate(image: np.ndarray, max_side: int = 256) -> np.ndarray:
    """Downsample by stride for fast upload routing on large phone photos."""
    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side <= max_side:
        return image

    stride = int(np.ceil(longest_side / max_side))
    return image[::stride, ::stride, :]
