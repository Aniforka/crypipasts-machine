import vlc

class Player():
    def __init__(self):
        self.instance = vlc.Instance()
        self.media = None
        self.mediaplayer = self.instance.media_player_new()

    def play(self):
        self.mediaplayer.play()
    
    def pause(self):
        self.mediaplayer.pause()

    def open_file(self, filename):
        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)
        self.play()

    def set_position(self, n):
        cur_pos = self.mediaplayer.get_position() * self.mediaplayer.get_length() / 1000
        new_pos = (cur_pos + n) * 1000 / self.mediaplayer.get_length()
        self.mediaplayer.set_position(new_pos)

    def set_volume(self, n):
        self.mediaplayer.audio_set_volume(n)

PLAYER = Player()

def play_file(path_to_file: str):
    PLAYER.open_file(path_to_file)

def pause_cur_audio():
    PLAYER.pause()
    
def resume_cur_audio():
    PLAYER.play()

def fastforward_cur_audio(seconds: int):
    PLAYER.set_position(seconds)

def volume_cur_audio(amount: int):
    PLAYER.set_volume(amount)