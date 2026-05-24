from __future__ import annotations

import base64
import io

import cv2
import numpy as np
import qrcode

from models.contracts import QRResult


class QRService:
    async def generate(self, payload_text: str) -> QRResult:
        qr_image = qrcode.make(payload_text)
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return QRResult(mode="generate", payload_text=payload_text, image_base64=encoded)

    async def scan(self, image_bytes: bytes) -> QRResult:
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            return QRResult(mode="scan", decoded_text=None)
        detector = cv2.QRCodeDetector()
        decoded_text, _, _ = detector.detectAndDecode(image)
        return QRResult(mode="scan", decoded_text=decoded_text or None)

