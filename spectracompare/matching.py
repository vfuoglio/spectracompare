# Copyright (c) 2026 Valerio Fuoglio
# Licensed under the MIT License.

import numpy as np
import librosa
from numpy.linalg import norm
from .utils import console

def similarity_chroma(y1, sr1, y2, sr2):
    c1 = np.mean(librosa.feature.chroma_stft(y=y1, sr=sr1), axis=1)
    c2 = np.mean(librosa.feature.chroma_stft(y=y2, sr=sr2), axis=1)
    return float(np.dot(c1, c2) / (norm(c1) * norm(c2)))

def fingerprint_file_for_matching(path, sr=22050):
    y, sr = librosa.load(path, sr=sr, mono=True)
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr), axis=1)
    return chroma, sr

def similarity_check_files(f1, f2, threshold=0.85):
    console.print("[yellow]→ Checking whether the two files contain the same song...[/yellow]")

    y1, sr1 = librosa.load(f1, sr=22050, mono=True)
    y2, sr2 = librosa.load(f2, sr=22050, mono=True)

    sim = similarity_chroma(y1, sr1, y2, sr2)
    console.print(f"[cyan]Similarity score: {sim:.3f}[/cyan]")

    if sim < threshold:
        console.print(
            "\n[bold red]❌ The two files do NOT appear to contain the same song.[/bold red]\n"
            "Spectral comparison only makes sense when the audio content is identical.\n"
            "Please provide two versions of the same track.\n"
        )
        import sys
        sys.exit(1)

    console.print("[green]✔ The two files appear to be the same song.[/green]\n")
