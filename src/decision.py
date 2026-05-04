"""Decision engine — combines all model outputs into unified agricultural intelligence."""


# Severity → risk level mapping
SEVERITY_RISK = {
    "none": "low",
    "moderate": "medium",
    "high": "high",
    "critical": "critical",
}


class DecisionService:
    """Combines segmentation, disease, and variety results into actionable intelligence."""

    @staticmethod
    def health_report(disease_result: dict) -> dict:
        """Generate a health-only report without rice field or variety outputs."""
        disease_name = disease_result.get("predicted_class", "Unknown")
        disease_conf = disease_result.get("confidence", 0.0)
        is_healthy = disease_result.get("is_healthy", False)
        severity = disease_result.get("severity", "none")
        risk_level = SEVERITY_RISK.get(severity, "low")
        recommendation = disease_result.get("recommendation", "")

        if is_healthy:
            summary = (
                f"No disease detected (confidence: {disease_conf * 100:.1f}%). "
                "The crop appears healthy. Continue regular monitoring."
            )
            recommendations = [
                "Continue routine field observation and balanced irrigation.",
                "Recheck leaves if discoloration, spots, or wilting appear.",
            ]
        else:
            summary = (
                f"{disease_name} detected with {disease_conf * 100:.1f}% confidence. "
                f"Severity: {severity.capitalize()}. {recommendation}"
            )
            recommendations = [recommendation]

        return {
            "health_score": _compute_disease_only_score(is_healthy, severity, disease_conf),
            "disease_assessment": {
                "disease": disease_name,
                "is_healthy": is_healthy,
                "severity": severity,
                "risk_level": risk_level,
                "confidence": round(disease_conf, 4),
                "summary": summary,
            },
            "recommendations": recommendations,
        }

    @staticmethod
    def variety_report(variety_result: dict) -> dict:
        """Generate a variety-only report without paddy health outputs."""
        variety_name = variety_result.get("predicted_class", "Unknown")
        variety_conf = variety_result.get("confidence", 0.0)
        variety_desc = variety_result.get("description", "")
        
        variety_summary = (
            f"Identified as {variety_name} (confidence: {variety_conf * 100:.1f}%). "
            f"{variety_desc}"
        )
        
        return {
            "health_score": 100,
            "field_health": None,
            "disease_assessment": None,
            "variety_info": {
                "variety": variety_name,
                "confidence": round(variety_conf, 4),
                "description": variety_desc,
                "summary": variety_summary,
            },
            "recommendations": [
                f"Rice sample successfully identified as {variety_name}.",
                "Store grains in a cool, dry place to prevent moisture and pest damage."
            ],
        }

    @staticmethod
    def analyze(
        segmentation_result: dict = None,
        disease_result: dict = None,
        variety_result: dict = None,
    ) -> dict:
        """Generate unified analysis from all three model outputs.

        Args:
            segmentation_result: Output from SegmentationService.predict()
            disease_result: Output from DiseaseService.predict()
            variety_result: Output from VarietyService.predict()

        Returns:
            Structured decision with field health, risk assessment, and recommendations.
        """
        # ── Field Health Assessment (from segmentation) ──
        if segmentation_result and "vegetation_percent" in segmentation_result:
            veg_pct = segmentation_result.get("vegetation_percent", 0.0)

            if veg_pct >= 70:
                field_status = "Healthy Growth"
                field_color = "green"
                field_summary = (
                    f"Excellent crop density detected — {veg_pct:.1f}% vegetation coverage. "
                    "The field shows strong, uniform growth with optimal canopy development."
                )
            elif veg_pct >= 40:
                field_status = "Moderate Growth"
                field_color = "amber"
                field_summary = (
                    f"Moderate crop density — {veg_pct:.1f}% vegetation coverage. "
                    "Some areas show sparse growth. Consider supplemental fertilization "
                    "and ensure adequate irrigation."
                )
            else:
                field_status = "Poor Growth"
                field_color = "red"
                field_summary = (
                    f"Low crop density — only {veg_pct:.1f}% vegetation coverage. "
                    "Significant bare patches detected. Immediate intervention required: "
                    "check for drainage issues, nutrient deficiency, or pest damage."
                )
        else:
            veg_pct = None
            field_status = "N/A"
            field_color = "slate"
            field_summary = "Image is not a wide field scene; skipping vegetation area analysis."

        # ── Disease Risk Assessment ──
        if disease_result:
            disease_name = disease_result.get("predicted_class", "Unknown")
            disease_conf = disease_result.get("confidence", 0.0)
            is_healthy = disease_result.get("is_healthy", False)
            severity = disease_result.get("severity", "none")
            risk_level = SEVERITY_RISK.get(severity, "low")
            recommendation = disease_result.get("recommendation", "")

            if is_healthy:
                disease_summary = (
                    f"No disease detected (confidence: {disease_conf * 100:.1f}%). "
                    "Plants appear healthy. Continue regular monitoring."
                )
            else:
                disease_summary = (
                    f"{disease_name} detected with {disease_conf * 100:.1f}% confidence. "
                    f"Severity: {severity.capitalize()}. {recommendation}"
                )
            
            disease_assessment = {
                "disease": disease_name,
                "is_healthy": is_healthy,
                "severity": severity,
                "risk_level": risk_level,
                "confidence": round(disease_conf, 4),
                "summary": disease_summary,
            }
        else:
            is_healthy = True
            severity = "none"
            disease_conf = 0.0
            disease_assessment = None

        # ── Variety Information ──
        if variety_result:
            variety_name = variety_result.get("predicted_class", "Unknown")
            variety_conf = variety_result.get("confidence", 0.0)
            variety_desc = variety_result.get("description", "")

            variety_summary = (
                f"Identified as {variety_name} (confidence: {variety_conf * 100:.1f}%). "
                f"{variety_desc}"
            )
            
            variety_info = {
                "variety": variety_name,
                "confidence": round(variety_conf, 4),
                "description": variety_desc,
                "summary": variety_summary,
            }
        else:
            variety_info = None

        # ── Overall Recommendation ──
        recommendations = []

        # Field condition recommendations
        if veg_pct is not None:
            if veg_pct < 40:
                recommendations.append(
                    "🔴 URGENT: Very low vegetation coverage. Inspect field for flooding, "
                    "pest infestation, or severe nutrient deficiency."
                )
            elif veg_pct < 70:
                recommendations.append(
                    "🟡 Monitor growth closely. Consider targeted fertilization in sparse areas."
                )

        # Disease recommendations
        if disease_result and not is_healthy:
            emoji = "🔴" if severity in ("critical", "high") else "🟡"
            recommendations.append(f"{emoji} {recommendation}")

        # If everything is fine
        if not recommendations:
            recommendations.append(
                "🟢 Field is in excellent condition. Maintain current management practices."
            )

        # ── Composite score (0-100) ──
        if veg_pct is not None:
            health_score = _compute_health_score(veg_pct, is_healthy, severity, disease_conf)
        else:
            health_score = _compute_disease_only_score(is_healthy, severity, disease_conf)

        field_health_dict = {
            "status": field_status,
            "color": field_color,
            "summary": field_summary,
        }
        if veg_pct is not None:
            field_health_dict["vegetation_percent"] = round(veg_pct, 1)

        return {
            "health_score": health_score,
            "field_health": field_health_dict,
            "disease_assessment": disease_assessment,
            "variety_info": variety_info,
            "recommendations": recommendations,
        }


def _compute_health_score(
    veg_pct: float, is_healthy: bool, severity: str, disease_conf: float
) -> int:
    """Compute a 0-100 composite health score.

    Weighted: vegetation (50%), disease (50%).
    """
    # Vegetation component (0-50)
    veg_score = min(veg_pct / 100 * 50, 50)

    # Disease component (0-50)
    if is_healthy:
        disease_score = 50.0
    else:
        penalty_map = {"moderate": 15, "high": 30, "critical": 45, "none": 0}
        penalty = penalty_map.get(severity, 10) * disease_conf
        disease_score = max(50 - penalty, 5)

    return int(round(veg_score + disease_score))


def _compute_disease_only_score(is_healthy: bool, severity: str, disease_conf: float) -> int:
    """Compute a health score when only disease inference is allowed."""
    if is_healthy:
        return 95

    penalty_map = {"moderate": 35, "high": 55, "critical": 75, "none": 10}
    penalty = penalty_map.get(severity, 30) * disease_conf
    return int(round(max(100 - penalty, 10)))
