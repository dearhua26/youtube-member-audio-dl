import subprocess
import os
import sys
import shutil
import re

# Configuration
# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YTDLP_EXE = os.path.join(BASE_DIR, "yt-dlp.exe")
LIST_FILE = os.path.join(BASE_DIR, "failed_ids.txt")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")
DOWNLOADED_FILE = os.path.join(BASE_DIR, "downloaded.txt")
ERROR_GUIDE_FILE = os.path.join(BASE_DIR, "ERROR_GUIDE.txt")

DIR_SINGLE = os.path.join(BASE_DIR, "Downloads_Single")
DIR_BATCH = os.path.join(BASE_DIR, "Downloads_Batch")

MAX_RETRIES_PER_VIDEO = 5
MAX_CONSECUTIVE_VIDEO_FAILURES = 5

ERROR_DEFINITIONS = {
    "Sign in to confirm": {
        "title": "需要验证账号 (Cookie 失效)",
        "solution": "检测到 YouTube 要求登录验证。\n原因: 这通常是因为 cookies.txt 过期了或者没有包含会员账号的凭证。\n\n解决方法:\n1. 打开浏览器并登录你的 YouTube 会员账号。\n2. 使用插件重新导出 cookies.txt。\n3. 覆盖当前目录下的 cookies.txt 文件。\n4. 重新运行脚本。"
    },
    "n challenge": {
        "title": "Node.js 环境缺失 (验证失败)",
        "solution": "无法通过 YouTube 的 'n' 参数挑战。\n原因: 你的电脑可能没有按照 Node.js，或者脚本没找到它。\n\n解决方法:\n1. 请访问 https://nodejs.org/ 下载并安装最新的 LTS 版本。\n2. 安装后，重启电脑让环境变量生效。\n3. 再次运行脚本。"
    },
    "Video unavailable": {
        "title": "视频不可用 (无权访问/已删除)",
        "solution": "视频无法下载。\n原因: 该视频可能已被发布者删除，或者是你没有会员权限访问该视频。\n\n解决方法:\n1. 检查该视频链接在浏览器是否能播放。\n2. 确认你的账号是否有权观看此会员视频。"
    },
    "HTTP Error 429": {
        "title": "请求过于频繁 (IP被限流)",
        "solution": "YouTube 暂时限制了你的 IP。\n原因: 短时间内下载了太多视频。\n\n解决方法:\n1. 暂停脚本，休息 10-30 分钟。\n2. 或者尝试重启路由器更换 IP。"
    },
    "EOF occurred in violation of protocol": {
        "title": "网络连接中断 (SSL 握手失败)",
        "solution": "下载过程中连接被强制断开。\n原因: 这是一个常见的网络问题，通常是因为 VPN/代理不稳定，或者防火墙干扰。\n\n解决方法:\n1. 检查你的 VPN 是否稳定，尝试更换线路（如切换到 US 或 TW 节点）。\n2. 确保网络通畅。\n3. 脚本会自动重试该视频 3 次。如果依然失败，请稍后再次运行脚本。"
    }
}

