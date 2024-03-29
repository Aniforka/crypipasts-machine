import youtube_dl
import yt_dlp
import scrapetube
import json
import vlc
from pprint import pprint
import os

class Video:
    title = ''
    duration=''
    date=''
    thumbnail_url = ''
    video_id = ''
    video_endpoint = None

    def __init__(self, scrapper_video, no_init=False) -> None:
        if no_init:
            return
        self.duration = scrapper_video['lengthText']['simpleText']
        self.date = scrapper_video['publishedTimeText']['simpleText']
        self.title = scrapper_video['title']['runs'][0]['text']
        self.thumbnail_url = scrapper_video['thumbnail']['thumbnails'][-1]['url']
        self.video_id = scrapper_video['videoId']
        self.video_endpoint = None

    def __repr__(self) -> str:
        return f'<Video({self.title})>'
    
    @staticmethod
    def construct_from_dict(video_id, data: dict):
        v = Video(None, True)
        v.duration = data['duration']
        v.date = data['date']
        v.title = data['title']
        v.video_id = video_id
        v.thumbnail_url = data['thumbnail']
        return v
    
    @staticmethod
    def construct_from_url(url):
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ex_data = ydl.extract_info(url, download=False)
            v = Video(None, True)
            v.title = ex_data['title']
            v.duration = str(ex_data['duration'])
            v.date = '1'
            v.thumbnail_url = ex_data["thumbnails"][-2]["url"]
            v.video_id = ex_data['id']
            v.video_endpoint = ex_data["requested_formats"][1]["url"]
        return v

    def make_working_endpoint(self):
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            # full_info = ydl.extract_info(f'https://www.youtube.com/watch?v={self.video_id}', download=False)
            # json.dump(full_info, open('debug_video.json', 'w', encoding='UTF-8'), indent=4)

            #self.video_endpoint = ydl.extract_info(f'https://www.youtube.com/watch?v={self.video_id}', download=False)["requested_formats"][1]["url"]
            pass
    
        ydl_opts = {
            'format': 'bestaudio',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={self.video_id}', download=False)
            self.video_endpoint = info['formats'][0]['url']

    def build_dict(self):
        return {'duration': self.duration,
                'date': self.date,
                'title': self.title,
                'thumbnail': self.thumbnail_url}

class YouTubeChannel:
    def __init__(self, url_to_channel) -> None:
        self.url = url_to_channel
        self.videos = dict()

    def fetch_videos(self):
        self.videos = dict()
        for ind, vid in enumerate(scrapetube.get_channel(channel_url=self.url)):
            new_vid = Video(vid)
            self.videos[new_vid.video_id] = new_vid
        
    def serialize_to_json(self, fname):
        f = open(fname, 'w', encoding='UTF-8')
        json.dump({vid.video_id: vid.build_dict() for vid in self.videos.values()}, f, indent=4, ensure_ascii=False)
        f.close()
        
    def deserialize_from_json(self, fname):
        f = open(fname, 'r', encoding='UTF-8')
        data = json.load(f)
        f.close()
        self.videos = {video_data[0]: Video.construct_from_dict(video_data[0], video_data[1]) for video_data in data.items()}
        
    def __getitem__(self, video_id: str) -> Video:
        return self.videos.get(video_id, None)

class MediaPlayer:
    def __init__(self) -> None:
        self.instance = vlc.Instance()
        self.media = None
        self.mediaplayer = self.instance.media_player_new()
        self.events = self.mediaplayer.event_manager()
    
    def add_event(self, eventType, func):
        self.events.event_attach(eventType, func)


    def playFromUrl(self, url):
        #self.__init__()

        if self.media is not None:
            pass

        self.media = self.instance.media_new(url)
        self.mediaplayer.set_media(self.media)

    def stopPlaying(self):
        self.mediaplayer.stop()

    def pause(self):
        self.mediaplayer.pause()
        while self.mediaplayer.is_playing():
            pass

    def resume(self):
        self.mediaplayer.play()
        while not self.mediaplayer.is_playing():
            pass

    def set_position(self, n):
        # cur_pos = self.mediaplayer.get_position() * self.mediaplayer.get_length() / 1000
        cur_pos = 0
        new_pos = (cur_pos + n) * 1000 / self.mediaplayer.get_length()
        self.mediaplayer.set_position(new_pos)

    def set_volume(self, n):
        self.mediaplayer.audio_set_volume(n)

    def isPlaying(self):
        return self.mediaplayer.is_playing()
    
    def get_volume(self):
        return self.mediaplayer.audio_get_volume()
    
    def get_position(self):
        return self.mediaplayer.get_position() * self.mediaplayer.get_length() / 1000
    
    def get_length(self):
        return self.mediaplayer.get_length() / 1000

class VideoQueue:
    def __init__(self) -> None:
        self.li = []
        self.active = None

    def get_active(self):
        return self.active
    
    def push(self, vid: Video):
        self.li.append(vid)
        print(self.li)

    def pop(self) -> Video:
        if len(self.li) == 0:
            self.active = None
            return None
        self.active = self.li.pop(0)
        return self.get_active()
    
    def getArr(self) -> list[Video]:
        return self.li
    
    def clear(self) -> None:
        self.li.clear()
        self.active = None

class ArchiveRecord:
    FINISHED_CONDITION = 0.9

    @staticmethod
    def construct_record(video_id, cur_duration, max_duration):
        FINISHED_CONDITION = 0.9
        record = dict()

        if video_id is None:
            return None
        
        if max_duration == 0:
            return None

        if cur_duration / max_duration > FINISHED_CONDITION:
            status = 'FINISHED'
        else:
            status = 'STARTED'

        record = {
            video_id : {
                'status': status,
                'duration': cur_duration,
                'percent': round(cur_duration / max_duration)
            }
        }

        return record


class Archive:
    def __init__(self, fname) -> None:
        self.fname = fname
        self.videos = dict()
        self.record = None

    def serialize_to_json(self):
        f = open(self.fname, 'w', encoding='UTF-8')
        json.dump(self.videos, f, indent=4, ensure_ascii=False)
        f.close()
        
    def deserialize_from_json(self):
        if self.fname in os.listdir('.'):
            f = open(self.fname, 'r', encoding='UTF-8')
            data = json.load(f)
            f.close()
            self.videos = data

    def update_record(self, video_id, cur_duration, max_duration):
        self.record = ArchiveRecord.construct_record(video_id, cur_duration, max_duration)

    def save_record(self):
        if self.record is not None:
            self.videos.update(self.record)

    def __getitem__(self, video_id: str) -> dict:
        return self.videos.get(video_id, None)
    
    def __del__(self):
        if self.record is not None:
            self.save_record()

        self.serialize_to_json()

    # <div class="progress-bar bg-danger" role="progressbar" style="width: {{ archive[video.video_id]['percent'] }}%" aria-valuenow="{{ archive[video.video_id]['percent'] }}" aria-valuemin="0" aria-valuemax="100"></div>
