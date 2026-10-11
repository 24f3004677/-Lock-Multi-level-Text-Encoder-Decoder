# 🔐 Secure Message Tool

A local-first, offline desktop utility for encrypting messages and file attachments
into a single portable `.lem` file that only the intended recipients can open.

Built with **Python + Tkinter**, **ChaCha20-Poly1305** for encryption, and
**Argon2id** for key derivation.

---

## 📌 Motive

Sending a sensitive note or a scanned ID over email or a chat app means trusting
the transport, the platform, and every server in between. Most "encrypted" chat
apps are tied to an account, a network connection, and a vendor.

**Secure Message Tool takes the network out of the equation.**

You encrypt on your machine, get a single `.lem` file, and hand that file to the
recipient however you like — USB drive, email, shared folder, carrier pigeon.
Without the correct password, the file is unreadable ciphertext. There is no
server, no account sync, no telemetry, and no internet connection required.

---

## 🎯 The Problem It Solves

| Pain point | How this tool addresses it |
|---|---|
| Cloud chat apps require accounts, internet, and trust in a vendor | Fully offline; data never leaves your disk unless you move it |
| Sharing one secret with **several** people usually means one password per channel | Multi-select recipients in one message; each recipient's phone number is recorded in the header |
| Sending a photo or PDF alongside a secret is awkward | Attachments (images + PDF) are embedded **inside** the ciphertext, not sent as loose files |
| Password-based encryption is often weak (MD5/SHA, low iteration counts) | Argon2id with 64 MB memory cost and 3 passes, plus authenticated encryption |
| Recipients may not be technical | Plain Tkinter GUI — tick boxes, type a password, click Decrypt |
| Files get half-written if the app crashes or antivirus locks the file | Atomic writes via temp file + `os.replace()` with retry logic (Windows-safe) |

---

## ✨ Features

- **Local accounts** — register and log in with a phone number + password.
  Login passwords are hashed with Argon2id (never stored in plain text).
- **Contact book** — add, edit, and delete contacts; used as the recipient picker.
- **Multi-recipient encryption** — tick one or more contacts; all selected phone
  numbers are stored in the file header.
- **Recipient enforcement** — on decrypt, the tool checks that the logged-in
  user's phone number is in the message's `receiver` list.
- **Message + attachment bundling** — attach `.jpg`, `.jpeg`, `.png`, `.gif`,
  `.bmp`, or `.pdf` files; they are base64-encoded and sealed inside the same
  ciphertext.
- **Single portable output** — everything becomes one `.lem` JSON file.
- **Recent files panel** — double-click to reopen a previously encoded file from
  the app folder.
- **Profile management** — change display name and login password in-app.
- **Scrollable checkbox picker** — custom `CheckList` widget for selecting
  multiple attachments or receivers without the window growing unbounded.
- **Backward compatibility** — can still read legacy v1/v2/v3 `.lem` / `.json`
  files and shows a clear warning that those formats were **not** actually
  encrypted.
- **Background threads** — Argon2id hashing runs off the UI thread so the
  window never freezes.
- **PyInstaller-friendly** — resolves its data directory relative to the
  executable when frozen (`sys.frozen`).

---

## 🏗️ Architecture

The app is a **single-file Tkinter application** organised into a light
controller + screen (frame) pattern. There is no server, no database, and no
network layer — state lives in JSON files next to the executable.

### High-level component map

```
┌─────────────────────────────────────────────────────────────────┐
│                            App (tk.Tk)                          │
│  • owns current_user                                            │
│  • swaps screens via show(FrameClass)                           │
│  • run_async(work, on_done, on_error) → background thread +     │
│    thread-safe callback marshalling via self.after(0, ...)      │
└───────────────┬─────────────────────────────────┬───────────────┘
                │                                 │
        ┌───────▼────────┐                ┌───────▼──────────────┐
        │  LoginFrame    │                │     MainFrame        │
        │  ─ Login tab   │                │  ┌────────────────┐  │
        │  ─ Register    │                │  │  ComposeTab    │  │
        │    tab         │                │  │  DecodeTab     │  │
        └───────┬────────┘                │  │  ContactsTab   │  │
                │                         │  │  ProfileTab    │  │
                │                         │  └────────────────┘  │
                │                         └──────────────────────┘
                │
     ┌──────────▼──────────────────────────────────────────┐
     │              Crypto / Storage layer                 │
     │  derive_key() → Argon2id (raw)                      │
     │  encrypt_text() / decrypt_text() → ChaCha20-Poly1305│
     │  load_json() / save_json() → atomic file writes     │
     │  encode_file_to_base64() / decode_base64_to_file()  │
     └─────────────────────────────────────────────────────┘
```

