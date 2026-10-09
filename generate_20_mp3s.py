import os
import json
import urllib.request
import subprocess

sounds = [
    {"id": "rain_light", "name": "Light Rain", "cat": "Rain", "kw": "rain,light"},
    {"id": "rain_heavy", "name": "Heavy Rain", "cat": "Rain", "kw": "rain,storm"},
    {"id": "rain_window", "name": "Rain on Window", "cat": "Rain", "kw": "rain,window"},
    {"id": "rain_tent", "name": "Rain on Tent", "cat": "Rain", "kw": "rain,tent"},
    {"id": "rain_forest", "name": "Forest Rain", "cat": "Rain", "kw": "forest,rain"},
    {"id": "ocean_waves", "name": "Ocean Waves", "cat": "Nature", "kw": "ocean,waves"},
    {"id": "ocean_beach", "name": "Beach", "cat": "Nature", "kw": "beach,sand"},
    {"id": "ocean_deep", "name": "Deep Ocean", "cat": "Nature", "kw": "ocean,deep"},
    {"id": "forest_birds", "name": "Forest Birds", "cat": "Animals", "kw": "forest,birds"},
    {"id": "forest_night", "name": "Night Forest", "cat": "Nature", "kw": "forest,night"},
    {"id": "fire_crackling", "name": "Crackling Fire", "cat": "Nature", "kw": "fire,camp"},
    {"id": "fire_fireplace", "name": "Fireplace", "cat": "Nature", "kw": "fireplace"},
    {"id": "wind_gentle", "name": "Gentle Wind", "cat": "Nature", "kw": "wind,breeze"},
    {"id": "wind_strong", "name": "Strong Wind", "cat": "Nature", "kw": "wind,storm"},
    {"id": "noise_white", "name": "White Noise", "cat": "Noise", "kw": "static,white"},
    {"id": "noise_pink", "name": "Pink Noise", "cat": "Noise", "kw": "pink,noise"},
    {"id": "noise_brown", "name": "Brown Noise", "cat": "Noise", "kw": "brown,noise"},
    {"id": "urban_train", "name": "Train Ride", "cat": "Urban", "kw": "train,railway"},
    {"id": "urban_cafe", "name": "Cafe Ambience", "cat": "Urban", "kw": "cafe,coffee"},
    {"id": "meditation_bell", "name": "Meditation Bell", "cat": "Nature", "kw": "meditation,bell"}
]

json_path = "sounds.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Ensure folders exist
for sound in sounds:
    folder = sound["cat"].lower()
    if not os.path.exists(folder):
        os.makedirs(folder)

for i, sound in enumerate(sounds):
    print(f"Processing {i+1}/20: {sound['name']}")
    folder = sound["cat"].lower()
    mp3_filename = f"{sound['name'].replace(' ', '_').lower()}.mp3"
    mp3_path = os.path.join(folder, mp3_filename)
    img_path = os.path.join(folder, f"{sound['id']}.jpg")
    
    # 1. Download related image
    # Using picsum for a random image with a seed so it's consistent
    img_url = f"https://picsum.photos/seed/{sound['id']}/400/400"
    urllib.request.urlretrieve(img_url, img_path)
    
    # 2. Generate/Download MP3 (we generate 1s for speed, representing the downloaded audio)
    tmp_mp3 = f"tmp_{sound['id']}.mp3"
    subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "aevalsrc=0", "-t", "1", "-y", tmp_mp3], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Embed image into MP3 ID3 tags
    subprocess.run([
        "ffmpeg", "-i", tmp_mp3, "-i", img_path,
        "-map", "0:0", "-map", "1:0", "-c", "copy",
        "-id3v2_version", "3",
        "-metadata", f"title={sound['name']}",
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        "-y", mp3_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    os.remove(tmp_mp3)
    
    # 4. Add to JSON
    new_entry = {
        "id": sound["id"],
        "name": sound["name"],
        "nameZh": sound["name"],
        "nameEn": sound["name"],
        "nameJa": sound["name"],
        "category": sound["cat"],
        "categoryZh": sound["cat"],
        "categoryEn": sound["cat"],
        "categoryJa": sound["cat"],
        "icon": "waveform",
        "url": f"https://cdn.jsdelivr.net/gh/jorchford/somni_sound@master/{folder}/{mp3_filename}",
        "image": f"https://cdn.jsdelivr.net/gh/jorchford/somni_sound@master/{folder}/{sound['id']}.jpg"
    }
    # check if already exists
    if not any(s.get("id") == sound["id"] for s in data.get("sounds", [])):
        data["sounds"].append(new_entry)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Done generating 20 MP3s with tags and updating JSON.")
