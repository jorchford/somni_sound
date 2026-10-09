import urllib.request
import urllib.parse
import json
import os
import subprocess
import time

def fetch_wikimedia_audio(query, max_results=5):
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}+type:audio&utf8=&format=json&srlimit={max_results}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    results = []
    for item in data['query']['search']:
        title = item['title']
        results.append(title)
    return results

def get_file_url(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    pages = data['query']['pages']
    for page_id in pages:
        if 'imageinfo' in pages[page_id]:
            return pages[page_id]['imageinfo'][0]['url']
    return None

categories = ["rain", "ocean", "forest", "white noise"]
all_titles = []
for cat in categories:
    titles = fetch_wikimedia_audio(cat, 5)
    all_titles.extend(titles)

# Filter out non-audio just in case
all_titles = [t for t in all_titles if t.lower().endswith(('.ogg', '.wav', '.flac', '.mp3'))][:20]

print(f"Found {len(all_titles)} tracks")
for t in all_titles:
    print(t)
