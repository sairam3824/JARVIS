from __future__ import annotations

import io

from PIL import Image

from models.contracts import BaseVisionAnalyzer, VisionAnalysisResult


class VisionAnalyzer(BaseVisionAnalyzer):
    async def analyze(self, image_bytes: bytes, filename: str) -> VisionAnalysisResult:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            return VisionAnalysisResult(
                filename=filename, width=0, height=0,
                dominant_colors=[], tags=["invalid-image"],
                summary=f"{filename} could not be decoded as a valid image.",
                similar_assets=[],
            )
        width, height = image.size
        resized = image.resize((32, 32))
        pixels = [resized.getpixel((x, y)) for y in range(resized.height) for x in range(resized.width)]
        avg_r = int(sum(pixel[0] for pixel in pixels) / len(pixels))
        avg_g = int(sum(pixel[1] for pixel in pixels) / len(pixels))
        avg_b = int(sum(pixel[2] for pixel in pixels) / len(pixels))
        dominant_colors = [f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"]
        brightness = (avg_r + avg_g + avg_b) / 3
        tags = ["portrait" if height > width else "landscape"]
        tags.append("bright" if brightness > 140 else "moody")
        if abs(avg_r - avg_b) > 35:
            tags.append("high-contrast")
        summary = f"{filename} looks like a {tags[0]} image with a {tags[1]} palette."
        return VisionAnalysisResult(
            filename=filename,
            width=width,
            height=height,
            dominant_colors=dominant_colors,
            tags=tags,
            summary=summary,
            similar_assets=[],
        )
