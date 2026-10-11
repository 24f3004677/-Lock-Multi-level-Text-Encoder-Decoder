# 🔐 Lock — Multi-level Text Encoder / Decoder

**Lock.exe** — standalone Windows app (≈ **7 MB**)
**Developer:** Sohamdip Santra

A compact, terminal-based encryption tool that encodes and decodes text using multiple random base transformations (bases 2–16). Packaged as a single Windows executable so testers can run it without installing Python.

---

## 🚀 Features

* Multi-level random-base encoding (2 → 16).
* Saves encoded output as JSON in the exact format:

  ```
  {"message": "<encoded string>", "key": [2,3,5,...]}
  ```

  (One-line JSON — ready to copy/share.)
* Decode using saved JSON files (auto-detect latest file, scan subfolders).
* Colorful CLI prompts for easy use (requires terminal supporting ANSI colors).
* Small single-file app — **\~7 MB**.

---

## 📦 Download

Download the latest release (Windows `.exe`) from the Releases section:

**Download (latest release):**
`https://github.com/Sohamdip-Santra1/-Lock-Multi-level-Text-Encoder-Decoder/releases` 

---

## 🗂 IMPORTANT — Where to put `Lock.exe`

**Please place `Lock.exe` inside its own folder** before running it (for example: `C:\Users\YourName\LockTool\`).
**Why:** Lock saves encoded `.json` files in the same folder (or subfolders) where the program is located. If you run the `.exe` from different locations, encoded files may be scattered across your system and become hard to find. Keeping the app in a dedicated folder keeps everything neat and traceable.

Recommended layout:

```
C:\Users\You\Lock\Lock.exe
C:\Users\You\Lock\EncodedFiles\encoded_2025...
C:\Users\You\Lock\log.txt
```

---

## 🧭 How to Use (quick)

1. Put `Lock.exe` in a new folder (recommended).
2. Double-click `Lock.exe` or open a command prompt in that folder and run:

   ```powershell
   ./Lock.exe
   ```
3. Choose:

   * `1` — Encode message
   * `2` — Decode message
   * `3` — Exit
4. Follow on-screen colored prompts:

   * When encoding you’ll be asked for the message and number of encoding levels.
   * You can press **Enter** to accept a timestamped default filename.
   * You can choose to save encoded files in a subfolder.
   * When decoding the tool scans the program folder and subfolders, lists JSON files with indexes, and lets you pick by number or press Enter to decode the latest.

---

## ✅ Example encoded output (one-line JSON)

After encoding, Lock prints the exact saved JSON in one line:

```
{"message":"132 213 021 ...","key":[4,2,9]}
```

You can copy that line or open the saved `.json` file later.

---

## ⚠️ Windows SmartScreen / Security

When opening the `.exe` for the first time, Windows may show:

> *“Windows protected your PC”* or *“Unknown publisher”*

This is normal for unsigned personal apps. To run:

* Click **More info → Run anyway**.

If you want to avoid such warnings later, consider code-signing the executable (optional / advanced).

---


## 🐞 Reporting Issues / Feedback

Please open Issues on this repository or contact me directly:
**Developer:** Sohamdip Santra

Suggested Issue template:

* OS & version (Windows 10/11)
* Steps to reproduce
* `log.txt` content (if available)
* Any error message or screenshot/video

---
