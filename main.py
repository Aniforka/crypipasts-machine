from audio import *
from get_info_channel import *

import os
import wget
import requests
from pytube import YouTube
from flask import Flask, render_template, url_for, redirect, request

URL = "https://www.youtube.com/@TheKotBegemotWorld"
FILE = "channel_data.json"
AUDIO_FILE = "cripipats.mp3"

app = Flask(__name__)

#Video = namedtuple("Video", "image title id url volume")
#videos = [Video("http://i0.kym-cdn.com/photos/images/newsfeed/000/538/345/7ad.png", "NANOMACHINES SON", "346HSR6U7", "abober", "10")]

videos = list()

@app.route('/', methods=["GET"])
def main():
    global videos

    videos = prepare_data(FILE)

    return render_template("index.html", videos=videos)

@app.route("/update_data", methods=["POST"])
def update_data():
    pasrse_data(URL, FILE)

    return redirect(url_for("main"))

@app.route("/<video_id>", methods=["GET"])
def video(video_id):
    vid = None

    for i in range(len(videos)):
        if videos[i].id == video_id:
            print("aaaa")
            vid = videos[i]
            '''response = requests.get(videos[i].url)
            print(response)

            with open(AUDIO_FILE, 'wb') as f:
                f.write(response.content)'''
            try: os.remove(AUDIO_FILE)
            except Exception: pass
            #wget.download(url=videos[i].url, out=AUDIO_FILE)
            video_link = "https://www.youtube.com/watch?v=" + videos[i].id
            print(video_link)
            video = YouTube(video_link)
            audio = video.streams.filter(only_audio=True, file_extension='mp4').first()
            audio.download(filename=AUDIO_FILE)

            print(videos[i].volume)

            break

    return render_template("video.html", video=vid)

@app.route("/change_volume", methods=["POST"])
def change_volume():
    volume = request.form["volume"]
    video_id = request.form["video_id"]

    for i in range(len(videos)):
        if videos[i].id == video_id:
            videos[i] = videos[i]._replace(volume=int(volume))
            break
    print(volume)
    volume_cur_audio(int(volume))

    return redirect(url_for("video", video_id=video_id))

@app.route("/play", methods=["POST"])
def play():
    video_id = request.form["video_id"]

    for i in range(len(videos)):
        if videos[i].id == video_id:
            if videos[i].play_status == 0:
                play_file(AUDIO_FILE)
                print(PLAYER)
                print("PLAY SUKA!")
                videos[i] = videos[i]._replace(play_status=1)
                volume_cur_audio(videos[i].volume)
            elif videos[i].play_status == 2:
                resume_cur_audio()
                videos[i] = videos[i]._replace(play_status=1)
                volume_cur_audio(videos[i].volume)
            break

    return redirect(url_for("video", video_id=video_id))

@app.route("/pause", methods=["POST"])
def pause():
    video_id = request.form["video_id"]

    for i in range(len(videos)):
        if videos[i].id == video_id:
            if videos[i].play_status == 1:
                pause_cur_audio()
                videos[i] = videos[i]._replace(play_status=2)
        break

    return redirect(url_for("video", video_id=video_id))

@app.route("/rewind", methods=["POST"])
def rewind():
    video_id = request.form["video_id"]

    fastforward_cur_audio(-10)

    return redirect(url_for("video", video_id=video_id))

@app.route("/fast_forward", methods=["POST"])
def fast_forward():
    video_id = request.form["video_id"]

    fastforward_cur_audio(10)

    return redirect(url_for("video", video_id=video_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=60000)