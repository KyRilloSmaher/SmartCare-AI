from ultralytics import YOLO
from PIL import Image
from App.config import get_config
import requests
import io
from App.observability.logger import get_logger

logger = get_logger(__name__)


class DrugNameExtractionService:
    def __init__(self):
        """
        Initialize the service and load the YOLO model once.
        This avoids reloading the model on every request which is expensive.
        """
        self.config = get_config()
        self.model = YOLO(self.config.YOLO_WEIGHTS)

    # ---------------------------------------------------------
    # Public Method (Main Workflow)
    # ---------------------------------------------------------
    def extract(self, file):
        """
        Full pipeline:
        1. Detect regions of interest using YOLO
        2. Crop detected regions
        3. Run OCR on each crop
        4. Return unique extracted drug names
        """

        try:
            logger.info("DrugNameExtraction | Start processing image")

            # Step 1: Run object detection
            detections, crops = self._detect_objects(file)

            if not crops:
                logger.warning("DrugNameExtraction | No detections found")
                return {
                    "detections": [],
                    "active_ingredients": []
                }

            # Step 2: Run OCR on each cropped region
            texts = []
            for crop in crops:
                text = self._run_ocr(crop)

                # Step 3: Validate extracted text
                if text and text.strip():
                    texts.append(text.strip())

            # Step 4: Remove duplicates while preserving order
            unique_texts = self._remove_duplicates(texts)

            logger.info("DrugNameExtraction | Extraction completed")
            logger.info(f"DrugNameExtraction | Texts : {unique_texts}") 

            return {
                "detections": detections,
                "active_ingredients": unique_texts
            }

        except Exception as e:
            logger.error(f"DrugNameExtraction | Error: {str(e)}", exc_info=True)
            raise

    # ---------------------------------------------------------
    # Private Methods
    # ---------------------------------------------------------

    def _detect_objects(self, file):
        """
        Detect bounding boxes in the image using YOLO.

        Returns:
        - detections: metadata (bbox + confidence)
        - crops: list of cropped images based on detected boxes
        """

        try:
            # Convert uploaded file to PIL image
            image = Image.open(file).convert("RGB")

            # Run YOLO inference
            results = self.model(image)[0]

            detections = []
            crops = []

            # Iterate over detected bounding boxes
            for box in results.boxes:
                # Extract coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                # Crop the detected region
                crop = image.crop((x1, y1, x2, y2))
                crops.append(crop)

                # Store detection metadata
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf[0])
                })

            return detections, crops

        except Exception as e:
            logger.error("YOLO detection failed", exc_info=True)
            raise RuntimeError("Detection failed")

    def _run_ocr(self, image):
        """
        Send image to OCR API and extract text.

        Steps:
        1. Convert image to bytes
        2. Send POST request to OCR service
        3. Parse response and return extracted text
        """

        try:
            url = self.config.OCR_SPACE_URL

            # Convert image to byte stream
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            # Prepare request payload
            files = {"file": ("image.png", buffered, "image/png")}
            data = {"apikey": self.config.OCR_API_KEY}

            # Send request to OCR API
            response = requests.post(url, files=files, data=data, timeout=30)

            result = response.json()
            logger.info(f"RUN OCR | RESULT : {result}") 
            # Extract text safely
            parsed_results = result.get("ParsedResults")
            if not parsed_results:
                return ""

            text = parsed_results[0].get("ParsedText", "")
            return text.strip()

        except Exception:
            logger.error("OCR failed", exc_info=True)
            return ""

    def _remove_duplicates(self, texts):
        """
        Remove duplicate strings while preserving order.
        Useful because OCR may return repeated results.
        """

        seen = set()
        unique = []

        for text in texts:
            key = text.lower()
            if key not in seen:
                seen.add(key)
                unique.append(text)

        return unique
