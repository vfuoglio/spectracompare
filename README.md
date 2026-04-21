# 🎵 **SpectraCompare**  
### *MP3 Audio Quality Analyzer & Comparator*

SpectraCompare is a Python‑based tool for analyzing and comparing MP3 audio quality. It extracts spectral features, measures loudness and dynamic range, detects potential fake 320 kbps encodes, and estimates real content bitrate. The tool can compare individual files or automatically match and analyze entire folders of tracks. Optional visual comparison tools, including spectrograms and waveform overlays, are available in single‑file mode.

---

## ⭐ **Features**

- **Spectral analysis**  
  Centroid, bandwidth, rolloff, high‑frequency energy.

- **Loudness & dynamics**  
  LUFS (integrated loudness), LRA (loudness range), RMS, peak level, dynamic range.

- **Fake 320 kbps detection**  
  Identifies MP3s that were likely upscaled from lower bitrates.

- **Real bitrate estimation**  
  Heuristic estimation of the true content bitrate (128/160/192/256/320 kbps).

- **Song matching**  
  Uses chroma fingerprints to match tracks across folders.

- **Batch mode**  
  Automatically pairs and compares entire folders of MP3s.

- **Visualizations (single mode)**  
  - Spectrogram comparison  
  - Waveform overlay  

- **JSON export**  
  Full machine‑readable analysis output.

- **CLI tool**  
  `spectra-compare` command installed via `pip`.

---

# 🎧 **Audio Theory (Short Explanations)**

### **Spectral Centroid**  
Represents the “brightness” of the audio. Higher values = more high‑frequency content.

### **Spectral Bandwidth**  
Measures how wide the frequency distribution is. Low bandwidth often indicates low‑quality encodes.

### **Spectral Rolloff (95%)**  
The frequency below which 95% of the energy is contained.  
Low rolloff often reveals low‑bitrate MP3s (e.g., 128 kbps cuts off around 16 kHz).

### **High‑Frequency Energy (HF Energy)**  
Percentage of energy above 10 kHz.  
Upscaled MP3s often have very low HF energy.

### **LUFS (Integrated Loudness)**  
A standardized measure of perceived loudness.  
Useful for comparing mastering differences.

### **LRA (Loudness Range)**  
Measures how much the loudness varies over time.  
Low LRA = compressed, flat dynamics.

### **Dynamic Range (Peak – RMS)**  
Higher dynamic range usually means more natural, less squashed audio.

### **Fake 320 Detection**  
Many “320 kbps” MP3s online are actually 128/192 kbps files re‑encoded.  
SpectraCompare detects this by analyzing HF rolloff and spectral energy patterns.

---

# 📦 **Installation**

### **1. Clone the repository**
```
git clone https://github.com/yourname/spectracompare.git
cd spectracompare
```

### **2. Install in editable mode**
```
pip install -e .
```

### **3. Run the CLI**
```
spectra-compare file1.mp3 file2.mp3
```

---

# 🚀 **Running Without Installing**

You can run the tool directly:

```
python -m spectracompare.main file1.mp3 file2.mp3
```

Or for batch mode:

```
python -m spectracompare.main folderA folderB --batch
```

---

# 🧪 **Running in a Virtual Environment**

### **Create a venv**
```
python3 -m venv env
```

### **Activate it**
macOS/Linux:
```
source env/bin/activate
```

Windows:
```
env\Scripts\activate
```

### **Install dependencies**
```
pip install -e .
```

### **Run**
```
spectra-compare file1.mp3 file2.mp3
```

---

# 📁 **Project Structure & File Explanations**

```
spectracompare/
│
├── __init__.py
├── utils.py
├── analysis.py
├── plots.py
├── matching.py
├── batch.py
└── main.py
```

### **`__init__.py`**  
Marks the folder as a Python package.

### **`utils.py`**  
Shared utilities: console output, bitrate extraction, warnings suppression.

### **`analysis.py`**  
Core audio analysis: spectral features, loudness, dynamic range, fake‑320 detection.

### **`plots.py`**  
Generates spectrograms and waveform overlays (single mode only).

### **`matching.py`**  
Chroma‑based fingerprinting and similarity scoring to ensure files are the same song.

### **`batch.py`**  
Folder‑to‑folder matching and parallelized comparison of multiple tracks.

### **`main.py`**  
CLI entry point. Handles argument parsing, single vs batch mode, and JSON export.

---

# 📄 **JSON Output Structure**

### **Single‑file comparison**
```json
{
  "mode": "single",
  "file1": {
    "path": "...",
    "bitrate": 320000,
    "features": {
      "centroid": ...,
      "bandwidth": ...,
      "rolloff": ...,
      "hf_energy": ...,
      "lufs": ...,
      "lra": ...,
      "rms_db": ...,
      "peak_db": ...,
      "dynamic_range": ...
    },
    "score": ...,
    "estimated_real_bitrate": "≈320 kbps",
    "fake_320_check": "✔️ High‑quality 320 kbps"
  },
  "file2": { ... },
  "plots": {
    "spectrogram": "spectrogram_comparison_20240101.png",
    "waveform_overlay": "waveform_overlay_20240101.png"
  }
}
```

