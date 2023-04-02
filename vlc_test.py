import vlc

class VLCPlayer:
    def __init__(self):
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.media_list = self.instance.media_list_new()
        self.media_list_player = self.instance.media_list_player_new()

        self.media_list_player.set_media_player(self.player)
        self.media_list_player.set_media_list(self.media_list)
        self.current_index = -1

        self.events = self.player.event_manager()
        self.isLoopMedia = False
        self.isLoopPlaylist = False

    def add_event(self, eventType, func):
        self.events.event_attach(eventType, func)

    def isPlaying(self):
        return self.player.is_playing()

    def get_position(self):
        return self.player.get_position() * self.player.get_length() / 1000

    def set_position(self, n):
        # cur_pos = self.player.get_position() * self.player.get_length() / 1000
        cur_pos = 0
        new_pos = (cur_pos + n) * 1000 / self.player.get_length()
        self.player.set_position(new_pos)

    def get_count(self):
        return self.media_list.count()
    
    def clear(self):
        self.media_list.unlock()

        for _ in range(len(self.media_list)):
            self.media_list.remove_index(0)

        self.current_index = -1

    def loop_media(self):
        pass

    def unloop_media(self):
        pass

    def loop_playlist(self):
        self.media_list_player.set_playback_mode(vlc.PlaybackMode.loop)

    def unloop_playlist(self):
        self.media_list_player.set_playback_mode(vlc.PlaybackMode.default)

    def switch_loop_media(self):
        if self.isLoopMedia:
            self.unloop_media()
        else:
            self.loop_media()

        self.isLoopMedia = not self.isLoopMedia

    def switch_loop_playlist(self):
        if self.isLoopPlaylist:
            self.unloop_playlist()
        else:
            self.loop_playlist()

        self.isLoopPlaylist = not self.isLoopPlaylist



    def add_to_playlist(self, path):
        media = self.instance.media_new(path)
        self.media_list.add_media(media)

    def play(self):
        if self.current_index < 0:
            self.current_index = 0
            self.media_list_player.play_item_at_index(self.current_index)
        else:
            self.media_list_player.play()

    def pause(self):
        self.media_list_player.pause()

    def stop(self):
        self.media_list_player.stop()

    def next(self):
        if self.current_index >= len(self.media_list):
            self.stop()
            return
        
        self.current_index += 1
        self.media_list_player.play_item_at_index(self.current_index)

    def previous(self):
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.media_list) - 1
        self.media_list_player.play_item_at_index(self.current_index)

    def get_volume(self):
        return self.player.audio_get_volume()

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)

    def get_duration(self):
        return self.player.get_length() / 1000
