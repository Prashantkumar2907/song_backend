import os
import pandas as pd
import yt_dlp
import shutil

DOWNLOAD_DIR = "downloads"

def ensure_dir():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

def download_song(song_name):
    ensure_dir()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'quiet': True,
        'cookiefile': 'youtube-cookies.txt', 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{song_name}"])
        return f"Downloaded: {song_name}"
    except Exception as e:
        print(f"Error downloading: {e}")
        return f"Failed: {song_name} | Error: {str(e)}"

def process_excel_and_download(file_path):
    ensure_dir()
    df = pd.read_excel(file_path)
    songs = df.iloc[:, 0].dropna().tolist()
    for song in songs:
        download_song(song)

def zip_downloads():
    zip_name = "downloads/songs"
    shutil.make_archive(zip_name, 'zip', DOWNLOAD_DIR)
    return f"{zip_name}.zip"
