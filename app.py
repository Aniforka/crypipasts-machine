# -*- coding: utf-8 -*-

# Python VLC напиши зацикливание для отдельного аудио, а также ОБЯЗАТЕЛЬНО добавить функцию отключения зацикливания. ПИШИ ПО БИБЛИОТЕКЕ
import os
import vlc
import wget
import time
import requests
from pytube import YouTube
from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_socketio import SocketIO, emit
URL = "https://www.youtube.com/@TheKotBegemotWorld"
FILE = "channel_data.json"
AUDIO_FILE = "cripipats.mp3"

import patslib
import vlc_test

channel = patslib.YouTubeChannel(URL)

if 'yt_data.json' in os.listdir('.'):
    channel.deserialize_from_json('yt_data.json')

archive = patslib.Archive('archive_data.json')
archive.deserialize_from_json()

video_que = patslib.VideoQueue()
media_player = vlc_test.VLCPlayer()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

#Video = namedtuple("Video", "image title id url volume")
#videos = [Video("http://i0.kym-cdn.com/photos/images/newsfeed/000/538/345/7ad.png", "NANOMACHINES SON", "346HSR6U7", "abober", "10")]


@app.route('/', methods=["GET"])
def index():
    videos = channel.videos
    return render_template("index.html", videos=videos, queue_list=videos.values(), archive=archive.videos)

@app.route('/player', methods=["GET"])
def player_page():
    videos = channel.videos
    return render_template("player.html", queue=video_que.getArr(), active_video=video_que.get_active())

@app.route('/api')
def api_page():
    return render_template('api.html')

@app.route("/api/update_data", methods=["GET"])
def update_data():
    channel.fetch_videos()
    channel.serialize_to_json('yt_data.json')
    return jsonify({'status': 200})

@app.route('/api/set_channel', methods=["POST", "GET"])
def api_set_channel():
    target = request.args.get('target', URL)
    channel.url = target
    channel.videos.clear()
    return jsonify({'status': 200, 'channel': target})

@app.route('/api/queue_add_video', methods=["POST", "GET"])
def api_queue_add_video():
    target = request.args.get('target', '')
    if target == '':
        return jsonify({'status': 404, 'msg': 'Пустой аргумент target'})
    
    vid = patslib.Video.construct_from_url(target)
    video_que.push(vid)
    media_player.add_to_playlist(vid.video_endpoint)
    return jsonify({'status': 200, 'id': vid.video_id})

@app.route('/api/set_volume', methods=["POST", "GET"])
def api_set_volume():
    target = request.args.get('target', '')
    if target == '':
        return jsonify({'status': 404, 'msg': 'Пустой аргумент target'})
    
    value = max(0, min(int(target), 100))
    media_player.set_volume(value)

    return jsonify({'status': 200, 'volume': value})

@app.route('/api/get_volume', methods=["GET"])
def api_get_volume():
    value = media_player.get_volume()

    return jsonify({'status': 200, 'volume': value})

@app.route('/api/change_volume', methods=["POST", "GET"])
def api_change_volume():
    target = request.args.get('target', '')
    if target == '':
        return jsonify({'status': 404, 'msg': 'Пустой аргумент target'})
    
    value = media_player.get_volume()
    value = max(0, min(value + int(target), 100))
    media_player.set_volume(value)

    return jsonify({'status': 200, 'volume': value})

@app.route('/api/q_pop', methods=["POST", "GET"])
def api_q_pop():
    vid = video_que.pop()

    if vid is None:
        media_player.stop()
        return jsonify({'status': 404, 'msg': 'Видео в очереди отсутствует'})

    media_player.next()

    return jsonify({'status': 200})


@socketio.on('q_push')
def push_to_queue(data):
    channel[data['y_id']].make_working_endpoint()
    video_que.push(channel[data['y_id']])
    media_player.add_to_playlist(channel[data['y_id']].video_endpoint)
    emit('build_queue', {'status': 0, 'data': [vid.build_dict() for vid in video_que.getArr()]})

@socketio.on('request_queue')
def request_queue():
    emit('build_queue', {'status': 0, 'data': [vid.build_dict() for vid in video_que.getArr()]})

@socketio.on('request_player_state')
def request_player_state():
    vid_id = None if video_que.get_active() is None else video_que.get_active().video_id
    data = {
        'isPlaying': media_player.isPlaying(),
        'sound': media_player.get_volume(),
        'cur_pos': int(media_player.get_position()),
        'duration': int(media_player.get_duration()),
        'isLoopMedia': media_player.isLoopMedia,
        'isLoopPlaylist': media_player.isLoopPlaylist,
        'video_id': vid_id
    }
    print(data)
    emit('set_player_state', data)

@socketio.on('player_req_queue')
def player_req_queue():
    data = {
        'queue': [vid.build_dict() for vid in video_que.getArr()],
        'active': None if video_que.get_active() is None else video_que.get_active().build_dict()
    }
    print(media_player.current_index, len(media_player.media_list))
    emit('set_player_queue', data)

@socketio.on('q_pop')
def pop_from_queue():
    print(media_player.current_index, len(media_player.media_list))

    #archive.save_record()
    #archive.serialize_to_json()

    vid = video_que.pop()

    if vid is None:
        media_player.stop()
        return

    media_player.next()

    #media_player.resume()

@socketio.on('update_archive_record')
def arch_update(data):
    #archive.update_record(data["video_id"], data["cur_pos"], data["max_pos"])
    pass

@socketio.on('q_clear')
def pop_from_queue(event=None):
    video_que.clear()

    media_player.stop()

    media_player.clear()

@socketio.on('looping')
def switch_looping(data):
    loop_media = bool(data["loop_media"])
    loop_playlist = bool(data["loop_playlist"])
    print(loop_media, loop_playlist)

    if loop_media:
        media_player.loop_media()
        media_player.unloop_playlist()
    elif loop_playlist:
        media_player.unloop_media()
        media_player.loop_playlist()
    else:
        media_player.unloop_media()
        media_player.unloop_playlist()

    media_player.isLoopMedia = loop_media
    media_player.isLoopPlaylist = loop_playlist


def auto_next_event(event=None):
    print(media_player.current_index, len(media_player.media_list))

    #archive.save_record()

    if media_player.current_index + 1 < len(media_player.media_list):
        media_player.current_index += 1

    video_que.pop()

    #archive.serialize_to_json()

@socketio.on('player_volume')
def changeVolume(data):
    value = max(0, min(data['value'], 100))
    media_player.set_volume(value)

@socketio.on('player_position')
def changePosition(data):
    print(data)
    media_player.set_position(data['value'])

@socketio.on('player_playtoggle')
def playerToggle(data):
    isPlaying = bool(data['value'])
    if isPlaying:
        if media_player.current_index == -1:
            video_que.pop()

        media_player.play()
    else:
        media_player.pause()

@socketio.on('ALARM_PIZDEC')
def pizdec():
    print('GOT ALARM')
    global media_player
    global video_que
    global channel
    media_player.stop()
    media_player = None
    video_que = None
    channel = None

if __name__ == "__main__":
    media_player.add_event(vlc.EventType.MediaPlayerEndReached, auto_next_event)
    socketio.run(app, host='0.0.0.0', port=60000, allow_unsafe_werkzeug=True)