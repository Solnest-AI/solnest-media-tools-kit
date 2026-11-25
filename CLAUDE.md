If the user said 'set this up', follow SETUP below.
If they said "check my media tools", run CHECK (SETUP step 7).
If they said "update the media tools kit", run UPDATE.

# Media Tools kit (Solnest AI): Claude's runbook

Installs ffmpeg, whisper.cpp (plus one speech model) and yt-dlp, then proves each one works. Nothing here needs an account or a key. Run every command yourself with the Bash tool; the user never types in a terminal. Plain, friendly sentences, no em-dash characters.

`KIT` below means the kit's home on this computer: `~/solnest/media-tools-kit` (the same path works on Mac and in Windows Git Bash). SETUP step 1 puts the kit there. The three tools and the speech model live outside that folder, so nothing in it has to stay open for them to work.

## Your own changes (read first, every time)

Before anything else, read `~/.solnest/media-tools-kit/my-instructions.md` if it exists and
follow it. It holds this user's own changes to how this tool works, and it wins over the
defaults in this file.

When the user asks to change how this tool works for them (wording, tone, topics, steps,
defaults, what to include or leave out), write the change into that file in plain words,
create it if needed, and read it back to them. **Never edit this tool's own files for
that.** This tool updates itself automatically and replaces its own files, so a change
made there is lost on the next update. Their installed tools (ffmpeg, whisper.cpp, yt-dlp),
their speech models in `whisper-models`, and any file they added to the kit folder are
never touched by an update either.

Good things to keep in that file: which speech model they picked (for example the
multilingual one), and where their models live if it is not the default folder.

## Rules
- Check before installing. If a tool is already there and runs, say so and skip it.
- Never use `sudo` yourself. If Homebrew is missing on a Mac, tell the user it needs their Mac password once, then run the official installer in a way they can type into, or ask them to paste it into Terminal: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
- Do not report anything as working until you have seen its real output.
- Nothing here asks for a key. If the user offers one, say this kit does not need it.
- Never commit, push or publish the kit folder.

## SETUP

### 1. Put the kit in its own folder (once)

Run one of these:

- You are reading this from the GitHub page (no local copy of this repo):

  ```bash
  bash -o pipefail -c "curl -fsSL https://raw.githubusercontent.com/Solnest-AI/solnest-media-tools-kit/main/install.sh | bash"
  ```

- You already have this repo as a folder on this computer: `bash "<that folder>/install.sh"`

The installer copies the kit to `~/solnest/media-tools-kit`, finds Python 3.9 or newer for the updater (or installs one for this user, no admin rights needed), writes a small launcher (`bin/py`), and lists which of the three tools are already on this computer. It does not install the tools: the next steps do. Running it again is safe: it keeps every file the user added.

Read the checklist it printed:

- Lines that start with `[ok]`: fine. `[--] ... not installed yet` is normal on a first run.
- `STOP: ... holds a different kit` or `... a link or a git checkout`: something else already lives at `~/solnest/media-tools-kit`. Nothing was changed. Tell the user what you found and ask what they want to do with it. Do not delete it yourself.
- `ERROR: could not download`: usually the network. Run it once more.
- `ERROR: no working Python`: send them to https://www.python.org/downloads/ (on Windows they must tick "Add python.exe to PATH"). When they say it is installed, run it again.
- Any `[!!]` line: run it once more. If it repeats, ask the user to send the full output to Solnest AI support (the address is at the bottom of README.md).

The copy you downloaded is not needed any more. Leave it, or delete it after a plain yes.

### 2. Detect the system
Mac or Windows? (`uname -s`: `Darwin` is Mac, `MINGW` or `MSYS` is Windows.) On Windows, Claude Code's Bash tool is Git Bash; use PowerShell (`powershell.exe -NoProfile -Command "..."`) for winget and file downloads.

### 3. ffmpeg
- Check: `ffmpeg -version` (first line shows the version).
- Mac: `brew install ffmpeg`
- Windows: `winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements`. Then the user must fully quit and reopen Claude Code so the new PATH loads (batch this with the restart after step 6).

### 4. whisper.cpp (speech to text)
- Check: `whisper-cli --help` (Mac) or `whisper-cli.exe --help`.
- Mac: `brew install whisper-cpp` (provides `whisper-cli`).
- Windows: whisper.cpp has no winget package. Download the official prebuilt file `whisper-bin-x64.zip` from GitHub:
  1. Find the newest release that ships it: `gh api repos/ggml-org/whisper.cpp/releases --jq '[.[] | select(.assets[].name=="whisper-bin-x64.zip")][0].tag_name'`. Recent releases do not all include it. If `gh` is missing or that prints nothing, use release `v1.8.2`, which has it: `https://github.com/ggml-org/whisper.cpp/releases/download/v1.8.2/whisper-bin-x64.zip`.
  2. Download it to `%LOCALAPPDATA%\whisper.cpp` and unpack it (PowerShell: `New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\whisper.cpp"; Invoke-WebRequest <url> -OutFile "$env:LOCALAPPDATA\whisper.cpp\whisper-bin-x64.zip"; Expand-Archive -Force "$env:LOCALAPPDATA\whisper.cpp\whisper-bin-x64.zip" "$env:LOCALAPPDATA\whisper.cpp"`).
  3. Add the folder that contains `whisper-cli.exe` to the user PATH: `[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";<that folder>", "User")`.

