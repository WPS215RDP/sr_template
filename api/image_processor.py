import os
import re
import requests
from PIL import Image
from io import BytesIO

def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "", name)

def download_image(url, size):
    response = requests.get(url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    return img.resize(size, Image.LANCZOS)

def compress_image(img, save_path, max_kb=50):
    for quality in range(85, 5, -5):
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() / 1024 <= max_kb:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
            return save_path
    img.save(save_path, format="JPEG", quality=10, optimize=True)
    return save_path

def process_thumbnail(thumbnail_url, game_name, overlay_path="poster.png"):
    game_name = sanitize_filename(game_name)
    img = download_image(thumbnail_url, (584, 800))
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        img_rgba = img.convert("RGBA")
        img_rgba.paste(overlay, (0, 0), overlay)
        img = img_rgba.convert("RGB")
    except Exception:
        pass
    return compress_image(img, f"{game_name}_thumbnail_final.jpg")

def process_featured_image(featured_url, game_name):
    game_name = sanitize_filename(game_name)
    img = download_image(featured_url, (1280, 720))
    return compress_image(img, f"{game_name}_featured_final.jpg")
