"""
YouTube 会员音频下载器 - 图形界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import threading
import subprocess
import sys
import json

# Configuration file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")

# Default settings
DEFAULT_CONFIG = {
    "output_dir": os.path.join(BASE_DIR, "Downloads"),
    "max_retries": 5,
    "max_failures": 5,
    "download_thumbnail": True,
    "embed_metadata": True
}

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 会员音频下载器")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Load config
        self.config = self.load_config()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.download_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.download_tab, text="📥 下载")
        self.notebook.add(self.settings_tab, text="⚙️ 设置")
        
        self.setup_download_tab()
        self.setup_settings_tab()
        
        # Download thread reference
        self.download_thread = None
        self.is_downloading = False
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except:
                pass
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def setup_download_tab(self):
        # URL Input Frame
        url_frame = ttk.LabelFrame(self.download_tab, text="下载链接", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.url_entry = ttk.Entry(url_frame, font=('Arial', 11))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.insert(0, "粘贴 YouTube 链接...")
        self.url_entry.bind('<FocusIn>', lambda e: self.url_entry.delete(0, tk.END) if self.url_entry.get() == "粘贴 YouTube 链接..." else None)
        
        self.single_btn = ttk.Button(url_frame, text="下载单个", command=self.download_single)
        self.single_btn.pack(side=tk.LEFT)
        
        # Batch Frame
        batch_frame = ttk.LabelFrame(self.download_tab, text="批量下载", padding=10)
        batch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.batch_path = tk.StringVar(value=os.path.join(BASE_DIR, "failed_ids.txt"))
        batch_entry = ttk.Entry(batch_frame, textvariable=self.batch_path, state='readonly')
        batch_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(batch_frame, text="选择文件", command=self.browse_batch_file)
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.batch_btn = ttk.Button(batch_frame, text="开始批量下载", command=self.download_batch)
        self.batch_btn.pack(side=tk.LEFT)
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.download_tab, text="下载日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9), state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Stop button
        self.stop_btn = ttk.Button(self.download_tab, text="⏹ 停止下载", command=self.stop_download, state='disabled')
        self.stop_btn.pack(pady=10)
    
    def setup_settings_tab(self):
        # Cookies Frame
        cookies_frame = ttk.LabelFrame(self.settings_tab, text="YouTube Cookies (粘贴内容)", padding=10)
        cookies_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cookies_text = scrolledtext.ScrolledText(cookies_frame, font=('Consolas', 9), height=10)
        self.cookies_text.pack(fill=tk.BOTH, expand=True)
        
        # Load existing cookies
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                    self.cookies_text.insert(tk.END, f.read())
            except:
                pass
        
        save_cookies_btn = ttk.Button(cookies_frame, text="保存 Cookies", command=self.save_cookies)
        save_cookies_btn.pack(pady=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.settings_tab, text="下载选项", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Output directory
        dir_frame = ttk.Frame(options_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="输出目录:").pack(side=tk.LEFT)
        self.output_dir = tk.StringVar(value=self.config.get("output_dir", DEFAULT_CONFIG["output_dir"]))
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=10)
        ttk.Button(dir_frame, text="浏览", command=self.browse_output_dir).pack(side=tk.LEFT)
        
        # Retries
        retry_frame = ttk.Frame(options_frame)
        retry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(retry_frame, text="单视频最大重试:").pack(side=tk.LEFT)
        self.max_retries = tk.IntVar(value=self.config.get("max_retries", 5))
        ttk.Spinbox(retry_frame, from_=1, to=10, textvariable=self.max_retries, width=5).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(retry_frame, text="连续失败停止:").pack(side=tk.LEFT, padx=(20, 0))
        self.max_failures = tk.IntVar(value=self.config.get("max_failures", 5))
        ttk.Spinbox(retry_frame, from_=1, to=10, textvariable=self.max_failures, width=5).pack(side=tk.LEFT, padx=10)
        
        # Checkboxes
        check_frame = ttk.Frame(options_frame)
        check_frame.pack(fill=tk.X, pady=5)
        
        self.download_thumbnail = tk.BooleanVar(value=self.config.get("download_thumbnail", True))
        ttk.Checkbutton(check_frame, text="下载封面图", variable=self.download_thumbnail).pack(side=tk.LEFT, padx=10)
        
        self.embed_metadata = tk.BooleanVar(value=self.config.get("embed_metadata", True))
        ttk.Checkbutton(check_frame, text="嵌入元数据", variable=self.embed_metadata).pack(side=tk.LEFT, padx=10)
        
        # Save button
        ttk.Button(options_frame, text="保存设置", command=self.save_settings).pack(pady=10)
    
    def browse_batch_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.batch_path.set(path)
    
    def browse_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)
    
    def save_cookies(self):
        content = self.cookies_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "Cookies 内容为空!")
            return
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("成功", "Cookies 已保存!")
    
    def save_settings(self):
        self.config["output_dir"] = self.output_dir.get()
        self.config["max_retries"] = self.max_retries.get()
        self.config["max_failures"] = self.max_failures.get()
        self.config["download_thumbnail"] = self.download_thumbnail.get()
        self.config["embed_metadata"] = self.embed_metadata.get()
        self.save_config()
        messagebox.showinfo("成功", "设置已保存!")
    
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def download_single(self):
        url = self.url_entry.get().strip()
        if not url or url == "粘贴 YouTube 链接...":
            messagebox.showwarning("警告", "请输入有效的 YouTube 链接!")
            return
        self.start_download([url])
    
    def download_batch(self):
        batch_file = self.batch_path.get()
        if not os.path.exists(batch_file):
            messagebox.showerror("错误", f"文件不存在: {batch_file}")
            return
        with open(batch_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            messagebox.showwarning("警告", "批量文件中没有找到有效链接!")
            return
        self.start_download(urls)
    
    def start_download(self, urls):
        if self.is_downloading:
            messagebox.showwarning("警告", "下载正在进行中!")
            return
        
        self.is_downloading = True
        self.stop_btn.config(state='normal')
        self.single_btn.config(state='disabled')
        self.batch_btn.config(state='disabled')
        
        self.download_thread = threading.Thread(target=self.run_download, args=(urls,), daemon=True)
        self.download_thread.start()
    
    def run_download(self, urls):
        try:
            self.log(f"开始下载 {len(urls)} 个视频...")
            
            ytdlp_exe = os.path.join(BASE_DIR, "yt-dlp.exe")
            output_dir = self.output_dir.get()
            os.makedirs(output_dir, exist_ok=True)
            
            for i, url in enumerate(urls, 1):
                if not self.is_downloading:
                    self.log("下载已停止。")
                    break
                
                self.log(f"\n[{i}/{len(urls)}] 正在处理: {url}")
                
                cmd = [
                    ytdlp_exe,
                    "-f", "bestaudio[ext=m4a]/bestaudio",
                    "--js-runtimes", "node",
                    "--extract-audio",
                    "--audio-format", "m4a",
                    "--cookies", COOKIES_FILE,
                    "--no-playlist",
                    "--no-check-certificate",
                    "--output", os.path.join(output_dir, "%(title)s.%(ext)s"),
                    "--ffmpeg-location", BASE_DIR,
                ]
                
                if self.download_thumbnail.get():
                    cmd.append("--write-thumbnail")
                if self.embed_metadata.get():
                    cmd.append("--add-metadata")
                
                cmd.append(url)
                
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    for line in process.stdout:
                        if not self.is_downloading:
                            process.terminate()
                            break
                        self.root.after(0, self.log, line.strip())
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.root.after(0, self.log, f"✅ 下载成功: {url}")
                    else:
                        self.root.after(0, self.log, f"❌ 下载失败: {url}")
                        
                except Exception as e:
                    self.root.after(0, self.log, f"错误: {str(e)}")
            
            self.root.after(0, self.log, "\n下载任务完成!")
            
        finally:
            self.root.after(0, self.on_download_complete)
    
    def stop_download(self):
        self.is_downloading = False
        self.log("正在停止下载...")
    
    def on_download_complete(self):
        self.is_downloading = False
        self.stop_btn.config(state='disabled')
        self.single_btn.config(state='normal')
        self.batch_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