### Data flow — Compose (encrypt)

```
User types message + ticks receivers + types password
                     │
                     ▼
  encode_file_to_base64() for each attachment
     → "FILE:<name>:<ext>:<base64>"
                     │
                     ▼
  full_text = message + "\n\n---ATTACHMENTS---\n" + blobs
                     │
                     ▼
  salt  = os.urandom(16)
  nonce = os.urandom(12)
  key   = Argon2id(password, salt, t=3, m=64MiB, p=4, len=32)
  ct    = ChaCha20Poly1305(key).encrypt(nonce, full_text, None)
                     │
                     ▼
  JSON envelope (version 4) written to .lem
```

### Data flow — Decode (decrypt)

```
Open .lem  →  json.load  →  detect_version(data, path)
                                │
        ┌───────────────────────┴───────────────────────┐
        │ v >= 2: check current_user.phone ∈ receiver[] │
        └───────────────────────┬───────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │ v4 (current)                      │ v1–v3 (legacy)
              ▼                                   ▼
   ChaCha20-Poly1305 decrypt          legacy_multi_decode() base-N
              │                        
              ▼
   split on "---ATTACHMENTS---"
              │
              ├── body → output textbox
              └── blobs → CheckList → save individually or in bulk
```

### The `.lem` v4 file format

```json
{
  "version": 4,
  "cipher": "chacha20-poly1305",
  "kdf": "argon2id",
  "salt": "<base64, 16 bytes>",
  "nonce": "<base64, 12 bytes>",
  "ciphertext": "<base64>",
  "receiver": ["<phone>", "<phone>"],
  "sender": "<phone>",
  "timestamp": "YYYY-MM-DD HH:MM:SS"
}
```

### Cryptographic parameters

| Parameter | Value |
|---|---|
| KDF | Argon2id (`argon2-cffi`) |
| Time cost | 3 iterations |
| Memory cost | 65 536 KiB (64 MiB) |
| Parallelism | 4 lanes |
| Derived key length | 32 bytes |
| Salt | 16 random bytes per message |
| Nonce | 12 random bytes per message |
| AEAD | ChaCha20-Poly1305 |

Each message gets a **fresh salt and nonce**, so encrypting the same text twice
with the same password produces different ciphertexts.

### Persistence layer

| File | Purpose |
|---|---|
| `users.json` | Local accounts: `{name, phone, login_password_hash}` |
| `contacts.json` | Address book: `[{name, phone}, ...]` |
| `*.lem` | Encrypted message bundles |
| `decoded_attachments/` | Default extraction folder for saved attachments |

Writes go through `save_json()`, which writes to `path + ".tmp"`, `fsync`s, then
`os.replace()`s — retrying up to 5 times on `PermissionError` (common on Windows
when antivirus or another handle briefly locks the file).

### Key classes

