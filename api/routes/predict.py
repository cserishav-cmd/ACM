"""Prediction API routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from src.pipeline import PipelineService
from api.schemas.response import PredictionResponse, ErrorResponse
from utils.image import validate_image, preprocess_upload

router = APIRouter()

# Shared pipeline and chatbot instances (loaded in main.py startup)
pipeline = PipelineService()
from src.chatbot import ChatbotService
chatbot = ChatbotService()


@router.post(
    "",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Full pipeline prediction",
    description="Route the upload, reject non-rice images, and run only the models allowed for that route.",
)
async def predict_full(file: UploadFile = File(...)):
    """Run the strictly routed unified pipeline on the uploaded image."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        results = pipeline.run_full_pipeline(image_array)
        if not results.get("rejected"):
            results["ai_insight"] = await chatbot.generate_initial_insight(results)

        if results.get("rejected"):
            return PredictionResponse(
                success=False,
                message=results["input_gate"]["reason"],
                data=results,
            )

        return PredictionResponse(
            success=True,
            message="Prediction completed successfully",
            data=results,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post(
    "/paddy",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Explicit Paddy Health Analysis",
    description="Run the paddy health analysis (disease and segmentation) regardless of strict routing.",
)
async def predict_paddy(file: UploadFile = File(...)):
    """Run the explicit paddy pipeline on the uploaded image."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        results = pipeline.run_explicit_paddy_analysis(image_array)
        results["ai_insight"] = await chatbot.generate_initial_insight(results)


        return PredictionResponse(
            success=True,
            message="Paddy prediction completed successfully",
            data=results,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paddy prediction failed: {str(e)}")


@router.post(
    "/grain",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Explicit Rice Grain Analysis",
    description="Run the grain analysis (variety classification) regardless of strict routing.",
)
async def predict_grain(file: UploadFile = File(...)):
    """Run the explicit grain pipeline on the uploaded image."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        results = pipeline.run_explicit_grain_analysis(image_array)
        results["ai_insight"] = await chatbot.generate_initial_insight(results)


        return PredictionResponse(
            success=True,
            message="Grain prediction completed successfully",
            data=results,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grain prediction failed: {str(e)}")


@router.post("/segment", summary="Segmentation only")
async def predict_segment(file: UploadFile = File(...)):
    """Run only the segmentation model after rice-analysis routing passes."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        gate = pipeline.image_gate.analyze(image_array).to_dict()
        if gate["route"] != "rice_analysis":
            return PredictionResponse(
                success=False,
                message="Segmentation is available only for valid rice analysis images.",
                data={"route": gate["route"], "input_gate": gate},
            )

        result = pipeline.run_segmentation(image_array)

        return PredictionResponse(
            success=True,
            message="Segmentation completed",
            data={"route": gate["route"], "input_gate": gate, "segmentation": result},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.post("/disease", summary="Disease detection only")
async def predict_disease(file: UploadFile = File(...)):
    """Run only the disease detection model for rice or paddy/grass-type images."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        gate = pipeline.image_gate.analyze(image_array).to_dict()
        if gate["route"] == "non_rice":
            return PredictionResponse(
                success=False,
                message=gate["reason"],
                data={"route": gate["route"], "input_gate": gate},
            )

        result = pipeline.run_disease_detection(image_array)

        return PredictionResponse(
            success=True,
            message="Disease detection completed",
            data={"route": gate["route"], "input_gate": gate, "disease": result},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease detection failed: {str(e)}")


@router.post("/variety", summary="Variety classification only")
async def predict_variety(file: UploadFile = File(...)):
    """Run only the variety classification model after rice-analysis routing passes."""
    try:
        image_bytes = await file.read()
        validate_image(file.filename, image_bytes)
        image_array = preprocess_upload(image_bytes)

        gate = pipeline.image_gate.analyze(image_array).to_dict()
        if gate["route"] != "rice_analysis":
            return PredictionResponse(
                success=False,
                message="Variety classification is available only for valid rice analysis images.",
                data={"route": gate["route"], "input_gate": gate},
            )

        result = pipeline.run_variety_classification(image_array)

        return PredictionResponse(
            success=True,
            message="Variety classification completed",
            data={"route": gate["route"], "input_gate": gate, "variety": result},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variety classification failed: {str(e)}")
