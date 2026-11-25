# Changelog

## 1.0.0

First release as its own GitHub repo.
- Install by pasting the repo link into Claude Code and saying "set this up".
- The kit lives in `solnest/media-tools-kit` in your home folder. Setup puts it there.
- Updates install themselves once a day, in the background, from published releases only. If a new release does not load, the old one is put back by itself.
- An update never touches your installed tools (ffmpeg, whisper.cpp, yt-dlp), your speech models, or any file you added. Changes you ask for are kept in `~/.solnest/media-tools-kit/my-instructions.md`.
- Windows: a direct download link for whisper.cpp when the GitHub command line is not installed.