### **Batch mode**
```json
{
  "mode": "batch",
  "folderA": "...",
  "folderB": "...",
  "pairs": [
    {
      "fileA": { ... },
      "fileB": { ... },
      "similarity": 0.97,
      "summary_note": "FileA higher quality"
    }
  ]
}
```

---

# ❓ **Frequently Asked Questions (FAQ)**

### **What types of audio files does SpectraCompare support?**  
SpectraCompare currently focuses on **MP3 files**, as MP3 encoding introduces characteristic spectral patterns that can be analyzed reliably. Support for lossless formats (FLAC, WAV) or other lossy codecs (AAC, OGG) may be added in future versions, but the current feature set is optimized specifically for MP3 behavior.

---

### **How accurate is the “fake 320 kbps” detection?**  
Fake‑320 detection is based on **spectral rolloff**, **high‑frequency energy**, and **frequency‑domain artifacts** typical of low‑bitrate encodes.  
The detection is **heuristic**, not absolute:

- It reliably identifies MP3s that were re‑encoded from **128–192 kbps** sources.  
- It may be less certain with **high‑quality VBR** or **studio‑processed material**.  
- It does not claim to be a forensic tool, but it provides strong indicators based on measurable audio features.

Users should treat the result as **evidence**, not a legal or archival guarantee.

---

### **Why do two files with the same bitrate show different quality scores?**  
Bitrate alone does not determine quality. Differences may arise from:

- The **source material** (CD rip vs. YouTube rip)  
- The **encoder** (LAME, Fraunhofer, iTunes, etc.)  
- **Encoding settings** (CBR vs. VBR, lowpass filters, joint stereo modes)  
- **Mastering differences** (compression, EQ, limiting)  

SpectraCompare evaluates the **actual audio content**, not just metadata, which is why two 320 kbps files may differ significantly.

---

### **Why does SpectraCompare check whether two files contain the same song?**  
Spectral comparison is only meaningful when both files contain **identical musical content**.  
Comparing unrelated audio would produce misleading results.  
To prevent this, SpectraCompare uses **chroma‑based fingerprinting** to confirm that both files represent the same musical material before performing deeper analysis.

---

### **What does the quality score represent?**  
The score is a **composite metric** derived from:

- Spectral centroid  
- Spectral bandwidth  
- Spectral rolloff  
- High‑frequency energy  
- Dynamic range  
- Loudness (LUFS)

It is not a standardized audio quality metric, but a **relative indicator** designed to help users compare two versions of the same track.  
Higher scores generally indicate:

- More preserved high‑frequency content  
- Wider spectral distribution  
- Greater dynamic range  
- Less aggressive compression  

---

### **Why does batch mode disable spectrogram and waveform generation?**  
Batch mode uses **parallel processing** to analyze many files efficiently.  
Generating images from multiple processes simultaneously can lead to:

- File corruption  
- Race conditions  
- Inconsistent output  
- Excessive memory usage  

For this reason, visualizations are intentionally restricted to **single‑file mode**, where they can be generated safely and deterministically.

---

### **Does SpectraCompare modify or rewrite audio files?**  
No.  
SpectraCompare is strictly **read‑only**.  
It analyzes audio content but never alters, rewrites, or re‑encodes files.

---

### **Can SpectraCompare determine which version “sounds better”?**  
SpectraCompare provides **objective measurements**, not subjective judgments.  
It can tell you:

- Which file has more preserved high‑frequency content  
- Which file has greater dynamic range  
- Which file is louder or more compressed  
- Whether one file appears to be an upscale  

But “better” depends on listener preference, playback equipment, and context.

---

### **Why does LUFS matter in audio comparison?**  
LUFS (Loudness Units Full Scale) reflects **perceived loudness**, not just peak amplitude.  
Two files may have identical spectral content but differ in loudness due to:

- Mastering  
- Limiting  
- Compression  

LUFS helps distinguish **encoding differences** from **mastering differences**, which is essential when comparing releases from different sources.

---

### **What does the JSON output contain?**  
The JSON file includes:

- Mode (`single` or `batch`)  
- File paths  
- Bitrate metadata  
- Extracted spectral features  
- Loudness and dynamic range metrics  
- Estimated real bitrate  
- Fake‑320 detection result  
- Similarity score (batch mode)  
- Optional plot filenames (single mode)

This structure is designed to be machine‑readable for automation, dashboards, or further analysis.

---

### **Is SpectraCompare suitable for archival or forensic use?**  
SpectraCompare is intended for **technical analysis and personal library management**, not legal or forensic certification.  
It provides strong indicators of encoding quality but does not replace professional forensic audio tools.

---

# 📜 **License**

MIT License — see `LICENSE`.
