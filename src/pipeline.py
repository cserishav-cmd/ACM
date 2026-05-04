"""Pipeline service — orchestrates all models for end-to-end inference."""

import numpy as np
from src.segmentation import SegmentationService
from src.disease import DiseaseService
from src.variety import VarietyService
from src.decision import DecisionService
from src.image_gate import ImageGateService


class PipelineService:
    """Combines segmentation, disease, and variety models into a single pipeline."""

    _instance = None

    def __new__(cls):
        """Singleton pattern — ensures models are loaded only once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.segmentation = SegmentationService()
        self.disease = DiseaseService()
        self.variety = VarietyService()
        self.decision = DecisionService()
        self.image_gate = ImageGateService()
        self.models_loaded = False
        self._initialized = True

    def load_models(self) -> None:
        """Load all three models into memory."""
        self.segmentation.load_model()
        self.disease.load_model()
        self.variety.load_model()
        self.models_loaded = True

    def run_full_pipeline(self, image: np.ndarray) -> dict:
        """Run conditionally routed inference for one uploaded image.

        Routing rules:
        - non-rice images are rejected before any Keras model is called.
        - paddy/grass-type images call only the disease model for health reporting.
        - valid rice images call disease, variety, and segmentation for rice-only analysis.
        """
        gate_result = self.image_gate.analyze(image)
        gate_payload = gate_result.to_dict()

        if gate_result.route == ImageGateService.NON_RICE:
            return {
                "route": gate_result.route,
                "input_gate": gate_payload,
                "rejected": True,
                "analysis_scope": "rejected_non_rice",
            }

        elif gate_result.route == ImageGateService.GRAIN_ANALYSIS:
            variety_result = self.variety.predict(image)
            decision_result = self.decision.variety_report(variety_result)
            return {
                "route": gate_result.route,
                "input_gate": gate_payload,
                "analysis_scope": "grain_analysis",
                "segmentation": None,
                "disease": None,
                "variety": variety_result,
                "decision": decision_result,
            }

        elif gate_result.route == ImageGateService.HEALTH_ONLY:
            disease_result = self.disease.predict(image)
            is_field_scene = gate_payload.get("metrics", {}).get("field_pattern_score", 0.0) >= 0.45
            if is_field_scene:
                seg_result = self.segmentation.predict(image)
            else:
                seg_result = {}
                
            decision_result = self.decision.analyze(
                segmentation_result=seg_result,
                disease_result=disease_result,
                variety_result=None,
            )
            return {
                "route": gate_result.route,
                "input_gate": gate_payload,
                "analysis_scope": "health_only",
                "segmentation": seg_result if is_field_scene else None,
                "disease": disease_result,
                "variety": None,
                "decision": decision_result,
            }

        else: # PADDY_ANALYSIS
            disease_result = self.disease.predict(image)
            
            is_field_scene = gate_payload.get("metrics", {}).get("field_pattern_score", 0.0) >= 0.45
            if is_field_scene:
                seg_result = self.segmentation.predict(image)
            else:
                seg_result = {}

            decision_result = self.decision.analyze(
                segmentation_result=seg_result,
                disease_result=disease_result,
                variety_result=None,
            )

            return {
                "route": gate_result.route,
                "input_gate": gate_payload,
                "analysis_scope": "paddy_analysis",
                "segmentation": seg_result if is_field_scene else None,
                "disease": disease_result,
                "variety": None,
                "decision": decision_result,
            }

    def run_explicit_paddy_analysis(self, image: np.ndarray) -> dict:
        """Run disease detection and segmentation for paddy explicitly, bypassing image gate."""
        disease_result = self.disease.predict(image)
        
        # We can still run segmentation optionally if it passes basic gating, or just try it.
        # To be safe, we'll check field_pattern_score from gate but skip strict gating.
        gate_result = self.image_gate.analyze(image)
        gate_payload = gate_result.to_dict()
        
        is_field_scene = gate_payload.get("metrics", {}).get("field_pattern_score", 0.0) >= 0.45
        if is_field_scene:
            seg_result = self.segmentation.predict(image)
        else:
            seg_result = {}

        decision_result = self.decision.analyze(
            segmentation_result=seg_result,
            disease_result=disease_result,
            variety_result=None,
        )

        return {
            "analysis_scope": "paddy_analysis",
            "segmentation": seg_result if is_field_scene else None,
            "disease": disease_result,
            "variety": None,
            "decision": decision_result,
            "input_gate": gate_payload,  # Included for frontend metadata if needed
        }

    def run_explicit_grain_analysis(self, image: np.ndarray) -> dict:
        """Run variety classification for grain explicitly, bypassing image gate."""
        variety_result = self.variety.predict(image)
        decision_result = self.decision.variety_report(variety_result)
        
        gate_result = self.image_gate.analyze(image)
        gate_payload = gate_result.to_dict()

        return {
            "analysis_scope": "grain_analysis",
            "segmentation": None,
            "disease": None,
            "variety": variety_result,
            "decision": decision_result,
            "input_gate": gate_payload,
        }

    def run_segmentation(self, image: np.ndarray) -> dict:
        """Run segmentation only."""
        return self.segmentation.predict(image)

    def run_disease_detection(self, image: np.ndarray) -> dict:
        """Run disease detection only."""
        return self.disease.predict(image)

    def run_variety_classification(self, image: np.ndarray) -> dict:
        """Run variety classification only."""
        return self.variety.predict(image)


def _is_low_confidence_rice_candidate(variety_result: dict) -> bool:
    """Reject weak rice candidates if the variety model is not highly confident."""
    confidence = variety_result.get("confidence", 0.0)
    return confidence < 0.40
