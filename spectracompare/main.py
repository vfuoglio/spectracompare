# Copyright (c) 2026 ${COPYRIGHT_NAME}
# Licensed under the MIT License.

import os
import sys
import json
import argparse
from datetime import datetime
from rich.table import Table

from .utils import console, get_bitrate
from .analysis import analyze, score, degradation_index, estimate_real_bitrate, fake_320_detector
from .plots import plot_spectrogram, plot_waveform_overlay
from .matching import similarity_check_files
from .batch import batch_compare_folders

def compare_two_files(
    f1,
    f2,
    json_out=None,
    with_spectrogram=False,
    with_waveform=False,
):
    """Single-mode comparison between two MP3 files of the same song."""
    similarity_check_files(f1, f2)

    s1 = analyze(f1, verbose=True)
    s2 = analyze(f2, verbose=True)

    score1 = float(score(s1))
    score2 = float(score(s2))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    spec_path = None
    wave_path = None

    if with_spectrogram:
        console.print("[yellow]→ Generating spectrogram comparison...[/yellow]")
        spec_path = f"spectrogram_comparison_{ts}.png"
        plot_spectrogram(s1, s2, f1, f2, out_path=spec_path)

    if with_waveform:
        console.print("[yellow]→ Generating waveform overlay plot...[/yellow]")
        wave_path = f"waveform_overlay_{ts}.png"
        plot_waveform_overlay(s1, s2, f1, f2, out_path=wave_path)

    table = Table(title="Spectral, Loudness & Dynamic Range Comparison", style="bold cyan")
    table.add_column("Metric")
    table.add_column(os.path.basename(f1), justify="right")
    table.add_column(os.path.basename(f2), justify="right")

    for key in [
        "centroid",
        "bandwidth",
        "rolloff",
        "hf_energy",
        "lufs",
        "lra",
        "rms_db",
        "peak_db",
        "dynamic_range",
    ]:
        table.add_row(key, f"{s1[key]:.4f}", f"{s2[key]:.4f}")

    console.print(table)

    real1 = estimate_real_bitrate(s1)
    real2 = estimate_real_bitrate(s2)

    # Compute degradation indices
    deg1 = degradation_index(s1)
    deg2 = degradation_index(s2)

    console.print("\n[bold yellow]=== QUALITY DECISION ===[/bold yellow]")

    # Show scores for transparency
    console.print(f"[cyan]{f1}[/cyan] score: [bold]{score1:.4f}[/bold]")
    console.print(f"[cyan]{f2}[/cyan] score: [bold]{score2:.4f}[/bold]")
    console.print(f"[cyan]{f1}[/cyan] degradation index: [bold]{deg1:.4f}[/bold]")
    console.print(f"[cyan]{f2}[/cyan] degradation index: [bold]{deg2:.4f}[/bold]\n")

    # Threshold for "too close to call"
    threshold = 0.03  # 3% difference

    if abs(deg1 - deg2) < threshold:
        console.print(
            "[yellow]Both files exhibit very similar degradation characteristics.[/yellow]\n"
            "Differences are too small to confidently declare a higher‑quality version.\n"
        )
    else:
        if deg1 > deg2:
            console.print(
                f"[bold green]👉 {f1} appears to be higher quality (less degraded).[/bold green]"
            )
        else:
            console.print(
                f"[bold green]👉 {f2} appears to be higher quality (less degraded).[/bold green]"
            )


    console.print("\n[bold magenta]=== Fake 320 kbps Detection ===[/bold magenta]")
    bitrate1 = get_bitrate(f1)
    bitrate2 = get_bitrate(f2)
    fake1 = fake_320_detector(s1, bitrate1)
    fake2 = fake_320_detector(s2, bitrate2)
    console.print(f"{f1}: {fake1}")
    console.print(f"{f2}: {fake2}")

    console.print("\n[bold cyan]=== Loudness & Dynamic Range Notes ===[/bold cyan]")
    console.print(
        f"{os.path.basename(f1)}: {s1['lufs']:.2f} LUFS, DR {s1['dynamic_range']:.2f} dB\n"
        f"{os.path.basename(f2)}: {s2['lufs']:.2f} LUFS, DR {s2['dynamic_range']:.2f} dB\n"
        "LUFS reflects perceived loudness; closer values mean similar loudness.\n"
        "Dynamic range indicates punch and nuance; higher values usually feel more natural.\n"
    )

    console.print("[bold cyan]Analysis complete![/bold cyan]\n")

    result = {
        "mode": "single",
        "file1": {
            "path": f1,
            "bitrate": bitrate1,
            "features": {k: v for k, v in s1.items() if k not in ['y', 'sr']},
            "score": score1,
            "estimated_real_bitrate": real1,
            "fake_320_check": fake1,
        },
        "file2": {
            "path": f2,
            "bitrate": bitrate2,
            "features": {k: v for k, v in s2.items() if k not in ['y', 'sr']},
            "score": score2,
            "estimated_real_bitrate": real2,
            "fake_320_check": fake2,
        },
        "plots": {
            "spectrogram": spec_path,
            "waveform_overlay": wave_path,
        },
    }

    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        console.print(f"[green]✔ Results exported to JSON: {json_out}[/green]")


def main():
    console.print("[bold cyan]\n🎵 SpectraCompare — MP3 Audio Quality Analyzer[/bold cyan]")
    console.print(
        "[green]Spectral analysis, LUFS loudness, dynamic range, fake 320 detection, batch matching.[/green]\n"
    )

    parser = argparse.ArgumentParser(
        prog="spectra-compare",
        description="SpectraCompare — MP3 audio quality analyzer.",
    )
    parser.add_argument("input1")
    parser.add_argument("input2")
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--with-spectrogram", action="store_true")
    parser.add_argument("--with-waveform", action="store_true")

    args = parser.parse_args()

    if args.batch:
        if not os.path.isdir(args.input1) or not os.path.isdir(args.input2):
            console.print("[red]In batch mode, both inputs must be directories.[/red]")
            sys.exit(1)

        batch_compare_folders(
            args.input1,
            args.input2,
            json_out=args.json_out,
            with_spectrogram=args.with_spectrogram,
            with_waveform=args.with_waveform,
        )
    else:
        if not os.path.isfile(args.input1) or not os.path.isfile(args.input2):
            console.print("[red]In single mode, both inputs must be files.[/red]")
            sys.exit(1)

        compare_two_files(
            args.input1,
            args.input2,
            json_out=args.json_out,
            with_spectrogram=args.with_spectrogram,
            with_waveform=args.with_waveform,
        )


if __name__ == "__main__":
    main()