### 5. A speech model
Download one model to a folder that stays put:
- Mac: `~/whisper-models/`. Windows: `%USERPROFILE%\whisper-models\`. Make the folder first (`mkdir -p ~/whisper-models`).
- If a model is already there, keep it and skip the download.
- Default: `ggml-base.en.bin` (English, about 150 MB, fast):
  `curl -L -o ~/whisper-models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin`
- If the user records in another language, use `ggml-base.bin` (multilingual) instead. For better accuracy on long recordings, `ggml-small.en.bin` (about 470 MB).
Tell the user where the model lives; skills that transcribe will look there. If they picked something other than the default, write it into `~/.solnest/media-tools-kit/my-instructions.md`.

### 6. yt-dlp
- Check: `yt-dlp --version`.
- Mac: `brew install yt-dlp`
- Windows: `winget install --id yt-dlp.yt-dlp -e --accept-source-agreements --accept-package-agreements`

If anything was installed with winget, do step 8 now (it does not depend on the tools), then ask the user to fully quit and reopen Claude Code, open the kit folder and say "check my media tools". Give them the full path to pick: run `cd ~/solnest/media-tools-kit && (pwd -W 2>/dev/null || pwd)` and read it out.

### 7. Prove it works (CHECK)
Run all of this in a temp folder and delete the files afterwards. It only reads and makes throwaway test files: it changes nothing.
1. `ffmpeg -version` and `yt-dlp --version`: both print a version.
2. Make a spoken test clip:
   - Mac: `say -o test.aiff "Hello from the Solnest AI community"`
   - Windows (PowerShell): `Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SetOutputToWaveFile("$PWD\test.wav"); $s.Speak("Hello from the Solnest AI community"); $s.Dispose()`
3. Convert it to what Whisper wants: `ffmpeg -y -i test.aiff -ar 16000 -ac 1 test16.wav` (Windows: input `test.wav`).
4. Transcribe: `whisper-cli -m ~/whisper-models/ggml-base.en.bin -f test16.wav -nt` (Windows: `whisper-cli.exe -m "$env:USERPROFILE\whisper-models\ggml-base.en.bin" -f test16.wav -nt`). Use the model the user actually has if it is not the default.
5. The output should contain roughly "Hello from the Solnest AI community". Show the user the line Whisper printed.

### 8. Turn on automatic updates (required, silent)

Run this exactly:

```bash
KIT="$HOME/solnest/media-tools-kit"; "$KIT/bin/py" "$KIT/scripts/solnest_autoupdate.py" register --name media-tools-kit --folder "$KIT" --update '{python} scripts/update.py' --after '{python} scripts/update.py --after' --undo '{python} scripts/update.py --undo'
```

From now on the kit keeps itself on the latest release with no one asking: once a day, in the background when Claude Code starts, it installs the newest published release of this runbook and checks that the new files load. If a new release fails that check it puts the old version back by itself. It never touches the installed tools, the speech models, or any file the user added. Relay the one line it prints. Nothing else to tell them.

### 9. Report
One short checklist of what you actually saw: ffmpeg version, whisper-cli works and the test sentence it typed back, model path, yt-dlp version. Then: "You're set. Your video, caption and transcript skills can use these now. The kit keeps itself up to date."

## UPDATE

Updates install themselves (SETUP step 8). They only replace the kit's own files (this runbook and its updater). The tools themselves are updated by Homebrew or winget, not by this kit: `brew upgrade ffmpeg whisper-cpp yt-dlp` on a Mac, `winget upgrade Gyan.FFmpeg yt-dlp.yt-dlp` on Windows. Run those only when the user asks, or when a download with yt-dlp starts failing (an old yt-dlp is the usual cause).

Only when the user asks to update the kit now:

```bash
KIT="$HOME/solnest/media-tools-kit"; "$KIT/bin/py" "$KIT/scripts/update.py" && "$KIT/bin/py" "$KIT/scripts/update.py" --after
```

Relay what it prints in plain words. Then run the SETUP step 8 line once more, so a newer auto-updater is picked up. To go back one version: `"$HOME/solnest/media-tools-kit/bin/py" "$HOME/solnest/media-tools-kit/scripts/update.py" --undo`. If `scripts/update.py` or `bin/py` is missing (an older copy of this kit, or a copy in another folder), run SETUP step 1 instead, then step 8.

"Is it updating itself?": `~/solnest/media-tools-kit/bin/py ~/.solnest/autoupdate.py status`. Use `pause` in place of `status` to stop all automatic updates, and `resume` to turn them back on. If `status` shows the last check failed, offer to update now with the line above.

## Repair

Run the installer again (SETUP step 1), then step 8, then CHECK.

## Uninstall

Ask for a plain yes first, and say what will be removed.
- Stop the updates: `~/solnest/media-tools-kit/bin/py ~/.solnest/autoupdate.py remove --name media-tools-kit`, then delete the folder `~/solnest/media-tools-kit`.
- Mac: `brew uninstall ffmpeg whisper-cpp yt-dlp`, then delete `~/whisper-models`.
- Windows: `winget uninstall Gyan.FFmpeg`, `winget uninstall yt-dlp.yt-dlp`, delete `%LOCALAPPDATA%\whisper.cpp` and `%USERPROFILE%\whisper-models`, and remove that folder from the user PATH.
- Other skills (video, captions, transcripts) stop working without these tools. Say so before removing them.

## Sources (whisper.cpp and the model link checked 2026-11-25, the winget names 2026-11-04)
- ffmpeg on winget: microsoft/winget-pkgs manifests/g/Gyan/FFmpeg. yt-dlp on winget: manifests/y/yt-dlp/yt-dlp.
- whisper.cpp: github.com/ggml-org/whisper.cpp (Homebrew formula whisper-cpp, 1.9.6 on this date; the Windows file `whisper-bin-x64.zip` ships on some releases, for example v1.8.2, not on v1.9.6).
- Models: huggingface.co/ggerganov/whisper.cpp (also fetched by the repo's models/download-ggml-model.sh / .cmd).
