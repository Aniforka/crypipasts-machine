import json
import yt_dlp
from copy import deepcopy
from collections import namedtuple

def read_data(file):
    data = list()

    try:
        with open(file, 'r', encoding="utf-8") as file_input:
            data = json.load(file_input)
    except Exception: pass

    return data

def save_data(file, data):
    with open(file, 'w', encoding="utf-8") as file_output:
        json.dump(data, file_output, ensure_ascii=False, indent=4)


def pasrse_data(url, file):
    ydl = yt_dlp.YoutubeDL()

    with ydl:
        result = ydl.extract_info(url, download=False)

    videos = list()

    try:
        for video in result["entries"][0]["entries"]:
            videos.append({
                "image":video["thumbnails"][-2]["url"],
                "title":video["title"],
                "id":video["id"],
                "audio":video["requested_formats"][1]["url"]
            })
    except Exception as exp: print(exp)

    save_data(file, videos)

def prepare_data(file):
    data = read_data(file)

    Video = namedtuple("Video", "image title id url volume rewind_count play_status")
    videos = list()

    try:
        for video in data:
            videos.append(Video(
                video["image"],
                video["title"],
                video["id"],
                video["audio"],
                50,
                10,
                0
            ))
    except Exception as exp: print(exp)

    return deepcopy(videos)

#0 - не играет
#1 - играет
#2 - на паузе

#0 - не скачан
#1 - скачан

#result["entries"]["entries"]["id"] - ID
#result["entries"]["entries"]["title"] - название
#result["entries"]["entries"]["thumbnails"][-2]["url"] - превью
#result["entries"]["entries"]["formats"][0]["url"] - аудио