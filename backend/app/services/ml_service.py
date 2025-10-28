"""Machine Learning service for image analysis."""

import base64
import io
import random
from typing import Dict, List, Tuple
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.models.cleaning_event import CleaningState


class MLService:
    """Service for ML-based image analysis."""

    def __init__(self):
        """Initialize ML service."""
        self.use_dummy = settings.ML_USE_DUMMY
        self.model = None
        self.confidence_threshold_clean = settings.ML_CONFIDENCE_THRESHOLD_CLEAN
        self.confidence_threshold_dirty = settings.ML_CONFIDENCE_THRESHOLD_DIRTY

        if not self.use_dummy:
            self._load_model()

    def _load_model(self) -> None:
        """Load ONNX model for inference."""
        model_path = Path(settings.ML_MODEL_PATH)

        if not model_path.exists():
            print(f"Warning: Model not found at {model_path}, using dummy classifier")
            self.use_dummy = True
            return

        try:
            import onnxruntime as ort
            self.model = ort.InferenceSession(
                str(model_path),
                providers=['CPUExecutionProvider']
            )
            print(f"Loaded ONNX model from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}, using dummy classifier")
            self.use_dummy = True

    def analyze_image(
        self,
        image_base64: str
    ) -> Tuple[CleaningState, float, List[str]]:
        """
        Analyze image to determine cleaning state.

        Args:
            image_base64: Base64-encoded image

        Returns:
            Tuple of (state, confidence, issues)
        """
        if self.use_dummy:
            return self._dummy_analysis(image_base64)
        else:
            return self._onnx_analysis(image_base64)

    def _dummy_analysis(
        self,
        image_base64: str
    ) -> Tuple[CleaningState, float, List[str]]:
        """
        Dummy analysis for development/testing.

        Args:
            image_base64: Base64-encoded image

        Returns:
            Tuple of (state, confidence, issues)
        """
        # Decode image to get basic stats
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image)

            # Simple heuristics based on image brightness
            brightness = np.mean(img_array)
            variance = np.var(img_array)

            # Simulate classification based on brightness
            if brightness > 180 and variance < 2000:
                state = CleaningState.CLEAN
                confidence = 0.85 + random.uniform(0, 0.1)
                issues = []
            elif brightness < 100 or variance > 4000:
                state = CleaningState.DIRTY
                confidence = 0.70 + random.uniform(0, 0.15)
                issues = self._generate_dummy_issues("dirty")
            else:
                state = CleaningState.UNCERTAIN
                confidence = 0.55 + random.uniform(0, 0.15)
                issues = self._generate_dummy_issues("uncertain")

        except Exception as e:
            print(f"Error in dummy analysis: {e}")
            state = CleaningState.UNCERTAIN
            confidence = 0.5
            issues = ["No se pudo analizar la imagen"]

        return state, confidence, issues

    def _onnx_analysis(
        self,
        image_base64: str
    ) -> Tuple[CleaningState, float, List[str]]:
        """
        Real ONNX model inference.

        Args:
            image_base64: Base64-encoded image

        Returns:
            Tuple of (state, confidence, issues)
        """
        try:
            # Decode and preprocess image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')

            # Resize to model input size (typically 224x224 for MobileNet)
            image = image.resize((224, 224))
            img_array = np.array(image).astype(np.float32) / 255.0

            # Normalize (ImageNet stats)
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img_array = (img_array - mean) / std

            # Add batch dimension and transpose to NCHW
            img_array = np.transpose(img_array, (2, 0, 1))
            img_array = np.expand_dims(img_array, axis=0)

            # Run inference
            input_name = self.model.get_inputs()[0].name
            output_name = self.model.get_outputs()[0].name
            result = self.model.run([output_name], {input_name: img_array})

            # Process output (assuming 3-class: clean, dirty, uncertain)
            probabilities = result[0][0]
            class_idx = np.argmax(probabilities)
            confidence = float(probabilities[class_idx])

            # Map to CleaningState
            class_map = [CleaningState.CLEAN, CleaningState.DIRTY, CleaningState.UNCERTAIN]
            state = class_map[class_idx]

            # Generate issues based on state
            issues = self._detect_issues(image_data, state)

            return state, confidence, issues

        except Exception as e:
            print(f"Error in ONNX analysis: {e}")
            # Fallback to dummy
            return self._dummy_analysis(image_base64)

    def _detect_issues(
        self,
        image_data: bytes,
        state: CleaningState
    ) -> List[str]:
        """
        Detect specific issues in the image using OpenCV.

        Args:
            image_data: Raw image bytes
            state: Detected cleaning state

        Returns:
            List of detected issues
        """
        if state == CleaningState.CLEAN:
            return []

        issues = []

        try:
            # Convert to OpenCV format
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Edge detection (for visible dirt/trash)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size

            if edge_density > 0.15:
                issues.append("Objetos visibles en el piso o asientos")

            # Brightness analysis
            brightness = np.mean(gray)
            if brightness < 80:
                issues.append("Ventanas o superficies con poca luz, posible suciedad")

            # Variance (texture analysis)
            variance = np.var(gray)
            if variance > 5000:
                issues.append("Superficies con manchas o patrones irregulares")

        except Exception as e:
            print(f"Error detecting issues: {e}")

        # If no specific issues found but state is dirty, add generic message
        if not issues and state == CleaningState.DIRTY:
            issues = ["Revisar limpieza general del bus"]

        return issues

    def _generate_dummy_issues(self, category: str) -> List[str]:
        """
        Generate dummy issues for testing.

        Args:
            category: Issue category ("dirty" or "uncertain")

        Returns:
            List of dummy issues
        """
        dirty_issues = [
            "Papeles o basura visible en el piso",
            "Ventanas con manchas o huellas",
            "Asientos con polvo o residuos",
            "Pasamanos sucios",
        ]

        uncertain_issues = [
            "Revisar ventanillas traseras",
            "Verificar esquinas y rincones",
            "Comprobar áreas de difícil acceso",
        ]

        if category == "dirty":
            return random.sample(dirty_issues, k=random.randint(1, 3))
        else:
            return random.sample(uncertain_issues, k=random.randint(1, 2))


# Global ML service instance
ml_service = MLService()
