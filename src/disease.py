"""Disease detection service — loads and runs the disease classification model."""

import numpy as np
import tensorflow as tf
from utils.config import config
from utils.image import resize_for_classification


# Disease classes — exact order matching training dataset folder sort
DISEASE_CLASSES = [
    "bacterial_leaf_blight",
    "bacterial_leaf_streak",
    "bacterial_panicle_blight",
    "blast",
    "brown_spot",
    "dead_heart",
    "downy_mildew",
    "hispa",
    "normal",
    "tungro",
]

# Human-readable display names
DISEASE_DISPLAY_NAMES = {
    "bacterial_leaf_blight": "Bacterial Leaf Blight",
    "bacterial_leaf_streak": "Bacterial Leaf Streak",
    "bacterial_panicle_blight": "Bacterial Panicle Blight",
    "blast": "Blast",
    "brown_spot": "Brown Spot",
    "dead_heart": "Dead Heart",
    "downy_mildew": "Downy Mildew",
    "hispa": "Hispa",
    "normal": "Normal (Healthy)",
    "tungro": "Tungro",
}

# Severity levels for the decision engine
DISEASE_SEVERITY = {
    "bacterial_leaf_blight": "high",
    "bacterial_leaf_streak": "moderate",
    "bacterial_panicle_blight": "high",
    "blast": "critical",
    "brown_spot": "moderate",
    "dead_heart": "critical",
    "downy_mildew": "moderate",
    "hispa": "moderate",
    "normal": "none",
    "tungro": "high",
}

# Treatment recommendations
DISEASE_RECOMMENDATIONS = {
    "bacterial_leaf_blight": "Apply copper-based bactericides. Ensure proper field drainage. Avoid excess nitrogen fertilization.",
    "bacterial_leaf_streak": "Remove infected plant debris. Apply streptomycin-based sprays. Maintain proper spacing between plants.",
    "bacterial_panicle_blight": "Use resistant varieties. Apply bactericides at flowering stage. Avoid high nitrogen application.",
    "blast": "Apply tricyclazole or isoprothiolane fungicides immediately. Remove and destroy infected plants. Ensure balanced fertilization.",
    "brown_spot": "Apply mancozeb or carbendazim fungicides. Improve soil fertility with potassium and phosphorus. Ensure proper water management.",
    "dead_heart": "Apply carbofuran granules in the field. Remove and destroy infested tillers. Use light traps for stem borers.",
    "downy_mildew": "Apply metalaxyl-based fungicides. Improve air circulation. Remove infected plant residues.",
    "hispa": "Apply chlorpyrifos or cartap hydrochloride insecticide. Remove leaf tips sheltering larvae. Encourage natural predators.",
    "normal": "Continue regular monitoring and maintenance. Maintain optimal water and nutrient levels.",
    "tungro": "Control green leafhopper vectors with insecticides. Remove infected plants. Use resistant varieties for replanting.",
}


class DiseaseService:
    """Handles rice disease classification inference."""

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
        """Load the disease classification model from disk."""
        print(f"[*] Loading disease model from {config.DISEASE_MODEL_PATH}...")
        self.model = tf.keras.models.load_model(config.DISEASE_MODEL_PATH, compile=False)
        print(f"    [OK] Disease model loaded. Input shape: {self.model.input_shape}")

    def predict(self, image: np.ndarray) -> dict:
        """Classify disease from a single image.

        Args:
            image: Preprocessed image array (H, W, 3) in [0, 1].

        Returns:
            Dict with predicted class, confidence, severity, and all predictions.
        """
        if self.model is None:
            self.load_model()

        input_tensor = resize_for_classification(image, self.model)
        predictions = self.model.predict(input_tensor, verbose=0)[0]

        predicted_idx = int(np.argmax(predictions))
        confidence = float(predictions[predicted_idx])
        predicted_class = DISEASE_CLASSES[predicted_idx]

        all_predictions = {
            DISEASE_DISPLAY_NAMES[cls]: round(float(prob), 4)
            for cls, prob in zip(DISEASE_CLASSES, predictions)
        }

        return {
            "predicted_class": DISEASE_DISPLAY_NAMES[predicted_class],
            "predicted_key": predicted_class,
            "confidence": round(confidence, 4),
            "severity": DISEASE_SEVERITY[predicted_class],
            "recommendation": DISEASE_RECOMMENDATIONS[predicted_class],
            "is_healthy": predicted_class == "normal",
            "all_predictions": all_predictions,
        }
