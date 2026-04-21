# Copyright (c) 2026 Valerio Fuoglio
# Licensed under the MIT License.

import numpy as np
import librosa
import pyloudnorm as pyln
from .utils import console

def analyze(path: str, verbose: bool = True) -> dict:
    if verbose:
        console.print(f"[yellow]→ Loading audio:[/yellow] {path}")
    y, sr = librosa.load(path, sr=None, mono=True)

    if verbose:
        console.print(f"[yellow]→ Computing spectral and loudness features for:[/yellow] {path}")

    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.95)))

    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    hf_energy = float(np.sum(S[freqs > 10000]) / np.sum(S))

    meter = pyln.Meter(sr)
    lufs = float(meter.integrated_loudness(y))
    lra = float(meter.loudness_range(y))

    rms_frame = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms_frame))
    rms_db = float(librosa.amplitude_to_db([rms_mean], ref=1.0)[0])

    peak_amp = float(np.max(np.abs(y)))
    peak_db = float(librosa.amplitude_to_db([peak_amp], ref=1.0)[0])

    dynamic_range = float(peak_db - rms_db)

    return {
        "y": y,
        "sr": sr,
        "centroid": centroid,
        "bandwidth": bandwidth,
        "rolloff": rolloff,
        "hf_energy": hf_energy,
        "lufs": lufs,
        "lra": lra,
        "rms_mean": rms_mean,
        "rms_db": rms_db,
        "peak_amp": peak_amp,
        "peak_db": peak_db,
        "dynamic_range": dynamic_range,
    }

def score(stats: dict) -> float:
    return (
        stats["centroid"] * 0.20 +
        stats["bandwidth"] * 0.20 +
        stats["rolloff"] * 0.20 +
        stats["hf_energy"] * 0.10 +
        (stats["dynamic_range"] + 60) * 0.15 +
        (stats["lufs"] + 40) * 0.15
    )

def degradation_index(stats: dict) -> float:
    """
    Lower = worse (more degraded)
    Higher = better (less degraded)

    Components:
    - rolloff: upper frequency limit (higher = better)
    - hf_energy: high-frequency content (higher = better)
    - dynamic_range: more dynamic = better
    - lufs: quieter files often retain more dynamic range, but we normalize it

    We normalize each component to keep the scale stable.
    """

    # Normalize components
    roll = stats["rolloff"] / 20000.0          # typical MP3 max ~20 kHz
    hf = stats["hf_energy"] * 50.0             # HF energy is tiny, scale it up
    dr = stats["dynamic_range"] / 20.0         # typical DR range ~0–20 dB
    loud = (stats["lufs"] + 40) / 40.0         # LUFS normalized to 0–1 range

    # Weighted sum
    return (
        roll * 0.40 +
        hf * 0.25 +
        dr * 0.25 +
        loud * 0.10
    )

def estimate_real_bitrate(stats: dict) -> str:
    roll = stats["rolloff"]
    hf = stats["hf_energy"]

    if roll < 16000 or hf < 0.012:
        return "≈128 kbps"
    if roll < 17500 or hf < 0.018:
        return "≈160 kbps"
    if roll < 18500 or hf < 0.022:
        return "≈192 kbps"
    if roll < 19500 or hf < 0.028:
        return "≈256 kbps"
    return "≈320 kbps"

def fake_320_detector(stats: dict, bitrate: int) -> str:
    if bitrate < 256000:
        return "ℹ️  Not a 320 kbps file — skipping authenticity check."

    estimated = estimate_real_bitrate(stats)
    if estimated != "≈320 kbps":
        return f"⚠️  Possible fake 320 kbps (real content looks like {estimated})"

    return "✔️  High‑quality 320 kbps (HF preserved)"
