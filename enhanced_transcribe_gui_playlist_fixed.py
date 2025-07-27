import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import tempfile
import shutil
import threading
import re
from pathlib import Path

class EnhancedTranscribeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Transcribe Anything - Single/Batch/Playlist Processing")
        self.root.geometry("700x750")  # Increased height for new elements

        # Variables
        self.folder_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()
        self.device_var = tk.StringVar(value="cuda")
        self.same_folder_var = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        self.is_processing = False
        self.mode_var = tk.StringVar(value="batch")  # Mode selection (batch, single, or playlist)
        self.file_path = tk.StringVar()  # Single file path
        self.youtube_url = tk.StringVar()  # YouTube URL
        self.playlist_url = tk.StringVar()  # NEW: YouTube Playlist URL

        # Supported file extensions
        self.supported_formats = {
            '.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.mpg', '.mpeg', '.m4v',
            '.3gp', '.ogv', '.ts', '.vob', '.asf', '.rm', '.rmvb', '.divx', '.xvid', '.f4v',
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.au'
        }

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Mode selection
        ttk.Label(main_frame, text="Mode Selection:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(5, 15))
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Three radio buttons for different modes
        ttk.Radiobutton(mode_frame, text="Batch Folder Processing",
            variable=self.mode_var, value="batch",
            command=self.toggle_mode).grid(row=0, column=0, padx=10, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Single File/YouTube URL",
            variable=self.mode_var, value="single",
            command=self.toggle_mode).grid(row=0, column=1, padx=10, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="YouTube Playlist",
            variable=self.mode_var, value="playlist",
            command=self.toggle_mode).grid(row=0, column=2, padx=10, sticky=tk.W)

        # BATCH MODE FRAME
        self.batch_frame = ttk.LabelFrame(main_frame, text="Batch Processing")
        self.batch_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(self.batch_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.batch_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(self.batch_frame, text="Browse", command=self.select_folder).grid(row=0, column=2, padx=5)

        # SINGLE MODE FRAME
        self.single_frame = ttk.LabelFrame(main_frame, text="Single File/URL Processing")
        self.single_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(self.single_frame, text="Single File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.single_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(self.single_frame, text="Browse", command=self.select_file).grid(row=0, column=2, padx=5)
        ttk.Label(self.single_frame, text="YouTube URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.single_frame, textvariable=self.youtube_url, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)

        # PLAYLIST MODE FRAME (NEW)
        self.playlist_frame = ttk.LabelFrame(main_frame, text="YouTube Playlist Processing")
        self.playlist_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(self.playlist_frame, text="Playlist URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.playlist_frame, textvariable=self.playlist_url, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Output options
        ttk.Label(main_frame, text="Output Options:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(15, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(output_frame, text="Same folder as input files",
            variable=self.same_folder_var, value=True,
            command=self.toggle_output_options).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(output_frame, text="Custom output folder",
            variable=self.same_folder_var, value=False,
            command=self.toggle_output_options).grid(row=1, column=0, sticky=tk.W)

        # Custom output folder selection
        self.output_frame = ttk.Frame(main_frame)
        self.output_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(self.output_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W)
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_folder_path, width=50)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.output_button = ttk.Button(self.output_frame, text="Browse", command=self.select_output_folder)
        self.output_button.grid(row=0, column=2, padx=5)
        self.output_frame.columnconfigure(1, weight=1)

        # Device selection
        ttk.Label(main_frame, text="Device:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=(15, 5))
        device_frame = ttk.Frame(main_frame)
        device_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        devices = [("CPU", "cpu"), ("CUDA (GPU)", "cuda"), ("Insane Mode", "insane"), ("MPS (Mac)", "mps")]
        for i, (text, value) in enumerate(devices):
            ttk.Radiobutton(device_frame, text=text, variable=self.device_var, value=value).grid(row=0, column=i, padx=10, sticky=tk.W)

        # Progress section
        ttk.Label(main_frame, text="Progress:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky=tk.W, pady=(15, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=12, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Log text area
        ttk.Label(main_frame, text="Log:", font=("Arial", 10, "bold")).grid(row=13, column=0, sticky=tk.W, pady=(15, 5))
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=14, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=12, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=15, column=0, columnspan=3, pady=20)

        self.start_button = ttk.Button(button_frame, text="Start Transcription",
            command=self.start_transcription, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_transcription, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)

        # Configure grid weights for main frame
        main_frame.rowconfigure(14, weight=1)

        # Initialize UI state
        self.toggle_output_options()
        self.toggle_mode()

    def get_youtube_title(self, url):
        """Fetch the YouTube video title, sanitized for filesystem use."""
        try:
            # Try to import yt-dlp first
            try:
                from yt_dlp import YoutubeDL
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title')
                    if title:
                        # Remove characters not allowed in filenames
                        title = re.sub(r'[\\/*?:"<>|]', "_", title)
                        # Limit length to avoid filesystem issues
                        if len(title) > 200:
                            title = title[:200]
                        return title
            except ImportError:
                self.log_message("yt-dlp not found, trying youtube-dl...")
                # Fallback to youtube-dl if yt-dlp is not available
                import youtube_dl
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title')
                    if title:
                        title = re.sub(r'[\\/*?:"<>|]', "_", title)
                        if len(title) > 200:
                            title = title[:200]
                        return title
        except Exception as e:
            self.log_message(f"Could not fetch YouTube title: {e}")
        return None

    def canonicalize_playlist_url(self, url):
        """Convert any YouTube playlist URL to canonical format"""
        try:
            # Extract playlist ID from various URL formats
            import re
            match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
            if match:
                playlist_id = match.group(1)
                return f"https://www.youtube.com/playlist?list={playlist_id}"
            else:
                return url  # Return original if no playlist ID found
        except Exception as e:
            self.log_message(f"Error canonicalizing playlist URL: {e}")
            return url

    def toggle_mode(self):
        """Show/hide frames based on selected mode"""
        mode = self.mode_var.get()
        if mode == "batch":
            self.batch_frame.grid()
            self.single_frame.grid_remove()
            self.playlist_frame.grid_remove()
        elif mode == "single":
            self.batch_frame.grid_remove()
            self.single_frame.grid()
            self.playlist_frame.grid_remove()
        elif mode == "playlist":
            self.batch_frame.grid_remove()
            self.single_frame.grid_remove()
            self.playlist_frame.grid()

    def toggle_output_options(self):
        """Enable/disable output folder selection based on radio button"""
        if self.same_folder_var.get():
            self.output_entry.config(state="disabled")
            self.output_button.config(state="disabled")
        else:
            self.output_entry.config(state="normal")
            self.output_button.config(state="normal")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"Input folder selected: {folder}")
            self.scan_files()

    def select_file(self):
        file_types = [("Media Files", [f"*{ext}" for ext in self.supported_formats]), ("All Files", "*.*")]
        file = filedialog.askopenfilename(filetypes=file_types)
        if file:
            self.file_path.set(file)
            self.log_message(f"Input file selected: {file}")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_path.set(folder)
            self.log_message(f"Output folder selected: {folder}")

    def scan_files(self):
        """Scan the selected folder for supported media files"""
        if not self.folder_path.get():
            return

        folder = Path(self.folder_path.get())
        if not folder.exists():
            self.log_message("ERROR: Selected folder does not exist!")
            return

        files = []
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                files.append(file_path)

        if files:
            self.log_message(f"Found {len(files)} supported media files:")
            for file_path in files[:10]:  # Show first 10 files
                self.log_message(f" - {file_path.name}")
            if len(files) > 10:
                self.log_message(f" ... and {len(files) - 10} more files")
        else:
            self.log_message("No supported media files found in the selected folder.")
            self.log_message(f"Supported formats: {', '.join(sorted(self.supported_formats))}")

    def log_message(self, message):
        """Add message to log with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def validate_youtube_url(self, url):
        """Validate if the given URL is a YouTube URL (video or playlist)"""
        youtube_patterns = [
            "youtube.com/watch",
            "youtu.be/",
            "youtube.com/embed/",
            "youtube.com/v/",
            "youtube.com/playlist",  # NEW: Added playlist support
            "list="  # NEW: Added list parameter support
        ]
        return any(pattern in url.lower() for pattern in youtube_patterns)

    def start_transcription(self):
        """Start the transcription process based on selected mode"""
        mode = self.mode_var.get()

        if mode == "batch":
            # BATCH MODE
            if not self.folder_path.get():
                messagebox.showerror("Error", "Please select an input folder first!")
                return
            if not self.same_folder_var.get() and not self.output_folder_path.get():
                messagebox.showerror("Error", "Please select an output folder!")
                return

            self.is_processing = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            thread = threading.Thread(target=self.process_files, daemon=True)
            thread.start()

        elif mode == "single":
            # SINGLE MODE
            if not self.file_path.get() and not self.youtube_url.get():
                messagebox.showerror("Error", "Please provide either a file or a YouTube URL!")
                return
            if not self.same_folder_var.get() and not self.output_folder_path.get():
                messagebox.showerror("Error", "Please select an output folder!")
                return

            self.is_processing = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            if self.youtube_url.get():
                if not self.validate_youtube_url(self.youtube_url.get()):
                    messagebox.showerror("Error", "Invalid YouTube URL! Please provide a valid YouTube URL.")
                    self.is_processing = False
                    self.start_button.config(state="normal")
                    self.stop_button.config(state="disabled")
                    return
                thread = threading.Thread(target=self.process_youtube_url, daemon=True)
                thread.start()
            else:
                thread = threading.Thread(target=self.process_single_file, daemon=True)
                thread.start()

        elif mode == "playlist":
            # PLAYLIST MODE (NEW)
            if not self.playlist_url.get():
                messagebox.showerror("Error", "Please provide a YouTube playlist URL!")
                return
            if not self.validate_youtube_url(self.playlist_url.get()):
                messagebox.showerror("Error", "Invalid YouTube playlist URL! Please provide a valid YouTube playlist URL.")
                return
            if not self.same_folder_var.get() and not self.output_folder_path.get():
                messagebox.showerror("Error", "Please select an output folder!")
                return

            self.is_processing = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            thread = threading.Thread(target=self.process_youtube_playlist, daemon=True)
            thread.start()

    def process_youtube_playlist(self):  # NEW METHOD
        """Process a YouTube playlist by transcribing each video"""
        try:
            from yt_dlp import YoutubeDL

            # Get and canonicalize the playlist URL
            playlist_url = self.playlist_url.get()
            playlist_url = self.canonicalize_playlist_url(playlist_url)

            self.progress_var.set(0)
            self.status_var.set("Fetching playlist info...")
            self.log_message(f"Fetching playlist: {playlist_url}")

            # Extract all video URLs from the playlist
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                entries = info.get('entries', [])

                # Format URLs properly
                video_urls = []
                for entry in entries:
                    if entry:  # Check if entry is not None
                        if 'url' in entry and entry['url'] and entry['url'].startswith('http'):
                            video_urls.append(entry['url'])
                        elif 'id' in entry and entry['id']:
                            video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                        elif 'webpage_url' in entry and entry['webpage_url']:
                            video_urls.append(entry['webpage_url'])

            total = len(video_urls)
            if total == 0:
                self.log_message("No videos found in the playlist.")
                self.log_message("This could be due to:")
                self.log_message("1. Private/unlisted videos in the playlist")
                self.log_message("2. Invalid playlist URL")
                self.log_message("3. Playlist access restrictions")
                return

            self.log_message(f"Found {total} videos in playlist.")

            successful = 0
            failed = 0

            for i, video_url in enumerate(video_urls):
                if not self.is_processing:
                    break

                # Update progress
                progress = (i / total) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing video {i+1}/{total}")

                self.log_message(f"\n=== Processing playlist video {i+1}/{total} ===")

                # Transcribe each video
                if self.transcribe_youtube_url(video_url):
                    successful += 1
                    self.log_message(f"✓ Successfully transcribed: {video_url}")
                else:
                    failed += 1
                    self.log_message(f"✗ Failed to transcribe: {video_url}")

            # Final results
            self.progress_var.set(100)
            self.status_var.set("Playlist Completed")
            self.log_message(f"\n=== PLAYLIST TRANSCRIPTION COMPLETED ===")
            self.log_message(f"Total videos processed: {successful + failed}")
            self.log_message(f"Successful: {successful}")
            self.log_message(f"Failed: {failed}")

        except Exception as e:
            self.log_message(f"ERROR processing playlist: {str(e)}")
            # Additional troubleshooting info
            self.log_message("Troubleshooting tips:")
            self.log_message("1. Ensure yt-dlp is installed: pip install yt-dlp")
            self.log_message("2. Try using the canonical playlist URL format")
            self.log_message("3. Check if the playlist is public and accessible")
        finally:
            self.is_processing = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def stop_transcription(self):
        """Stop the transcription process"""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Stopping...")
        self.log_message("Transcription stopped by user.")
    def process_files(self):
        """Process all media files in the selected folder"""
        try:
            folder = Path(self.folder_path.get())
            files = [f for f in folder.iterdir()
                   if f.is_file() and f.suffix.lower() in self.supported_formats]

            if not files:
                self.log_message("No supported files found to process.")
                return

            total_files = len(files)
            self.log_message(f"Starting batch transcription of {total_files} files...")

            successful = 0
            failed = 0

            for i, file_path in enumerate(files):
                if not self.is_processing:
                    break

                # Update progress
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing: {file_path.name}")

                self.log_message(f"\n=== Processing file {i+1}/{total_files}: {file_path.name} ===")

                try:
                    # Transcribe the file with custom naming
                    if self.transcribe_single_file(file_path):
                        successful += 1
                        self.log_message(f"✓ Successfully transcribed: {file_path.name}")
                    else:
                        failed += 1
                        self.log_message(f"✗ Failed to transcribe: {file_path.name}")
                except Exception as e:
                    failed += 1
                    self.log_message(f"✗ Error transcribing {file_path.name}: {str(e)}")

            # Final results
            self.progress_var.set(100)
            self.status_var.set("Completed")
            self.log_message(f"\n=== BATCH TRANSCRIPTION COMPLETED ===")
            self.log_message(f"Total files processed: {successful + failed}")
            self.log_message(f"Successful: {successful}")
            self.log_message(f"Failed: {failed}")

        except Exception as e:
            self.log_message(f"ERROR in batch processing: {str(e)}")
        finally:
            self.is_processing = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def process_single_file(self):
        """Process a single file"""
        try:
            file_path = Path(self.file_path.get())
            if not file_path.exists():
                self.log_message("ERROR: Selected file does not exist!")
                return

            self.progress_var.set(10)
            self.status_var.set(f"Processing: {file_path.name}")
            self.log_message(f"\n=== Processing file: {file_path.name} ===")

            if self.transcribe_single_file(file_path):
                self.log_message(f"✓ Successfully transcribed: {file_path.name}")
            else:
                self.log_message(f"✗ Failed to transcribe: {file_path.name}")

            self.progress_var.set(100)
            self.status_var.set("Completed")

        except Exception as e:
            self.log_message(f"ERROR processing file: {str(e)}")
        finally:
            self.is_processing = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def process_youtube_url(self):
        """Process a YouTube URL"""
        try:
            url = self.youtube_url.get()
            self.progress_var.set(10)
            self.status_var.set(f"Processing YouTube URL")
            self.log_message(f"\n=== Processing YouTube URL: {url} ===")

            if self.transcribe_youtube_url(url):
                self.log_message(f"✓ Successfully transcribed YouTube URL: {url}")
            else:
                self.log_message(f"✗ Failed to transcribe YouTube URL: {url}")

            self.progress_var.set(100)
            self.status_var.set("Completed")

        except Exception as e:
            self.log_message(f"ERROR processing YouTube URL: {str(e)}")
        finally:
            self.is_processing = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def extract_youtube_id(self, url):
        """Extract YouTube video ID from URL"""
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\?\/]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def transcribe_single_file(self, file_path):
        """Transcribe a single file with custom naming"""
        try:
            # Create temporary directory for this transcription
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Determine output directory
                if self.same_folder_var.get():
                    final_output_dir = file_path.parent
                else:
                    final_output_dir = Path(self.output_folder_path.get())

                final_output_dir.mkdir(parents=True, exist_ok=True)

                # Prepare the transcribe-anything command
                device_arg = self.device_var.get()

                # Build command
                cmd_parts = [
                    'pushd "F:\Python scripts\Transcribe anything"',
                    'call virtualEnv\Scripts\activate.bat',
                    f'transcribe-anything "{file_path}" --device {device_arg} --output_dir "{temp_path}"'
                ]

                bat_content = f"""
@echo off
{chr(10).join(cmd_parts)}
"""

                # Create and run temporary batch file
                temp_bat = temp_path / "transcribe_temp.bat"
                with open(temp_bat, "w", encoding="utf-8") as f:
                    f.write(bat_content)

                self.log_message(f"Running transcription command...")

                # Execute the command
                result = subprocess.run(['cmd.exe', '/c', str(temp_bat)],
                                     capture_output=True, text=True, timeout=1800)  # 30 minute timeout

                if result.returncode != 0:
                    self.log_message(f"Command failed with return code: {result.returncode}")
                    if result.stderr:
                        self.log_message(f"Error output: {result.stderr}")
                    return False

                # Move and rename output files
                return self.move_and_rename_outputs(temp_path, file_path, final_output_dir)

        except subprocess.TimeoutExpired:
            self.log_message(f"Transcription timed out after 30 minutes")
            return False
        except Exception as e:
            self.log_message(f"Error in transcribe_single_file: {str(e)}")
            return False

    def transcribe_youtube_url(self, url):
        """Transcribe a YouTube URL using video title for naming"""
        try:
            # Create temporary directory for this transcription
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Determine output directory
                if not self.same_folder_var.get():
                    final_output_dir = Path(self.output_folder_path.get())
                else:
                    # For YouTube URLs with "same folder", create a subfolder in user's documents
                    documents_dir = Path.home() / "Documents" / "Transcribe Anything"
                    final_output_dir = documents_dir

                final_output_dir.mkdir(parents=True, exist_ok=True)

                # Try to get the YouTube video title first
                self.log_message("Attempting to fetch YouTube video title...")
                title = self.get_youtube_title(url)

                if title:
                    base_name = title
                    self.log_message(f"Using video title: {title}")
                else:
                    # Fallback to video ID
                    video_id = self.extract_youtube_id(url)
                    base_name = video_id if video_id else "youtube_video"
                    self.log_message(f"Title not available, using video ID: {base_name}")

                # Create a file path object for naming purpose
                dummy_file_path = Path(f"{base_name}.mp4")

                # Prepare the transcribe-anything command
                device_arg = self.device_var.get()

                # Build command
                cmd_parts = [
                    'pushd "F:\Python scripts\Transcribe anything"',
                    'call virtualEnv\Scripts\activate.bat',
                    f'transcribe-anything "{url}" --device {device_arg} --output_dir "{temp_path}"'
                ]

                bat_content = f"""
@echo off
{chr(10).join(cmd_parts)}
"""

                # Create and run temporary batch file
                temp_bat = temp_path / "transcribe_temp.bat"
                with open(temp_bat, "w", encoding="utf-8") as f:
                    f.write(bat_content)

                self.log_message(f"Running transcription command for YouTube URL...")

                # Execute the command
                result = subprocess.run(['cmd.exe', '/c', str(temp_bat)],
                                     capture_output=True, text=True, timeout=1800)  # 30 minute timeout

                if result.returncode != 0:
                    self.log_message(f"Command failed with return code: {result.returncode}")
                    if result.stderr:
                        self.log_message(f"Error output: {result.stderr}")
                    return False

                # Move and rename output files
                return self.move_and_rename_outputs(temp_path, dummy_file_path, final_output_dir)

        except subprocess.TimeoutExpired:
            self.log_message(f"Transcription timed out after 30 minutes")
            return False
        except Exception as e:
            self.log_message(f"Error in transcribe_youtube_url: {str(e)}")
            return False

    def move_and_rename_outputs(self, temp_dir, original_file, output_dir):
        """Move and rename output files from temp directory to final location"""
        try:
            temp_path = Path(temp_dir)
            base_name = original_file.stem  # filename without extension

            # Expected output file extensions from transcribe-anything
            output_extensions = ['.txt', '.srt', '.vtt', '.json', '.tsv']

            # Extensions to delete after processing
            extensions_to_delete = ['.json', '.vtt', '.tsv']

            moved_files = 0

            # Look for output files in temp directory
            for temp_file in temp_path.iterdir():
                if temp_file.is_file():
                    # Check if it's one of the expected output files
                    if temp_file.name.startswith('out.') or temp_file.suffix in output_extensions:
                        # Determine the new filename
                        if temp_file.name.startswith('out.'):
                            # Replace 'out.' with the original filename
                            new_name = temp_file.name.replace('out.', f'{base_name}.')
                        else:
                            # For other files, use base name + extension
                            new_name = f"{base_name}{temp_file.suffix}"

                        final_path = output_dir / new_name

                        try:
                            # Copy the file to final location
                            shutil.copy2(temp_file, final_path)
                            self.log_message(f" → Created: {new_name}")
                            moved_files += 1
                        except Exception as e:
                            self.log_message(f" ✗ Failed to copy {temp_file.name}: {str(e)}")

            # Auto-delete unwanted extensions after all files are moved
            if moved_files > 0:
                self.log_message(f" Successfully created {moved_files} output files")
                self.delete_unwanted_extensions(output_dir, base_name, extensions_to_delete)
                return True
            else:
                self.log_message(f" No output files found in temp directory")
                return False

        except Exception as e:
            self.log_message(f"Error moving output files: {str(e)}")
            return False

    def delete_unwanted_extensions(self, output_dir, base_name, extensions_to_delete):
        """Delete files with unwanted extensions from the output directory"""
        try:
            deleted_files = 0
            for ext in extensions_to_delete:
                file_to_delete = output_dir / f"{base_name}{ext}"
                if file_to_delete.exists():
                    try:
                        file_to_delete.unlink()  # Delete the file
                        self.log_message(f" 🗑️ Deleted: {file_to_delete.name}")
                        deleted_files += 1
                    except Exception as e:
                        self.log_message(f" ✗ Failed to delete {file_to_delete.name}: {str(e)}")

            if deleted_files > 0:
                self.log_message(f" Cleaned up {deleted_files} unwanted files")
            else:
                self.log_message(f" No unwanted files to delete")

        except Exception as e:
            self.log_message(f"Error during cleanup: {str(e)}")

def main():
    root = tk.Tk()
    app = EnhancedTranscribeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
