import os
import sys
import glob
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from numpy.linalg import norm
from rich.table import Table

from .utils import console, get_bitrate
from .analysis import analyze, score, estimate_real_bitrate, fake_320_detector, degradation_index
from .matching import fingerprint_file_for_matching

def find_mp3_files(folder):
    return sorted(glob.glob(os.path.join(folder, "**", "*.mp3"), recursive=True))

def process_pair(args):
    fa, fb, sim = args
    s1 = analyze(fa, verbose=False)
    s2 = analyze(fb, verbose=False)

    score1 = float(score(s1))
    score2 = float(score(s2))

    real1 = estimate_real_bitrate(s1)
    real2 = estimate_real_bitrate(s2)

    bitrate1 = get_bitrate(fa)
    bitrate2 = get_bitrate(fb)

    fake1 = fake_320_detector(s1, bitrate1)
    fake2 = fake_320_detector(s2, bitrate2)

    # NEW: degradation index
    deg1 = degradation_index(s1)
    deg2 = degradation_index(s2)

    # NEW: quality decision using degradation index
    if abs(deg1 - deg2) < 0.03:
        summary = "Files have similar degradation levels"
    else:
        summary = (
            f"{os.path.basename(fa)} higher quality"
            if deg1 > deg2
            else f"{os.path.basename(fb)} higher quality"
        )

    return {
        "fileA": {
            "path": fa,
            "bitrate": bitrate1,
            "features": {k: v for k, v in s1.items() if k not in ["y", "sr"]},
            "score": score1,
            "estimated_real_bitrate": real1,
            "fake_320_check": fake1,
            "degradation_index": deg1,   # NEW
        },
        "fileB": {
            "path": fb,
            "bitrate": bitrate2,
            "features": {k: v for k, v in s2.items() if k not in ["y", "sr"]},
            "score": score2,
            "estimated_real_bitrate": real2,
            "fake_320_check": fake2,
            "degradation_index": deg2,   # NEW
        },
        "similarity": sim,
        "summary_note": summary,
    }

def batch_compare_folders(dir1, dir2, json_out=None, with_spectrogram=False, with_waveform=False):

    if with_spectrogram or with_waveform:
        console.print("[bold red]❌ Plot generation is not supported in batch mode.[/bold red]")
        console.print(
            "Multiple worker processes cannot safely write PNG files in parallel.\n"
            "Please rerun batch mode without --with-spectrogram or --with-waveform.\n"
        )
        sys.exit(1)

    console.print(f"[bold cyan]\nBatch mode: comparing folders[/bold cyan]")
    console.print(f"[yellow]Folder A:[/yellow] {dir1}")
    console.print(f"[yellow]Folder B:[/yellow] {dir2}")

    files1 = find_mp3_files(dir1)
    files2 = find_mp3_files(dir2)

    if not files1 or not files2:
        console.print("[red]No MP3 files found in one or both folders.[/red]")
        sys.exit(1)

    console.print(f"[green]Found {len(files1)} MP3s in A, {len(files2)} in B.[/green]")

    console.print("[yellow]→ Building fingerprints for folder B...[/yellow]")
    fingerprints_b = [(f, *fingerprint_file_for_matching(f)) for f in files2]

    matches = []
    used_b = set()

    console.print("[yellow]→ Matching songs between folders by audio content...[/yellow]")
    for fa in files1:
        chroma_a, sr_a = fingerprint_file_for_matching(fa)
        best_sim = 0.0
        best_fb = None

        for fb, chroma_b, sr_b in fingerprints_b:
            sim = float(np.dot(chroma_a, chroma_b) / (norm(chroma_a) * norm(chroma_b)))
            if sim > best_sim:
                best_sim = sim
                best_fb = fb

        if best_fb and best_sim >= 0.85 and best_fb not in used_b:
            matches.append((fa, best_fb, best_sim))
            used_b.add(best_fb)

    if not matches:
        console.print("[red]No matching songs found between the two folders.[/red]")
        sys.exit(0)

    console.print(f"[green]✔ Found {len(matches)} matching song pairs.[/green]\n")

    batch_results = {"mode": "batch", "folderA": dir1, "folderB": dir2, "pairs": []}

    console.print("[yellow]→ Analyzing pairs in parallel...[/yellow]")
    pair_args = [(fa, fb, sim) for (fa, fb, sim) in matches]
    results = []

    with ProcessPoolExecutor() as executor:
        future_map = {executor.submit(process_pair, args): args for args in pair_args}
        for future in as_completed(future_map):
            results.append(future.result())

    ordered = []
    for fa, fb, sim in matches:
        for r in results:
            if r["fileA"]["path"] == fa and r["fileB"]["path"] == fb:
                ordered.append(r)
                break

    for idx, (match, pair) in enumerate(zip(matches, ordered), 1):
        fa, fb, sim = match
        console.print(f"[bold cyan]\n=== Pair {idx} ===[/bold cyan]")
        console.print(f"A: {fa}")
        console.print(f"B: {fb}")
        console.print(f"Similarity: {sim:.3f}")

        s1 = pair["fileA"]["features"]
        s2 = pair["fileB"]["features"]

        table = Table(title="Spectral, Loudness & Dynamic Range Comparison", style="bold cyan")
        table.add_column("Metric")
        table.add_column(os.path.basename(fa), justify="right")
        table.add_column(os.path.basename(fb), justify="right")

        for key in ["centroid", "bandwidth", "rolloff", "hf_energy",
                    "lufs", "lra", "rms_db", "peak_db", "dynamic_range"]:
            table.add_row(key, f"{s1[key]:.4f}", f"{s2[key]:.4f}")

        console.print(table)

        console.print("[bold yellow]Quality summary for this pair:[/bold yellow]")
        console.print(pair["summary_note"])

        console.print("[bold magenta]Degradation Index:[/bold magenta]")
        console.print(f"{fa}: {pair['fileA']['degradation_index']:.4f}")
        console.print(f"{fb}: {pair['fileB']['degradation_index']:.4f}")

        console.print("[bold magenta]Fake 320 kbps Detection for this pair:[/bold magenta]")
        console.print(f"{fa}: {pair['fileA']['fake_320_check']}")
        console.print(f"{fb}: {pair['fileB']['fake_320_check']}")

        batch_results["pairs"].append(pair)

    console.print("\n[bold cyan]=== BATCH SUMMARY ===[/bold cyan]")
    summary = Table(title="Pairing Summary", style="bold cyan")
    summary.add_column("#", justify="right")
    summary.add_column("File A")
    summary.add_column("File B")
    summary.add_column("Similarity")
    summary.add_column("Real BR A")
    summary.add_column("Real BR B")
    summary.add_column("Deg. A")   # NEW
    summary.add_column("Deg. B")   # NEW
    summary.add_column("Summary")

    for idx, (match, pair) in enumerate(zip(matches, ordered), 1):
        fa, fb, sim = match
        summary.add_row(
            str(idx),
            os.path.basename(fa),
            os.path.basename(fb),
            f"{sim:.3f}",
            pair["fileA"]["estimated_real_bitrate"],
            pair["fileB"]["estimated_real_bitrate"],
            f"{pair['fileA']['degradation_index']:.4f}",   # NEW
            f"{pair['fileB']['degradation_index']:.4f}",   # NEW
            pair["summary_note"],
        )

    console.print(summary)
    console.print("\n[bold cyan]Batch analysis complete.[/bold cyan]")
    console.print(f"[green]Matched {len(matches)} song pairs between the two folders.[/green]")

    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(batch_results, f, indent=2)
        console.print(f"[green]✔ Batch results exported to JSON: {json_out}[/green]")
