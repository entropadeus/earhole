# Earhole 👂

Stop typing. Start talking. Your computer will figure it out. Fully local, zero bullshit, no cloud nonsense.

## What is it?

Earhole is a desktop app that listens to your microphone, figures out what the hell you just said, and automatically types it wherever you are. No cloud, no bullshit, no privacy-stealing. It runs 100% locally using OpenAI's **Whisper** model.

Use it when:
- You wanna dictate instead of type (because who doesn't?)
- Your wrists need a goddamn break
- You're lazy (relatable)
- You're actually busy and can't type
- The keyboard is across the room and you're comfortable
- You just feel like talking to your computer like a normal person

## How it works

1. **Hold F9** on your keyboard to start recording
2. **Speak clearly** into your microphone
3. **Release F9** to stop recording and begin transcription
4. **The text appears** automatically typed into your active window

That's it. No account creation, no API keys, no internet connection required.

### The flow:
```
Hold F9 → Record audio → Release F9 → Transcribe → Auto-type text
```

The application runs in your system tray, staying out of your way until you need it.

## Why the fuck I built it

Look, I was tired as hell of typing all day. My wrists were killing me, and I just wanted to fucking *talk* into my computer like a normal human instead of pecking away at the keyboard like a chicken.

The thing is, all the existing voice-to-text solutions either:
- Steal your data and send it to some company's servers
- Have annoying latency or require subscription bullshit
- Only work with specific applications
- Are unreliable garbage

So I built Earhole. It's:
- **Offline** — your voice never leaves your machine
- **Fast** — Whisper + faster-whisper = no bullshit delays
- **Works everywhere** — types into any app that accepts text
- **Dead simple** — hold F9, speak, done
- **Respects your privacy** — everything stays local

Basically, I wanted a tool that just *works* without asking permission, tracking me, or being a pain in the ass. Hence Earhole.

## System Requirements

### Minimum
- **OS**: Windows 7+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space (for model + environment)
- **Microphone**: Any working audio input device

### Recommended
- **RAM**: 8GB+
- **GPU**: NVIDIA GPU with CUDA (optional, for faster transcription)
- **Disk**: SSD (faster model loading)

### Disk Space by Model Size
- `tiny`: ~40MB (fastest, least accurate)
- `base`: ~140MB (recommended for most users)
- `small`: ~466MB (better accuracy)
- `medium`: ~1.5GB (high accuracy)
- `large-v3`: ~2.9GB (best accuracy, slowest)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/earhole.git
cd earhole
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

For **GPU acceleration** (NVIDIA only):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Run the application
```bash
python main.py
```

## Usage

### Basic usage
```bash
python main.py
```
This starts Earhole with default settings (base model, auto-detect language).

### Command-line options
```bash
python main.py --model base --language en --no-notifications
```

**Available options:**
- `--model {tiny,base,small,medium,large-v2,large-v3}` — Whisper model size (default: base)
- `--language {en,es,fr,de,...}` — Language code (default: auto-detect)
- `--no-notifications` — Disable desktop notifications

### Keyboard shortcuts
- **F9** — Hold to record, release to transcribe and type
- **System tray icon** — Right-click for menu options

### Configuration
Settings are saved to:
- **Windows**: `%APPDATA%\LocalSTT\config.json`
- **macOS/Linux**: `~/.config/LocalSTT/config.json` (or `~/.LocalSTT/config.json`)

You can manually edit this file to adjust:
- `model_size` — Default Whisper model
- `language` — Default language (null for auto-detect)
- `typing_delay` — Delay between keystrokes in seconds
- `use_clipboard` — Use clipboard paste for typing (faster, more reliable)
- `show_notifications` — Desktop notifications

## Dependencies

- **faster-whisper** — Fast Whisper transcription engine
- **sounddevice** — Microphone audio capture
- **numpy** — Numerical operations
- **pynput** — Keyboard hotkeys and text simulation
- **pyperclip** — Clipboard management
- **pystray** — System tray integration
- **Pillow** — Image handling for tray icon

See `requirements.txt` for version details.

## Troubleshooting

### "No audio recorded" error
- Make sure your microphone isn't dead or muted
- Check system settings and set your audio input as default
- Try: `python -m src.audio_recorder` to list available devices
- Make sure you're actually holding F9, genius

### Transcription is slow
- Smaller models (`tiny` or `base`) are faster, `large` is a fucking tank
- Add a GPU if you've got one and want 3-5x speedup
- The model pre-loads on startup, so first-use won't kill you

### Text isn't typing into my application
- Some apps are locked down and won't accept keyboard simulation (banks, remote desktop, etc.)
- Try `use_clipboard: false` in config if clipboard paste doesn't work
- Security software sometimes blocks keyboard automation
- Some old apps are just weird

### "Model failed to load" error
- Not enough disk space? You need at least 2GB free
- Delete the model cache: `~/.cache/huggingface/hub/` (Linux/macOS) or `%USERPROFILE%\.cache\huggingface\hub\` (Windows)
- Reinstall Whisper if you're desperate

### High CPU/RAM usage
- Bigger models = more power. `large` is going to tank old machines
- Downgrade to `base` or `small` if your computer is struggling
- Close your 47 browser tabs and try again

## Performance Tips

1. **Pre-load the model on startup** — First transcription takes 5-30 seconds while the model loads. Earhole does this automatically, so you're ready to go.

2. **Use clipboard mode** (enabled by default) — Way faster than typing character-by-character. Only disable it if an app is weird about clipboard paste.

3. **Choose a model that matches your hardware**:
   - **Potato CPU**: `tiny` (small and fast, accuracy is... okay)
   - **Normal CPU**: `base` (sweet spot, accurate enough)
   - **Good CPU or GPU**: `small` or `medium` (very accurate)
   - **Gaming rig with GPU**: Go wild with `large-v3` for perfect transcription

4. **Set your language** — Skipping auto-detect speeds things up a bit and improves accuracy if you always speak the same language.

## Building a Standalone Executable

You can package Earhole into a standalone `.exe` for Windows:

```bash
python build_exe.py
```

The executable will be in the `dist/` folder. No Python installation needed to run it.

## Known Limitations

- **Push-to-talk only** — You gotta hold F9 while you speak. No "always listening" mode (which is probably better for your privacy anyway).
- **Local machine only** — Runs on the machine you're using. Can't pipe audio from your weird cousin's setup remotely.
- **English is its jam** — Whisper knows 99 languages but is best with English. Other languages work fine, just expect some quirks.
- **Special characters are weird** — Emojis and fancy unicode stuff might not type correctly into some apps. It's a Windows/Linux/Mac thing.

## Contributing

Found a bug? Have a feature request? Feel free to open an issue or pull request.

## License

MIT License — use it, modify it, share it freely.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) — The amazing speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) — High-performance Whisper implementation
- [pynput](https://github.com/moses-palmer/pynput) — Cross-platform keyboard/mouse control

## FAQ

**Q: Is my voice being recorded and sent to some server?**
A: Hell no. Everything stays on your machine. No internet after the model downloads. Your voice is yours.

**Q: What languages does this thing support?**
A: 99 languages. By default it figures out what language you're speaking. You can lock it to a specific language in settings if you want.

**Q: Works on Mac?**
A: Yep, it's cross-platform. F9 might be different on Mac depending on your keyboard, but it works.

**Q: How good is the transcription?**
A: Scary good if you speak clearly. Quality depends on:
- Your microphone (don't whisper into a potato)
- Background noise (quiet is better)
- Which model you use (`tiny` is okay, `large` is creepy accurate)

**Q: Can I toggle recording instead of holding F9?**
A: Nope. Push-to-talk only. This is intentional—it keeps things simple and makes sure you know when you're recording.

**Q: Does this work with literally every app?**
A: Most of them, yeah. Some are locked down tight (banking sites, remote desktop) and won't accept keyboard simulation. Those are the annoying ones.

---

Built because I got tired of typing. You probably will too.
