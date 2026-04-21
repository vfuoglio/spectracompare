# Copyright (c) 2026 Valerio Fuoglio
# Licensed under the MIT License.

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from .utils import console

def plot_spectrogram(s1, s2, f1, f2, out_path):
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    for i, (stats, title) in enumerate([(s1, f1), (s2, f2)]):
        S = librosa.amplitude_to_db(np.abs(librosa.stft(stats["y"])), ref=np.max)
        img = librosa.display.specshow(
            S, sr=stats["sr"], x_axis="time", y_axis="log", ax=ax[i]
        )
        ax[i].set_title(os.path.basename(title))
        fig.colorbar(img, ax=ax[i], format="%+2.f dB")

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close(fig)
    console.print(f"[green]✔ Spectrogram saved as {out_path}[/green]")

def plot_waveform_overlay(s1, s2, f1, f2, out_path):
    y1 = s1["y"]
    y2 = s2["y"]
    sr1 = s1["sr"]

    min_len = min(len(y1), len(y2))
    y1 = y1[:min_len]
    y2 = y2[:min_len]

    t = np.linspace(0, min_len / sr1, min_len)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(t, y1, alpha=0.6, label=os.path.basename(f1))
    ax.plot(t, y2, alpha=0.6, label=os.path.basename(f2))
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Waveform Overlay")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close(fig)
    console.print(f"[green]✔ Waveform overlay saved as {out_path}[/green]")