| Class | Responsibility |
|---|---|
| `App` | Root window, screen switching, async worker dispatch |
| `LoginFrame` | Login + Register notebook tabs |
| `MainFrame` | Top bar (user + logout) and inner notebook |
| `ComposeTab` | Message editor, attachment picker, receiver picker, encryption |
| `DecodeTab` | File/recent-file picker, decryption, attachment extraction |
| `ContactsTab` / `ContactDialog` | Address book CRUD |
| `ProfileTab` | Change display name and login password |
| `CheckList` | Reusable scrollable multi-select checkbox widget |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| GUI | Tkinter / ttk |
| AEAD | [`cryptography`](https://pypi.org/project/cryptography/) — ChaCha20-Poly1305 |
| KDF | [`argon2-cffi`](https://pypi.org/project/argon2-cffi/) — Argon2id |
| Storage | JSON files (stdlib `json`) |
| Threading | stdlib `threading` + Tk `after()` for UI marshalling |
| Packaging | PyInstaller-compatible (`sys.frozen` aware) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or newer
- `pip`

### Install

```bash
git clone https://github.com/<your-username>/secure-message-tool.git
cd secure-message-tool
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install cryptography argon2-cffi
```

### Run

```bash
python secure_message_tool.py
```

On first launch you'll land on the **Register** tab. Create an account with a
phone number, name, and password (min. 6 characters), then start using the app.

### Optional: build a standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SecureMessageTool" secure_message_tool.py
```

The app detects it's frozen and stores `users.json`, `contacts.json`, and
`decoded_attachments/` next to the executable.

---

## 📖 Usage

### 1. Add contacts
**Contacts → Add…** — enter a name and phone number. These populate the
receiver picker in Compose.

### 2. Encrypt a message
1. Open the **Compose** tab.
2. Type your message.
3. (Optional) **Add…** one or more images/PDFs. Tick any you want to remove.
4. Tick one or more **Receivers**.
5. Enter and confirm a **message password**.
6. Click **Encrypt & Save…** and choose where to store the `.lem` file.

### 3. Decrypt a message
1. Open the **Decode** tab.
2. Click **Open file…** or double-click a file in the **Recent** list.
3. Enter the message password.
4. Click **Decrypt**.
   - If the file lists recipients and your phone number isn't among them,
     decryption is refused.
   - Legacy v1–v3 files decrypt too, but with a warning that they were never
     truly encrypted.
5. The message body appears in the output pane. If attachments were included,
   an **Attachments** panel appears — tick files and click **Save checked…**,
   or use **Save all…**.
6. **Save decoded message…** writes the plaintext body to a `.txt` file.

### 4. Manage your account
**Profile** tab — change your display name or rotate your login password
(old password required).

---

## 🔒 Security Notes

**What this tool does well**

- Authenticated encryption (ChaCha20-Poly1305) — tampered ciphertext fails to
  decrypt rather than silently returning garbage.
- Memory-hard key derivation (Argon2id, 64 MiB) makes offline password
  brute-forcing expensive.
- Fresh salt + nonce per message.
- Zero network access — nothing is transmitted anywhere.
- Login passwords stored only as Argon2id hashes with automatic rehash when
  parameters change.

**What to be aware of**

- **The message password is the only thing protecting the ciphertext.** Choose
  it well; the tool enforces a 6-character minimum but does not enforce entropy.
- **The recipient check is a header-level guard, not cryptography.** Anyone who
  knows the password can strip the `receiver` list and decrypt. It prevents
  accidental opening, not a determined attacker.
- **`users.json` and `contacts.json` are plaintext.** Phone numbers and names
  are readable by anyone with disk access.
- **Legacy v1–v3 files are encoding the text in N rounds of different base.** They use base-N encoding only. The
  app reads them for compatibility and warns loudly.
- **No forward secrecy, no key exchange, no signatures.** This is a symmetric
  password-based file encryption tool, not a messaging protocol.
- **Distributing the password is out of scope.** Send it over a different
  channel than the `.lem` file itself.

---

## 🗺️ Next Improvements 

- [ ] Optional public-key mode (X25519) so recipients need no shared password
- [ ] Sign-then-encrypt so recipients can verify the sender's identity
- [ ] Passphrase strength meter during encryption
- [ ] Encrypt `users.json` / `contacts.json` at rest
- [ ] Drag-and-drop attachment support
- [ ] Dark/light theme toggle
- [ ] Unit tests for `encrypt_text` / `decrypt_text` / attachment round-trips
- [ ] i18n / localisation

---

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the repo and create a feature branch.
2. Keep the single-file structure unless there's a strong reason to split it.
3. Test on at least Windows and one Unix-like OS.
4. Open a pull request describing the change and its motivation.

---

## 📄 License

<!-- Replace with your chosen license -->
Released under the MIT License.

---

## ⚠️ Disclaimer

This is a personal/educational security tool. It has not been independently
audited. Do not rely on it as the sole protection for life-critical, medical,
legal, or high-value financial data.
