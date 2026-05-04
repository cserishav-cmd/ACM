"""Segmentation service — loads and runs the segmentation model."""

import numpy as np
from utils.config import config
from utils.image import resize_for_segmentation, colorize_mask, mask_to_base64


# Segmentation classes from the RiceSEG dataset (6-class)
SEG_CLASSES = [
    "background",
    "vegetation",
    "dry_leaves",
    "panicles",
    "weeds",
    "others",
]

# Human-readable display names
SEG_DISPLAY_NAMES = {
    "background": "Background (Soil/Water)",
    "vegetation": "Vegetation (Rice Plants)",
    "dry_leaves": "Dry Leaves",
    "panicles": "Panicles (Grain Heads)",
    "weeds": "Weeds",
    "others": "Others",
}

# Color palette for each class (RGB)
SEG_COLORS = {
    "background": (40, 40, 40),       # dark gray
    "vegetation": (52, 211, 153),      # emerald green
    "dry_leaves": (251, 191, 36),      # amber
    "panicles": (251, 146, 60),        # orange
    "weeds": (248, 113, 113),          # red
    "others": (148, 163, 184),         # slate
}

# Color array for fast vectorized indexing (shape: 6×3)
SEG_COLOR_ARRAY = np.array([SEG_COLORS[c] for c in SEG_CLASSES], dtype=np.uint8)


class SegmentationService:
    """Handles rice field segmentation inference."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model = None
        self._num_classes = len(SEG_CLASSES)
        self._initialized = True

    def load_model(self) -> None:
        """Load the segmentation model from disk."""
        import tensorflow as tf
        print(f"[*] Loading segmentation model from {config.SEG_MODEL_PATH}...")
        self.model = tf.keras.models.load_model(config.SEG_MODEL_PATH, compile=False)
        print(f"    [OK] Segmentation model loaded. Input shape: {self.model.input_shape}")
        print(f"    [OK] Segmentation output shape: {self.model.output_shape}")

    def predict(self, image: np.ndarray) -> dict:
        """Run segmentation on a single image.

        Args:
            image: Preprocessed image array (H, W, 3) in [0, 1].

        Returns:
            Dict with color-coded mask, per-class coverage percentages, and shape info.
        """
        if self.model is None:
            self.load_model()

        input_tensor = resize_for_segmentation(image, self.model)
        prediction = self.model.predict(input_tensor, verbose=0)

        # Squeeze batch dim → (H, W, C) or (H, W) or (H, W, 1)
        mask = prediction[0]

        # Determine if multi-class or binary output
        if mask.ndim == 3 and mask.shape[-1] > 1:
            # Multi-class: argmax along channel axis → (H, W) class indices
            class_mask = np.argmax(mask, axis=-1).astype(np.int32)
            num_output_classes = mask.shape[-1]
        elif mask.ndim == 3 and mask.shape[-1] == 1:
            # Binary segmentation: threshold → 0 = background, 1 = vegetation
            class_mask = (mask.squeeze(-1) > 0.5).astype(np.int32)
            num_output_classes = 2
        else:
            # 2D mask: threshold
            class_mask = (mask > 0.5).astype(np.int32)
            num_output_classes = 2

        # Compute per-class coverage percentages
        total_pixels = class_mask.size
        class_coverage = {}
        for idx in range(min(num_output_classes, self._num_classes)):
            class_name = SEG_CLASSES[idx]
            pixel_count = int(np.sum(class_mask == idx))
            class_coverage[SEG_DISPLAY_NAMES[class_name]] = round(
                (pixel_count / total_pixels) * 100, 2
            )

        # If fewer output classes than SEG_CLASSES, fill remaining with 0
        for idx in range(num_output_classes, self._num_classes):
            class_name = SEG_CLASSES[idx]
            class_coverage[SEG_DISPLAY_NAMES[class_name]] = 0.0

        # Vegetation percentage (for decision engine)
        veg_key = SEG_DISPLAY_NAMES["vegetation"]
        vegetation_percent = class_coverage.get(veg_key, 0.0)

        # Generate color-coded mask image
        color_mask = colorize_mask(class_mask, SEG_COLOR_ARRAY)

        return {
            "mask_base64": mask_to_base64(color_mask, mode="RGB"),
            "mask_shape": list(class_mask.shape),
            "vegetation_percent": vegetation_percent,
            "class_coverage": class_coverage,
            "class_colors": {
                SEG_DISPLAY_NAMES[c]: list(SEG_COLORS[c]) for c in SEG_CLASSES
            },
        }
