from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils.downloader import download_song, process_excel_and_download, zip_downloads
import os
import glob
import unicodedata
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"

class SongRequest(BaseModel):
    song_name: str

@app.get("/")
def home():
    return {"message": "Welcome to the Song Downloader API"}

@app.post("/download/")
async def download_single_song(request: SongRequest):
    msg = download_song(request.song_name)
    list_of_files = glob.glob(f"{DOWNLOAD_DIR}/*.mp3")

    if not list_of_files:
        return {"error": "Download failed or was blocked by YouTube."}

    latest_file = max(list_of_files, key=os.path.getctime)
    raw_filename = os.path.basename(latest_file)
    safe_filename = sanitize_filename(raw_filename)

    return FileResponse(
        latest_file,
        media_type='audio/mpeg',
        filename=safe_filename,  
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'}
    )

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    process_excel_and_download(temp_path)
    os.remove(temp_path)

    zip_path = zip_downloads()
    return FileResponse(zip_path, media_type='application/zip', filename="songs.zip")


def sanitize_filename(name):
    # Normalize and remove unsafe characters
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r'[^\w\s.-]', '', name)  # keep alphanumerics, dots, hyphens
    name = name.strip().replace(" ", "_")
    return name