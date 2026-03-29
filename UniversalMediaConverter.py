import os
import threading
import shutil
import requests
import yt_dlp
import customtkinter as ctk
from PIL import Image, ImageOps
from io import BytesIO

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class UniversalConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        script_dir = os.path.dirname(__file__)
        icon_path = os.path.join(script_dir, "icon.ico")

        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except ctk.tkinter.TclError as e:
                print(f"WARNING: Couldn't set window icon. Error: {e}")

        self.title("Universal Media Converter (Beta v2.0)")
        self.geometry("800x540")
        self.video_info = {}

        self.save_path = os.path.join(os.path.expanduser("~"), "Documents", "Universal Media Converter")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.url_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Paste Your Media URL Here", justify="center")
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.analyze_button = ctk.CTkButton(self.top_frame, text="Analyze The URL", command=self.start_analysis_thread)
        self.analyze_button.grid(row=0, column=1, padx=10, pady=10)

        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.thumbnail_label = ctk.CTkLabel(self.info_frame, text="", width=160, height=90)
        self.thumbnail_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        self.title_label = ctk.CTkLabel(self.info_frame, text="The Media Title Will Be Shown Here", anchor="w", wraplength=650)
        self.title_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.duration_label = ctk.CTkLabel(self.info_frame, text="The Media Duration Will Be Shown Here", text_color="gray", anchor="w", wraplength=650)
        self.duration_label.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.path_button = ctk.CTkButton(self.info_frame, text="Change Output Path", command=self.select_save_path)
        self.path_button.grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.path_label = ctk.CTkLabel(self.info_frame, text=f"Output Path: {self.save_path}", text_color="gray", anchor="w")
        self.path_label.grid(row=2, column=1, padx=10, sticky="ew")

        placeholder_path = os.path.join(script_dir, "placeholder.png")
        if os.path.exists(placeholder_path):
            placeholder_img = Image.open(placeholder_path)
            placeholder_img = ImageOps.pad(placeholder_img, (160, 90), color=(30, 30, 30))
            self.placeholder_ctk_img = ctk.CTkImage(light_image=placeholder_img, dark_image=placeholder_img, size=(160, 90))
        else:
            self.placeholder_ctk_img = None

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1, uniform="equal_frames")
        self.main_frame.grid_columnconfigure(1, weight=1, uniform="equal_frames")
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.video_download_frame = ctk.CTkFrame(self.main_frame)
        self.video_download_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_download_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.video_download_frame, text="Video Converter", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)

        self.video_formats_menu = ctk.CTkOptionMenu(self.video_download_frame, values=["Video Download Options"], state="disabled")
        self.video_formats_menu.grid(row=1, column=0, padx=10, pady=20, sticky="ew")
        self.download_video_button = ctk.CTkButton(self.video_download_frame, text="Download Video", state="disabled", command=lambda: self.start_download_thread('video', 'mp4'))
        self.download_video_button.grid(row=2, column=0, padx=10, pady=20)

        self.audio_download_frame = ctk.CTkFrame(self.main_frame)
        self.audio_download_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.audio_download_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.audio_download_frame, text="Audio Converter", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)

        self.audio_formats = {
            "WAV": "wav",
            "FLAC": "flac",
            "MP3": "mp3",
            "M4A (AAC)": "m4a",
            "OPUS": "opus",
            "OGG (Vorbis)": "vorbis"
        }

        self.audio_format_menu = ctk.CTkOptionMenu(self.audio_download_frame, values=["Audio Download Options"], state="disabled")
        self.audio_format_menu.set("Audio Download Options")
        self.audio_format_menu.grid(row=1, column=0, padx=10, pady=20, sticky="ew")
        self.download_audio_button = ctk.CTkButton(self.audio_download_frame, text="Download Audio", state="disabled", command=lambda: self.start_download_thread("audio", self.audio_formats[self.audio_format_menu.get()]))
        self.download_audio_button.grid(row=2, column=0, padx=10, pady=20)

        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Paste your Media URL and press the \"Analyze The URL\" button.", justify="center")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.format_map = {}

        self.check_dependencies()
        self.set_ui_state("initial")

    def set_ui_state(self, state):
        if state == "initial":
            self.url_entry.configure(state="normal")
            self.analyze_button.configure(state="normal")
            self.path_button.configure(state="normal")
            self.video_formats_menu.configure(state="disabled", values=["Waiting for \"Analyze The URL\" button..."])
            self.download_video_button.configure(state="disabled")
            self.audio_format_menu.configure(state="disabled", values=["Audio Download Options"])
            self.audio_format_menu.set("Audio Download Options")
            self.download_audio_button.configure(state="disabled")
            self.title_label.configure(text="The Media Title Will Be Shown Here")
            self.duration_label.configure(text="The Media Duration Will Be Shown Here")
            self.thumbnail_label.configure(image=self.placeholder_ctk_img)
            self.thumbnail_label.image = self.placeholder_ctk_img
            self.progress_bar.set(0)
            self.progress_bar.configure(mode="determinate")
            self.update_status("Paste your Media URL and press the \"Analyze The URL\" button.", "white")

        elif state == "analyzing":
            self.url_entry.configure(state="disabled")
            self.analyze_button.configure(state="disabled")
            self.path_button.configure(state="disabled")
            self.video_formats_menu.configure(state="disabled", values=["Analyzing the URL..."])
            self.download_video_button.configure(state="disabled")
            self.audio_format_menu.configure(state="disabled", values=["Audio Download Options"])
            self.download_audio_button.configure(state="disabled")
            self.title_label.configure(text="Getting Media Data...")
            self.duration_label.configure(text="Getting Media Data...")
            self.progress_bar.set(0)
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.update_status("Analyzing the URL...", "yellow")

        elif state == "analysis_complete":
            self.url_entry.configure(state="normal")
            self.analyze_button.configure(state="normal")
            self.path_button.configure(state="normal")
            self.video_formats_menu.configure(state="normal")
            self.download_video_button.configure(state="normal")
            self.audio_format_menu.configure(state="normal", values=list(self.audio_formats.keys()))
            self.audio_format_menu.set(list(self.audio_formats.keys())[0])
            self.download_audio_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")

        elif state == "downloading":
            self.url_entry.configure(state="disabled")
            self.analyze_button.configure(state="disabled")
            self.path_button.configure(state="disabled")
            self.video_formats_menu.configure(state="disabled")
            self.download_video_button.configure(state="disabled")
            self.audio_format_menu.configure(state="disabled")
            self.download_audio_button.configure(state="disabled")
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
            self.update_status("Preparing download...", "yellow")

    def check_dependencies(self):
        ffmpeg_ok = shutil.which("ffmpeg")
        if not ffmpeg_ok:
            self.update_status("ERROR: Couldn't find \"FFmpeg\"! Please configure your PATH settings.", "red")
            self.analyze_button.configure(state="disabled")
            self.url_entry.configure(state="disabled")

    def update_status(self, message, color="white", progress=None):
        self.status_label.configure(text=message, text_color=color)
        if progress is not None:
            self.progress_bar.set(progress)
        self.update_idletasks()

    def select_save_path(self):
        path = ctk.filedialog.askdirectory(initialdir=self.save_path)
        if path:
            self.save_path = path
            self.path_label.configure(text=f"Current Output Path: {self.save_path}")

    def start_analysis_thread(self):
        url = self.url_entry.get().strip()
        self.set_ui_state("analyzing")
        thread = threading.Thread(target=self.analyze_url, args=(url,))
        thread.daemon = True
        thread.start()

    def analyze_url(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
            self.after(0, self.update_ui_after_analysis)
        except Exception as e:
            self.after(0, lambda: self.set_ui_state("initial"))
            self.after(0, lambda: self.update_status("ERROR: Failed to analyze the URL. Unsupported site or invalid link.", "red"))
            print(f"Analysis Error: {e}")

    def format_duration(self, duration):
        if not duration:
            return "Unknown Duration"
        try:
            total_seconds = int(float(duration))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "Unknown Duration"

    def update_ui_after_analysis(self):
        self.title_label.configure(text=self.video_info.get("title", "Unknown Title"))

        duration = self.video_info.get("duration")
        self.duration_label.configure(text="Duration: " + self.format_duration(duration))

        thumb_url = self.video_info.get("thumbnail")
        if thumb_url:
            threading.Thread(target=self.load_thumbnail, args=(thumb_url,), daemon=True).start()
        else:
            self.thumbnail_label.configure(image=self.placeholder_ctk_img)

        best_formats_by_res_fps = {}

        for f in self.video_info.get('formats', []):
            vcodec = f.get('vcodec', 'none')
            if vcodec != 'none':
                if f.get('ext') == 'm3u8' or 'm3u8' in f.get('url', '') or 'hls' in f.get('format_note', '').lower():
                    continue

                res = f.get('resolution') or f"{f.get('width', '?')}x{f.get('height', '?')}"
                if res == "?x?":
                    res = "Unknown Res"

                fps_val = f.get('fps')
                fps_display = f"{int(fps_val)}FPS" if fps_val else "Unknown FPS"

                display_key = f"{res} - {fps_display} - {f.get('ext', 'mp4').upper()}"
                current_bitrate = f.get('tbr') or f.get('vbr') or 0

                if display_key not in best_formats_by_res_fps or current_bitrate > best_formats_by_res_fps[display_key][0]:
                    best_formats_by_res_fps[display_key] = (current_bitrate, f)

        video_formats_display = []
        self.format_map = {}

        for display_text, (bitrate, format_obj) in best_formats_by_res_fps.items():
            format_id = format_obj.get("format_id")
            if format_id:
                if format_obj.get("acodec", "none") == "none":
                    format_id += "+bestaudio/best"
                video_formats_display.append(display_text)
                self.format_map[display_text] = format_id

        if video_formats_display:
            self.video_formats_menu.configure(values=video_formats_display, state="normal")
            self.video_formats_menu.set(video_formats_display[-1])
            self.download_video_button.configure(state="normal")
        else:
            self.video_formats_menu.configure(values=["No Video Available (Audio Only)"], state="disabled")
            self.download_video_button.configure(state="disabled")

        self.set_ui_state("analysis_complete")
        self.update_status("Analysis completed. Please select a download option.", progress=1)

    def load_thumbnail(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = ImageOps.pad(img, (160, 90), color=(30, 30, 30))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 90))
            self.after(0, lambda: self.thumbnail_label.configure(image=ctk_img))
            self.after(0, lambda: setattr(self.thumbnail_label, 'image', ctk_img))
        except Exception as e:
            if self.placeholder_ctk_img:
                self.after(0, lambda: self.thumbnail_label.configure(image=self.placeholder_ctk_img))
            print(f"Thumbnail Error: {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                downloaded = d.get('downloaded_bytes', 0)
                percent = downloaded / total
                speed = d.get('speed', 0)

                speed_str = "0 B/s"
                if speed:
                    speed_mb = speed / (1024 * 1024)
                    speed_str = f"{speed_mb:.1f} MB/s"

                self.after(0, lambda: self.progress_bar.set(percent))
                self.after(0, lambda: self.update_status(f"Downloading... {percent*100:.1f}% ({speed_str})", "yellow"))

        elif d['status'] == 'finished':
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.update_status("Download complete. Finalizing/Converting file...", "yellow"))

    def start_download_thread(self, download_type, target_format):
        self.set_ui_state("downloading")
        thread = threading.Thread(target=self.download_and_convert, args=(download_type, target_format))
        thread.daemon = True
        thread.start()

    def download_and_convert(self, download_type, target_format):
        url = self.url_entry.get().strip()

        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'windowsfilenames': True,
            'progress_hooks': [self.progress_hook],
            'concurrent_fragment_downloads': 5,
            'quiet': True,
            'no_warnings': True
        }

        if download_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': target_format,
                'preferredquality': '320',
            }]
        elif download_type == 'video':
            selected_format_code = self.format_map.get(self.video_formats_menu.get())
            ydl_opts['format'] = selected_format_code
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['postprocessor_args'] = ['-c:a', 'aac', '-b:a', '320k']

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                if download_type == 'audio':
                    base, _ = os.path.splitext(downloaded_file)
                    downloaded_file = f"{base}.{target_format}"

            self.after(0, lambda: self.update_status(f"Success! Saved as: {os.path.basename(downloaded_file)}", "lightgreen", 1.0))

        except Exception as e:
            print(f"Download Error: {e}")
            self.after(0, lambda: self.update_status("ERROR: An issue occurred during download.", "red"))

        finally:
            self.after(0, lambda: self.set_ui_state("analysis_complete"))

if __name__ == "__main__":
    app = UniversalConverterApp()
    app.mainloop()