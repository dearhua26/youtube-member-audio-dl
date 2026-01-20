# Contributing to YouTube Audio Downloader Pro

Thank you for considering contributing to this project! We welcome all kinds of contributions, including code, documentation, bug reports, and feature requests.

## How to Contribute

1.  **Fork the Repository**: Click the "Fork" button on the top right.
2.  **Clone your Fork**: `git clone https://github.com/your-username/youtube-member-audio-dl.git`
3.  **Create a Branch**: `git checkout -b feature/your-feature-name`
4.  **Make Changes**: Write your code and tests.
5.  **Commit**: `git commit -m "Add some feature"`
6.  **Push**: `git push origin feature/your-feature-name`
7.  **Create a Pull Request**: Go to the original repository and click "Compare & pull request".

## Development Setup

The project uses Python 3.8+ and standard libraries.

1.  Install dependencies (for dev tools): `pip install pyinstaller`
2.  Run the UI: `python scripts/downloader_ui.py`
3.  Build EXE: `python -m PyInstaller --onefile --windowed --name "YouTubeAudioDownloader" scripts/downloader_ui.py`

## Code Style

- Follow PEP 8 guidelines for Python code.
- Write clear comments for complex logic.
- Ensure variable names are descriptive.

## Reporting Bugs

Please use the [Issues](https://github.com/dearhua26/youtube-member-audio-dl/issues) page to report bugs. Include:
- Your OS version
- Python version
- Steps to reproduce
- Error logs or screenshots

Thank you for helping make this project better! 🚀
