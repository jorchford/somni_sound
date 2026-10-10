import os
import json
import urllib.request
import subprocess

json_path = "sounds.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Remove the two old mp3s
to_remove = ["brown_noise_sleep", "github_merged_free"]
# Remove from json
new_sounds = [s for s in data.get("sounds", []) if s.get("id") not in to_remove]
data["sounds"] = new_sounds

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Delete from disk and git
for file in ["noise/brown_noise_sleep.mp3", "noise/github_merged_free.mp3"]:
    if os.path.exists(file):
        subprocess.run(["git", "rm", "-f", file])

# 2. Add images to ALL mp3s in the directory (that don't have it, or just overwrite)
# Let's get all mp3 files from the JSON configuration so we know their IDs and names for fetching images
for sound in data.get("sounds", []):
    category = sound.get("category", "nature").lower()
    sid = sound.get("id")
    sname = sound.get("name")
    
    # Locate mp3
    # Try different paths, typically category/id.mp3 or category/name.mp3
    mp3_path = None
    for folder in os.listdir("."):
        if os.path.isdir(folder) and not folder.startswith("."):
            possible_path_1 = os.path.join(folder, f"{sid}.mp3")
            possible_path_2 = os.path.join(folder, f"{sname.replace(' ', '_').lower()}.mp3")
            url_path = sound.get("url", "").split("@master/")[-1]
            if os.path.exists(possible_path_1): mp3_path = possible_path_1; break
            if os.path.exists(possible_path_2): mp3_path = possible_path_2; break
            if url_path and os.path.exists(url_path): mp3_path = url_path; break
    
    if mp3_path and os.path.exists(mp3_path):
        img_path = os.path.join(os.path.dirname(mp3_path), f"{sid}.jpg")
        
        # Download image if it doesn't exist
        if not os.path.exists(img_path):
            print(f"Downloading image for {sname} -> {img_path}")
            img_url = f"https://picsum.photos/seed/{sid}/400/400"
            urllib.request.urlretrieve(img_url, img_path)
        
        # We will embed the image unconditionally for older ones
        # Actually we can just run ffmpeg on all to be sure
        tmp_mp3 = f"tmp_{sid}.mp3"
        print(f"Tagging {mp3_path} with {img_path}")
        
        cmd = [
            "ffmpeg", "-y", "-i", mp3_path, "-i", img_path,
            "-map", "0:0", "-map", "1:0", "-c", "copy",
            "-id3v2_version", "3",
            "-metadata", f"title={sname}",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            tmp_mp3
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(tmp_mp3):
            os.replace(tmp_mp3, mp3_path)
            # Update json with image if missing
            if "image" not in sound:
                sound["image"] = f"https://cdn.jsdelivr.net/gh/jorchford/somni_sound@master/{img_path}"
        else:
            if os.path.exists(tmp_mp3):
                os.remove(tmp_mp3)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Finished processing old mp3s and updating JSON.")
