import numpy as np
from scipy.ndimage import maximum_filter

NEIGHBORHOOD_SIZE = 20


def find_peaks(spectrogram: np.ndarray, amp_min: float = None) -> list[tuple[int, int]]:
    """Find local maxima in spectrogram (constellation points).

    Args:
        spectrogram: 2D array (frequency_bins, time_frames)
        amp_min: Minimum amplitude threshold. If None, uses mean + 2*std.

    Returns:
        List of (time_idx, freq_idx) tuples for each peak.
    """
    # Apply maximum filter to find local maxima
    local_max = maximum_filter(spectrogram, size=NEIGHBORHOOD_SIZE)

    # Points that equal local max are peaks
    is_peak = spectrogram == local_max

    # Set amplitude threshold
    if amp_min is None:
        amp_min = np.mean(spectrogram) + 2 * np.std(spectrogram)

    # Filter by amplitude
    is_peak &= spectrogram > amp_min

    # Get coordinates (freq_idx, time_idx) and convert to (time_idx, freq_idx)
    freq_idx, time_idx = np.where(is_peak)

    # Return as list of (time, freq) tuples
    return list(zip(time_idx.tolist(), freq_idx.tolist()))
