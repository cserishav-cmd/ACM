"""Variety classification service — loads and runs the variety model."""

import numpy as np
import tensorflow as tf
from utils.config import config
from utils.image import resize_for_classification


# Variety classes — sorted by directory name (alphabetical), matching training order
VARIETY_CLASSES = [
    "10_Lal_Aush",
    "11_Jirashail",
    "12_Gutisharna",
    "13_Red_Cargo",
    "14_Najirshail",
    "15_Katari_Polao",
    "16_Lal_Biroi",
    "17_Chinigura_Polao",
    "18_Amon",
    "19_Shorna5",
    "1_Subol_Lota",
    "20_Lal_Binni",
    "2_Bashmoti",
    "3_Ganjiya",
    "4_Shampakatari",
    "5_Katarivog",
    "6_BR28",
    "7_BR29",
    "8_Paijam",
    "9_Bashful",
]

# Human-readable display names (strip numeric prefix)
VARIETY_DISPLAY_NAMES = {v: v.split("_", 1)[1].replace("_", " ") for v in VARIETY_CLASSES}

# Variety descriptions for the decision engine
VARIETY_DESCRIPTIONS = {
    "10_Lal_Aush": "Traditional red Aush rice, cultivated during the early monsoon season. Known for its reddish grain color.",
    "11_Jirashail": "Premium aromatic variety popular in Bangladesh. Prized for its fine grain and fragrance.",
    "12_Gutisharna": "Local heritage variety with good cooking quality. Commonly grown in wetland regions.",
    "13_Red_Cargo": "Whole-grain red rice rich in antioxidants and fiber. Retains the bran layer for nutrition.",
    "14_Najirshail": "Popular slender-grain aromatic rice from Bangladesh. Widely used for special dishes.",
    "15_Katari_Polao": "Fine aromatic variety ideal for polao and biriyani. Known for its elongated grains.",
    "16_Lal_Biroi": "Traditional red-husked variety cultivated in flood-prone areas. Resilient to waterlogging.",
    "17_Chinigura_Polao": "Miniature aromatic grain, often called 'the prince of rice'. Used for festive dishes.",
    "18_Amon": "Major monsoon-season (Aman) variety. Forms the backbone of annual rice production.",
    "19_Shorna5": "High-yielding modern variety with golden grain. Developed for improved productivity.",
    "1_Subol_Lota": "Heritage variety with medium grain size. Known for its adaptability to local conditions.",
    "20_Lal_Binni": "Sticky red glutinous rice used in traditional desserts and festive preparations.",
    "2_Bashmoti": "Aromatic long-grain Basmati variety. Expands significantly during cooking.",
    "3_Ganjiya": "Local variety suited to lowland cultivation. Tolerant to moderate flooding.",
    "4_Shampakatari": "Traditional variety with short maturation period. Ideal for multiple cropping cycles.",
    "5_Katarivog": "Popular coarse-grain variety grown widely in northern regions. Robust and high-yielding.",
    "6_BR28": "Modern high-yield variety developed by BRRI. Short-duration Boro season rice.",
    "7_BR29": "High-yielding Boro variety from BRRI. Widely adopted for winter-season cultivation.",
    "8_Paijam": "Traditional fine-grain variety. Appreciated for its cooking quality and taste.",
    "9_Bashful": "Local aromatic variety with distinctive flavor profile. Grown in select regions.",
}


class VarietyService:
    """Handles rice variety classification inference."""

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
        self._initialized = True

    def load_model(self) -> None:
        """Load the variety classification model from disk."""
        print(f"[*] Loading variety model from {config.VARIETY_MODEL_PATH}...")
        self.model = tf.keras.models.load_model(config.VARIETY_MODEL_PATH, compile=False)
        print(f"    [OK] Variety model loaded. Input shape: {self.model.input_shape}")

    def predict(self, image: np.ndarray) -> dict:
        """Classify rice variety from a single image.

        Args:
            image: Preprocessed image array (H, W, 3) in [0, 1].

        Returns:
            Dict with predicted class, confidence, description, and all predictions.
        """
        if self.model is None:
            self.load_model()

        input_tensor = resize_for_classification(image, self.model)
        predictions = self.model.predict(input_tensor, verbose=0)[0]

        predicted_idx = int(np.argmax(predictions))
        confidence = float(predictions[predicted_idx])
        predicted_key = VARIETY_CLASSES[predicted_idx]
        sorted_predictions = np.sort(predictions)[::-1]
        second_confidence = float(sorted_predictions[1]) if len(sorted_predictions) > 1 else 0.0
        confidence_margin = confidence - second_confidence

        all_predictions = {
            VARIETY_DISPLAY_NAMES[cls]: round(float(prob), 4)
            for cls, prob in zip(VARIETY_CLASSES, predictions)
        }

        return {
            "predicted_class": VARIETY_DISPLAY_NAMES[predicted_key],
            "predicted_key": predicted_key,
            "confidence": round(confidence, 4),
            "confidence_margin": round(float(confidence_margin), 4),
            "description": VARIETY_DESCRIPTIONS.get(predicted_key, ""),
            "all_predictions": all_predictions,
        }
