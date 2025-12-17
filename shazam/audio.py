import numpy as np
import librosa

SAMPLE_RATE = 44100


def load_audio(filepath: str) -> tuple[np.ndarray, int]:
    """Load audio file, convert to mono, resample to 44100Hz."""
    audio, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)
    return audio, sr


def normalize(audio: np.ndarray) -> np.ndarray:
    """Normalize audio amplitude to [-1, 1]."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        return audio / max_val
    return audio