class ErrorAnalyzer:
    def __init__(self):
        self.found_errors = []

    def scan_line(self, line):
        for pattern, info in ERROR_DEFINITIONS.items():
            if pattern in line:
                if info not in self.found_errors:
                    self.found_errors.append(info)

    def has_errors(self):
        return len(self.found_errors) > 0

    def save_guide(self):
        if not self.found_errors:
            return
        
        print(f"\n[智能诊断] 检测到 {len(self.found_errors)} 个问题，正在生成解决方案...")
        with open(ERROR_GUIDE_FILE, "w", encoding="utf-8") as f:
            f.write("="*50 + "\n")
            f.write("       YouTube 下载器 - 智能故障排除指南\n")
            f.write("="*50 + "\n\n")
            f.write(f"检测时间: {subprocess.check_output('date /t', shell=True).decode().strip()}\n\n")
            
            for i, error in enumerate(self.found_errors, 1):
                f.write(f"问题 {i}: {error['title']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"{error['solution']}\n\n")
                f.write("*"*50 + "\n\n")
        
        print(f"!!! 请查看当前目录下的 {ERROR_GUIDE_FILE} 文件以获取修复帮助 !!!\n")

def check_dependencies():
    print("Checking system dependencies...")
    missing = []
    
    # Check Node.js
    if shutil.which("node") is None:
        print("[WARNING] Node.js not found! Audio download may fail.")
        missing.append("Node.js")
    else:
        print("[OK] Node.js found.")

    # Check FFmpeg (local)
    if not os.path.exists("ffmpeg.exe"):
         print("[WARNING] ffmpeg.exe not found! Conversion will fail.")
         missing.append("ffmpeg.exe")
    else:
        print("[OK] ffmpeg.exe found.")

    if missing:
        print("\n" + "!"*50)
        print("MISSING DEPENDENCIES DETECTED:")
        for item in missing:
            print(f" - {item}")
        print("Please run simple_download.bat to fix ffmpeg.")
        print("For Node.js, please install it from nodejs.org.")
        print("!"*50 + "\n")

def load_downloaded_ids():
    downloaded = set()
    if not os.path.exists(DOWNLOADED_FILE):
        return downloaded
    
    try:
        with open(DOWNLOADED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    # format: provider id (e.g., youtube IQvq4HU09F0)
                    downloaded.add(parts[1])
    except Exception as e:
        print(f"[WARNING] Failed to read archive file: {e}")
    
    print(f"[Archive] Loaded {len(downloaded)} already downloaded videos.")
    return downloaded

def extract_id_from_url(url):
    # Match standard youtube id (11 chars) roughly
    # patterns: v=ID, or short url /ID
    # This regex looks for 11 characters after v= or / that are safe chars
    match = re.search(r'(?:v=|be\/)([0-9A-Za-z_-]{11})', url)
    if match:
        return match.group(1)
    return None

def expand_urls(initial_urls):
    expanded_urls = []
    print(f"\n[Playlist Analysis] Scanning {len(initial_urls)} inputs for playlists/channels...")
    
    for url in initial_urls:
        # Check if it looks like a playlist or channel
        if "list=" in url or "/@" in url or "/channel/" in url or "/c/" in url or "/user/" in url or "/videos" in url:
            print(f"  - Expanding playlist/channel: {url}")
            try:
                # Use yt-dlp to flat-dump the playlist
                # --flat-playlist: Don't download, just list
                cmd = [YTDLP_EXE, "--flat-playlist", "--print", "url", url]
                
                # Check for dependencies again just in case (though main checked it)
                if not os.path.exists(YTDLP_EXE):
                     print("    [ERROR] yt-dlp.exe missing logic error.")
                     expanded_urls.append(url)
                     continue

                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding='utf-8', 
                    errors='replace'
                )
                
                if result.returncode == 0:
                    found_urls = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                    if found_urls:
                        print(f"    Found {len(found_urls)} videos.")
                        expanded_urls.extend(found_urls)
                    else:
                         print(f"    [WARNING] No videos found in playlist (or empty). Keeping original.")
                         expanded_urls.append(url)
                else:
                    print(f"    [WARNING] Failed to expand playlist (yt-dlp error). Keeping original URL.")
                    # print(f"    Debug: {result.stderr}")
                    expanded_urls.append(url)
            except Exception as e:
                print(f"    [ERROR] Exception during expansion: {e}")
                expanded_urls.append(url)
        else:
            expanded_urls.append(url)
            
    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(expanded_urls))
    if len(unique_urls) != len(expanded_urls):
         print(f"  - Removed {len(expanded_urls) - len(unique_urls)} duplicate videos.")
         
    return unique_urls

