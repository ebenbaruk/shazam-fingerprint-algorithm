import hashlib

TARGET_ZONE_START = 1
TARGET_ZONE_END = 200
FAN_OUT = 15


def generate_hashes(peaks: list[tuple[int, int]], song_id: int = None) -> list[tuple[str, int, int]]:
    """Generate fingerprint hashes from peak pairs.

    Args:
        peaks: List of (time_idx, freq_idx) tuples, sorted by time.
        song_id: Optional song identifier to include in output.

    Returns:
        List of (hash_string, anchor_time, song_id) tuples.
    """
    # Sort peaks by time
    peaks = sorted(peaks, key=lambda x: x[0])

    hashes = []
    for i, (t1, f1) in enumerate(peaks):
        # Find targets in the zone after this anchor
        targets = []
        for j in range(i + 1, len(peaks)):
            t2, f2 = peaks[j]
            delta_t = t2 - t1

            if delta_t < TARGET_ZONE_START:
                continue
            if delta_t > TARGET_ZONE_END:
                break

            targets.append((t2, f2, delta_t))

            if len(targets) >= FAN_OUT:
                break

        # Create hash for each anchor-target pair
        for t2, f2, delta_t in targets:
            # Hash: freq1|freq2|delta_t
            hash_input = f"{f1}|{f2}|{delta_t}"
            hash_value = hashlib.sha1(hash_input.encode()).hexdigest()[:20]
            hashes.append((hash_value, t1, song_id))

    return hashes
