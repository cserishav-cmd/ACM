"""Image preprocessing utilities."""

import io
import base64
import numpy as np
from PIL import Image
from utils.config import config


def validate_image(filename: str, image_bytes: bytes) -> None:
    """Validate uploaded image file.

    Args:
        filename: Original filename of the uploaded image.
        image_bytes: Raw bytes of the uploaded image.

    Raises:
        ValueError: If the file is too large or has an unsupported extension.
    """
    if len(image_bytes) > config.MAX_IMAGE_SIZE:
        raise ValueError(
            f"Image too large. Maximum size is {config.MAX_IMAGE_SIZE // (1024 * 1024)}MB."
        )

    if filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in config.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '.{ext}'. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )


def preprocess_upload(image_bytes: bytes) -> np.ndarray:
    """Convert uploaded bytes to a normalized numpy array with memory-safe resizing.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Numpy array of shape (H, W, 3) with values in [0, 1].
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Memory safety: If image is very large, downscale it immediately before normalization
    # Normalizing a 4K image to float32 consumes ~100MB RAM.
    max_dim = 1024
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
    return np.array(image, dtype=np.float32) / 255.0


def _input_size_from_model(model, fallback_shape: tuple[int, int]) -> tuple[int, int]:
    """Return the expected image size for a loaded Keras model."""
    input_shape = getattr(model, "input_shape", None)
    if isinstance(input_shape, list):
        input_shape = input_shape[0]

    if input_shape and len(input_shape) >= 4:
        height, width = input_shape[1], input_shape[2]
        if height is not None and width is not None:
            return int(height), int(width)

    return fallback_shape


def resize_for_model(
    image: np.ndarray,
    model,
    fallback_shape: tuple[int, int],
) -> np.ndarray:
    """Resize an uploaded image to the input size expected by a model.

    Args:
        image: Input image array (H, W, 3).
        model: Loaded Keras model with an input_shape attribute.
        fallback_shape: Shape to use if the model has dynamic dimensions.

    Returns:
        Resized image array with batch dimension.
    """
    h, w = _input_size_from_model(model, fallback_shape)
    pil_image = Image.fromarray((image * 255).astype(np.uint8))
    pil_image = pil_image.resize((w, h), Image.BILINEAR)
    resized = np.array(pil_image, dtype=np.float32) / 255.0
    return np.expand_dims(resized, axis=0)


def resize_for_segmentation(image: np.ndarray, model=None) -> np.ndarray:
    """Resize image for the segmentation model."""
    return resize_for_model(image, model, config.SEG_INPUT_SHAPE)


def resize_for_classification(image: np.ndarray, model=None) -> np.ndarray:
    """Resize image for classification models (disease / variety).

    Args:
        image: Input image array (H, W, 3).

    Returns:
        Resized image array with batch dimension (1, 224, 224, 3).
    """
    return resize_for_model(image, model, config.CLASSIFY_INPUT_SHAPE)


def colorize_mask(class_mask: np.ndarray, color_array: np.ndarray) -> np.ndarray:
    """Convert an integer class mask to an RGB color image.

    Args:
        class_mask: 2D array of shape (H, W) with integer class indices.
        color_array: Array of shape (N, 3) mapping class index → RGB color.

    Returns:
        RGB image array of shape (H, W, 3) with uint8 values.
    """
    # Clip indices to valid range
    safe_mask = np.clip(class_mask, 0, len(color_array) - 1)
    return color_array[safe_mask]


def mask_to_base64(mask: np.ndarray, mode: str = "L") -> str:
    """Convert a mask array to a base64 PNG string.

    Args:
        mask: Numpy array — (H, W) grayscale or (H, W, 3) RGB.
        mode: PIL image mode. "L" for grayscale, "RGB" for color.

    Returns:
        Base64-encoded PNG string.
    """
    if mode == "L":
        if mask.ndim == 3:
            mask = mask.squeeze(-1)
        mask_uint8 = (mask * 255).astype(np.uint8)
        pil_mask = Image.fromarray(mask_uint8, mode="L")
    else:
        # RGB mode — already uint8 from colorize_mask
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)
        pil_mask = Image.fromarray(mask, mode="RGB")

    buffer = io.BytesIO()
    pil_mask.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
