import numpy as np
from scipy.signal import stft

FFT_SIZE = 4096
HOP_SIZE = 2048


def compute_spectrogram(audio: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
    """Compute magnitude spectrogram using STFT.

    Returns 2D array: (frequency_bins, time_frames)
    """
    _, _, Zxx = stft(audio, fs=sample_rate, nperseg=FFT_SIZE, noverlap=FFT_SIZE - HOP_SIZE)
    return np.abs(Zxx)
