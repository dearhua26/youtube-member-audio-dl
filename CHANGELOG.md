# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### Added
- **Lite Release Package**: New distribution option (~10MB) that auto-downloads dependencies on first run.
- **Auto-Dependency Manager**: Integrated logic in `downloader_ui.py` to check for Node.js, FFmpeg, and yt-dlp on startup.
- **GUI**: Complete Tkinter-based graphical user interface with tabs for Download and Settings.
- **Promotional Landing Page**: `docs/index.html` for GitHub Pages.
- **README Refactor**: Clarified project positioning as a general audio downloader with optional Pro features.

### Changed
- Refactored `smart_download.py` logic into `DownloaderApp` class.
- Optimized download strategy to prioritize M4A format directly.
- Improved error handling with `ErrorAnalyzer` providing Chinese guidance.

## [0.2.0] - 2026-01-18

### Added
- **Smart Error Diagnosis**: Automatically analyzes `yt-dlp` output and generates `ERROR_GUIDE.txt`.
- **Node.js Integration**: Added `--js-runtimes node` argument to solve YouTube "n challenge".
- **Batch Script**: `simple_download.bat` for automated environment setup.

### Changed
- Switched default download format to `bestaudio[ext=m4a]`.
- Enhanced console output for better readability.

## [0.1.0] - 2026-01-15

### Added
- Initial release of `smart_download.py` scripts.
- Basic batch download functionality from `failed_ids.txt`.
- Cookie file support for member content.
