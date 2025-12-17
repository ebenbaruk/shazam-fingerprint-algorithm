# Shazam Audio Fingerprinting Algorithm

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python implementation of the Shazam audio fingerprinting algorithm for identifying songs from audio samples. Based on the 2003 paper ["An Industrial-Strength Audio Search Algorithm"](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf) by Avery Wang.

## Features

- Identify songs from short audio clips (5-10 seconds)
- Robust to background noise and audio quality degradation
- Fast fingerprinting and matching
- Simple CLI and Python API
- SQLite database for persistent storage
- Supports MP3, WAV, FLAC, M4A, OGG formats

## How It Works

```
Audio → Spectrogram → Peak Detection → Hash Generation → Database Match
```

1. **Spectrogram**: Convert audio to frequency-domain using FFT (4096-point)
2. **Peak Detection**: Find constellation points (local maxima in spectrogram)
3. **Fingerprinting**: Pair peaks into hashes with time offsets
4. **Matching**: Find time-aligned hash matches to identify songs

The key insight is **temporal alignment**: matching hashes must occur at consistent time offsets to confirm a match, making the algorithm robust to noise.

## Quick Start

```bash
# Install
git clone https://github.com/ebenbaruk/shazam-fingerprint-algorithm
cd shazam-fingerprint-algorithm
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy 'numba==0.60.0' 'llvmlite==0.43.0' librosa

# Add songs and identify
python main.py add song.mp3
python main.py identify sample.wav
```

## Installation

```bash
# Clone the repository
git clone https://github.com/ebenbaruk/shazam-fingerprint-algorithm
cd shazam-fingerprint-algorithm

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install numpy scipy
pip install 'numba==0.60.0' 'llvmlite==0.43.0'
pip install librosa
```

## Usage

### Command Line

```bash
# Add a song to the database
python main.py add path/to/song.mp3

# Add all songs in a directory
python main.py add-dir path/to/songs/

# Identify a song from an audio sample
python main.py identify path/to/sample.wav

# List all songs in the database
python main.py list

# Use a custom database file
python main.py --db custom.db add song.mp3
```

### Python API

```python
from shazam import Shazam

# Initialize with database path
shazam = Shazam("fingerprints.db")

# Add songs to database
shazam.add_song("song1.mp3")
shazam.add_song("song2.mp3", name="Custom Name")

# Identify a sample
result = shazam.identify("sample.wav")
if result:
    print(f"Match: {result.song_name}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Aligned matches: {result.aligned_matches}")
else:
    print("No match found")

# List all songs
for song_id, name in shazam.list_songs():
    print(f"{song_id}: {name}")

# Get database stats
stats = shazam.stats()
print(f"Songs: {stats['songs']}, Fingerprints: {stats['fingerprints']}")
```

## Project Structure

```
shazam-fingerprint-algorithm/
├── shazam/
│   ├── __init__.py       # Package exports
│   ├── audio.py          # Audio loading and normalization
│   ├── spectrogram.py    # FFT spectrogram generation
│   ├── peaks.py          # Constellation point detection
│   ├── fingerprint.py    # Hash generation from peak pairs
│   ├── database.py       # SQLite storage layer
│   ├── matcher.py        # Time-aligned matching algorithm
│   └── shazam.py         # Main interface
├── main.py               # CLI interface
├── requirements.txt      # Python dependencies
├── PRD.md                # Product requirements document
└── README.md             # This file
```

## Algorithm Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Sample rate | 44100 Hz | Standard audio sample rate |
| FFT size | 4096 | Frequency resolution (~10 Hz per bin) |
| Hop size | 2048 | 50% overlap between frames |
| Peak neighborhood | 20x20 | Local maximum filter size |
| Target zone | 1-200 frames | Time range for pairing peaks (~5s) |
| Fan-out | 15 | Max targets per anchor peak |
| Min matches | 5 | Minimum aligned matches for identification |

## Performance

| Metric | Typical Value |
|--------|---------------|
| Fingerprint speed | ~10x realtime |
| Identification speed | <1 second for 10s sample |
| Storage | ~10KB per minute of audio |
| Accuracy | >90% with clean audio |

## How Matching Works

The algorithm doesn't just count hash matches—it looks for **time-aligned** matches:

1. For each query hash that matches a database hash, compute the time difference: `db_offset - query_offset`
2. Group matches by `(song_id, time_difference)`
3. The song with the most matches at the same time offset wins

This temporal alignment is what makes the algorithm robust to noise and able to identify songs even from short clips recorded in noisy environments.

```
Query:     [hash_A at t=10] [hash_B at t=15] [hash_C at t=20]
Database:  [hash_A at t=110] [hash_B at t=115] [hash_C at t=120]

Time diff: 100, 100, 100 → All aligned! Strong match.
```

## Dependencies

- **numpy**: Numerical operations
- **scipy**: FFT and signal processing
- **librosa**: Audio file loading and resampling
- **numba/llvmlite**: JIT compilation (librosa dependency)

## Supported Audio Formats

- MP3
- WAV
- FLAC
- M4A
- OGG

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- [An Industrial-Strength Audio Search Algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf) - Original Shazam paper by Avery Wang (2003)
- [How Shazam Works](https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition) - Toptal article explaining the algorithm

## Author

**Eli Benbaruk** - [GitHub](https://github.com/ebenbaruk)