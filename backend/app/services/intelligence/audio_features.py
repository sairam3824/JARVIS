from __future__ import annotations

from models.contracts import AudioFeatureProfile, BaseAudioFeatureExtractor


class LightweightAudioFeatureExtractor(BaseAudioFeatureExtractor):
    async def extract(self, audio_bytes: bytes, filename: str) -> AudioFeatureProfile:
        byte_length = len(audio_bytes)
        signal_strength = min(byte_length / 500000, 1.0)
        return AudioFeatureProfile(
            duration_seconds=None,
            signal_strength=signal_strength,
            file_size_bytes=byte_length,
            descriptors={"filename": filename},
        )

