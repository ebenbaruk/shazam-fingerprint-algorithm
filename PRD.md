# PRD: Shazam Audio Fingerprinting Algorithm

## Overview

A Python implementation of the Shazam audio fingerprinting algorithm for identifying songs from audio samples. Based on the 2003 paper "An Industrial-Strength Audio Search Algorithm" by Avery Wang.

## Core Concept

The algorithm creates a "fingerprint" of audio by:
1. Converting audio to a spectrogram
2. Finding peak frequencies (constellation points)
3. Pairing peaks into hashes
4. Matching hashes against a database

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Audio     │───▶│ Spectrogram │───▶│    Peak     │───▶│   Hash      │
│   Input     │    │   (FFT)     │    │  Detection  │    │ Generation  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Result    │◀───│   Match     │◀───│  Database   │◀───│   Store/    │
│             │    │  Scoring    │    │   Lookup    │    │   Query     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Components

### 1. Audio Preprocessing (`audio.py`)

**Purpose:** Load and normalize audio files

**Functions:**
- `load_audio(filepath)` → Returns mono audio array at 44100 Hz
- `normalize(audio)` → Normalize amplitude to [-1, 1]

**Dependencies:** `librosa` or `scipy.io.wavfile`

---

### 2. Spectrogram Generation (`spectrogram.py`)

**Purpose:** Convert time-domain audio to frequency-domain

**Functions:**
- `compute_spectrogram(audio, sample_rate)` → Returns 2D magnitude spectrogram

**Parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| FFT size | 4096 | Good frequency resolution |
| Hop size | 2048 | 50% overlap |
| Window | Hanning | Reduces spectral leakage |

---

### 3. Peak Detection (`peaks.py`)

**Purpose:** Find constellation points (local maxima in spectrogram)

**Functions:**
- `find_peaks(spectrogram, threshold)` → Returns list of (time, freq) tuples

**Algorithm:**
1. Apply maximum filter (neighborhood comparison)
2. Keep points where value equals local maximum
3. Filter by minimum amplitude threshold

**Parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Neighborhood size | 20x20 | Balance between density and uniqueness |
| Amplitude threshold | Top 1% | Keep strongest peaks only |

---

### 4. Fingerprint Generation (`fingerprint.py`)

**Purpose:** Create hashes from peak pairs

**Functions:**
- `generate_hashes(peaks, song_id=None)` → Returns list of (hash, time_offset, song_id)

**Hash Structure:**
```
hash = sha1(f"{freq1}|{freq2}|{time_delta}")[:20]
```

**Pairing Rules:**
- Target zone: 1-200 time units after anchor
- Fan-out: Pair each anchor with up to 15 targets
- This creates combinatorial robustness

**Parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Target zone start | 1 | Skip immediate neighbors |
| Target zone end | 200 | ~5 seconds lookahead |
| Fan-out | 15 | Balance storage vs. accuracy |

---

### 5. Database (`database.py`)

**Purpose:** Store and retrieve fingerprints

**Functions:**
- `insert(song_id, song_name, hashes)` → Store fingerprints
- `query(hashes)` → Returns matching (song_id, time_offset) pairs
- `get_song_name(song_id)` → Returns song name

**Schema:**
```sql
-- songs table
CREATE TABLE songs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- fingerprints table
CREATE TABLE fingerprints (
    hash TEXT NOT NULL,
    song_id INTEGER NOT NULL,
    time_offset INTEGER NOT NULL
);

CREATE INDEX idx_hash ON fingerprints(hash);
```

**Implementation:** SQLite for simplicity

---

### 6. Matching (`matcher.py`)

**Purpose:** Identify songs from query fingerprints

**Functions:**
- `match(query_hashes, db)` → Returns best matching song or None

**Algorithm:**
1. Look up all query hashes in database
2. For each match, compute time difference: `db_offset - query_offset`
3. Group matches by (song_id, time_diff)
4. Song with most aligned matches wins

**Scoring:**
```python
# Matches that align temporally are strong evidence
score = count of matches with same time_diff
confidence = score / total_query_hashes
```

**Threshold:** Minimum 5 aligned matches to declare a match

---

### 7. Main Interface (`shazam.py`)

**Functions:**
- `add_song(filepath)` → Fingerprint and store a song
- `identify(filepath)` → Identify a song from audio sample

---

## File Structure

```
shazam-fingerprint-algorithm/
├── shazam/
│   ├── __init__.py
│   ├── audio.py
│   ├── spectrogram.py
│   ├── peaks.py
│   ├── fingerprint.py
│   ├── database.py
│   ├── matcher.py
│   └── shazam.py
├── tests/
│   └── test_shazam.py
├── requirements.txt
├── main.py
└── README.md
```

## Dependencies

```
numpy>=1.21.0
scipy>=1.7.0
librosa>=0.9.0
```

## Usage

```python
from shazam import Shazam

# Initialize
shazam = Shazam("fingerprints.db")

# Add songs to database
shazam.add_song("songs/song1.mp3")
shazam.add_song("songs/song2.mp3")

# Identify a sample
result = shazam.identify("sample.wav")
print(f"Match: {result.song_name}, confidence: {result.confidence}")
```

## CLI Interface

```bash
# Add a song
python main.py add path/to/song.mp3

# Add all songs in a directory
python main.py add-dir path/to/songs/

# Identify a sample
python main.py identify path/to/sample.wav
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Fingerprint speed | >10x realtime |
| Identification speed | <1 second for 10-second sample |
| Accuracy | >90% with clean audio |
| Database size | ~10KB per minute of audio |

## Key Design Decisions

1. **SQLite over in-memory dict**: Persists between runs, handles large libraries
2. **SHA1 hashes**: Fast, sufficient collision resistance for this use case
3. **Librosa for audio**: Handles multiple formats, resampling built-in
4. **50% FFT overlap**: Standard practice, good time resolution
5. **Fan-out of 15**: Empirically good balance per original paper

## Testing Strategy

1. **Unit tests**: Each module independently
2. **Integration test**: Full pipeline with known songs
3. **Robustness tests**:
   - Add noise to samples
   - Test with short clips (5-10 seconds)
   - Test with different sample rates

## Implementation Order

1. `audio.py` - Load audio files
2. `spectrogram.py` - Generate spectrograms
3. `peaks.py` - Find constellation points
4. `fingerprint.py` - Generate hashes
5. `database.py` - Store/retrieve fingerprints
6. `matcher.py` - Match algorithm
7. `shazam.py` - Main interface
8. `main.py` - CLI
9. Tests

## Success Criteria

- Can add songs to database
- Can identify 10-second clips of known songs
- Works with MP3, WAV, FLAC input
- Handles moderate background noise