def main():
    check_dependencies()

    print("\n" + "="*50)
    print("      Smart YouTube Downloader")
    print("="*50)
    
    urls = []
    
    # Interactive Input
    print("Select Mode:")
    print("[1] Single Video Download")
    print("[2] Batch Download (File or Paste List)")
    mode = input("Enter choice (1/2): ").strip()

    if mode == "1":
        url = input("\nEnter YouTube URL: ").strip()
        if url:
            urls.append(url)
    else:
        # Batch Mode
        # Check if default file exists to offer as default
        default_prompt = f" (press Enter for '{LIST_FILE}')" if os.path.exists(LIST_FILE) else ""
        path = input(f"\nEnter file path{default_prompt}, or type 'paste' to input manually: ").strip()
        
        target_file = path if path else LIST_FILE
        
        if path.lower() == 'paste':
            print("-" * 30)
            print("Paste URLs below. Enter 'GO' on a new line to finish and start.")
            print("-" * 30)
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'GO':
                        break
                    if line.strip():
                        urls.append(line.strip())
                except EOFError:
                    break
        elif path.lower().startswith("http"):
            # Direct URL input in batch mode
            print(f"Detected URL input: {path}")
            urls.append(path)
        elif os.path.exists(target_file) and (path or os.path.exists(LIST_FILE)):
            # If path provided exists, OR path empty but default exists
            print(f"Reading from {target_file}...")
            with open(target_file, 'r', encoding='utf-8') as f:
                 urls = [line.strip() for line in f if line.strip()]
        else:
             if path:
                print(f"File not found: {path}")
             
             print("Switching to manual input mode...")
             print("-" * 30)
             print("Paste URLs below. Enter 'GO' on a new line to finish and start.")
             print("-" * 30)
             while True:
                try:
                    line = input()
                    if line.strip().upper() == 'GO':
                        break
                    if line.strip():
                        urls.append(line.strip())
                except EOFError:
                    break

    if not urls:
        print("No URLs provided. Exiting.")
        input("Press Enter to exit...")
        return

    # Expand Playlists/Channels
    urls = expand_urls(urls)

    print(f"Ready to process {len(urls)} videos.")
    
    # Determine Output Directory
    if mode == "1":
        current_output_dir = DIR_SINGLE
        print(f"Mode: Single Download -> Saving to: {current_output_dir}")
    else:
        current_output_dir = DIR_BATCH
        print(f"Mode: Batch Download -> Saving to: {current_output_dir}")
        
    if not os.path.exists(current_output_dir):
        os.makedirs(current_output_dir)

    # Load history for fast skipping
    downloaded_ids = load_downloaded_ids()

    global_consecutive_failures = 0
    total_success = 0
    total_skipped = 0
    
    analyzer = ErrorAnalyzer()

    for i, url in enumerate(urls, 1):
        # FAST SKIP LOGIC
        video_id = extract_id_from_url(url)
        if video_id and video_id in downloaded_ids:
            # Print update on same line or simplified log to reduce spam
            # Using carriage return to update inline for skips might be cleaner, 
            # but simple logging is safer for user debugging.
            print(f"Skipping ({i}/{len(urls)}): {video_id} (Already in archive)")
            total_skipped += 1
            continue
        
        print("\n" + "="*50)
        print(f"Processing ({i}/{len(urls)}): {url}")
        print("="*50)

        # Video Retry Loop
        video_success = False

        for attempt in range(1, MAX_RETRIES_PER_VIDEO + 1):
            if attempt > 1:
                print(f"[Retry] Attempt {attempt}/{MAX_RETRIES_PER_VIDEO} for current video...")

            # VidBee-inspired command with Node.js runtime support + optimized for speed & resume
            cmd = [
                YTDLP_EXE,
                "-f", "bestaudio[ext=m4a]/bestaudio",
                "--js-runtimes", "node",
                "--extract-audio",
                "--audio-format", "m4a",
                "--download-archive", DOWNLOADED_FILE,
                "--continue",
                "--cookies", COOKIES_FILE,
                "--paths", current_output_dir,
                "--write-thumbnail",
                "--add-metadata",
                "--file-access-retries", "3",
                "--fragment-retries", "3",
                "--no-playlist",
                "--embed-chapters",
                "--no-mtime",
                "--no-check-certificate",
                "--ignore-errors",
                "--output", "%(title)s.%(ext)s",
                "--ffmpeg-location", BASE_DIR,
                url
            ]

            try:
                # Run yt-dlp and capture output for analysis
                # FORCE UTF-8 for Windows console compatibility
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )

                # Real-time output printing and scanning
                last_was_progress = False
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        content = line.strip()
                        # Check for progress bar output
                        if "[download]" in content and "%" in content:
                            sys.stdout.write(f"\r{content}")
                            sys.stdout.flush()
                            last_was_progress = True
                        else:
                            # If the previous line was a progress bar, we need a newline first
                            if last_was_progress:
                                sys.stdout.write("\n")
                            sys.stdout.write(f"{content}\n")
                            last_was_progress = False
                        
                        analyzer.scan_line(line)

                return_code = process.poll()
                
                if return_code == 0:
                    video_success = True
                    break
                else:
                    if analyzer.has_errors():
                        analyzer.save_guide()
                
            except Exception as e:
                print(f"An error occurred: {e}")

        if video_success:
            print(f"[SUCCESS] Downloaded: {url}")
            global_consecutive_failures = 0
            total_success += 1
        else:
            print(f"[FAILURE] Failed to download: {url} after {MAX_RETRIES_PER_VIDEO} attempts.")
            global_consecutive_failures += 1
            if analyzer.has_errors():
                analyzer.save_guide()

        if global_consecutive_failures >= MAX_CONSECUTIVE_VIDEO_FAILURES:
            print("\n" + "!"*50)
            print(f"STOPPING: Reached {MAX_CONSECUTIVE_VIDEO_FAILURES} consecutive VIDEO failures.")
            print("To protect your account or network, the script is pausing.")
            if analyzer.has_errors():
                analyzer.save_guide()
            print("!"*50)
            break

    print(f"\nTask Finished. Total Success: {total_success}")
    # Keep console open
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
