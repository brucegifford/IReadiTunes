# -*- coding: utf-8 -*-
"""
Tool to get any information about iTunes tracks and playlists quickly and easily.
Mickael <mickael2054dev@gmail.com>
MIT License
"""

import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse
import urllib.request
from datetime import datetime


def lib_init():
    """Initilize the library, must be called at the very beginning"""
    lib_class = Library()
    return lib_class


class Library(object):

    def __init__(self):
        """Constructor"""
        self.lib = 0
        self.playlists = []
        self.playlist_by_persistent_id = {}
        self.track_map = {}
        self.song_list = []
        self.movie_list = []
        self.podcast_list = []
        self.tvshow_list = []
        self.audiobook_list = []

    def parse(self, path_to_XML_file):
        """Reads xml file and generate tracks list"""
        tree = ET.parse(path_to_XML_file)
        self.lib = tree.getroot()
        self.read_tracks()
        self.read_playlists()
        self.generate_playlist_dislay_paths()

    def get_plist_attr_value(self, attr_name, attr):
        if attr.tag == 'string':
            return attr.text
        elif attr.tag == 'true':
            return True
        elif attr.tag == 'false':
            return False
        elif attr.tag == 'integer':
            if attr.text is not None:
                return int(attr.text)
            else:
                return None
        elif attr.tag == 'date':
            datetime_object = datetime.strptime(attr.text, "%Y-%m-%dT%H:%M:%SZ")
            return datetime_object
        else:
            print("What to do for plist attribute '%s' of type '%s', value '%s'" % (attr_name, attr.tag, str(attr.text)))
            return attr.text

    def read_playlists(self):
        """Generate tracks list"""
        attribut_name_list = [ "Name", "Description", "Master", "Playlist ID", "Playlist Persistent ID", "Visible",
                               "All Items", "Distinguished Kind", "Music", 'Movies', 'TV Shows', 'Podcasts',
                               'Audiobooks', 'Folder', 'Parent Persistent ID', 'Purchased Music' ]

        # Docs are here??? https://developer.apple.com/documentation/ituneslibrary/itlibdistinguishedplaylistkind
        ITLibDistinguishedPlaylistKindNone = 0
        ITLibDistinguishedPlaylistKindMovies = 1
        ITLibDistinguishedPlaylistKindTVShows = 2
        ITLibDistinguishedPlaylistKindMusic = 3
        ITLibDistinguishedPlaylistKindAudioBooks = 4
        ITLibDistinguishedPlaylistKindRingtones = 5

        ITLibDistinguishedPlaylistKindPodcasts = 7

        ITLibDistinguishedPlaylistKindVoiceMemos = 14

        ITLibDistinguishedPlaylistKindPurchases = 16

        ITLibDistinguishedPlaylistKindiTunesU = 26

        ITLibDistinguishedPlaylistKind90sMusic = 42
        ITLibDistinguishedPlaylistKindMyTopRated = 43
        ITLibDistinguishedPlaylistKindTop25MostPlayed = 44
        ITLibDistinguishedPlaylistKindRecentlyPlayed = 45
        ITLibDistinguishedPlaylistKindRecentlyAdded = 46
        ITLibDistinguishedPlaylistKindMusicVideos = 47
        ITLibDistinguishedPlaylistKindClassicalMusic = 48
        ITLibDistinguishedPlaylistKindLibraryMusicVideos = 49

        ITLibDistinguishedPlaylistKindHomeVideos = 50
        ITLibDistinguishedPlaylistKindApplications = 51
        ITLibDistinguishedPlaylistKindLovedSongs = 52
        ITLibDistinguishedPlaylistKindMusicShowsAndMovies = 53

        distinguishedKindMap = {
            "None": ITLibDistinguishedPlaylistKindNone,
            "Movies": ITLibDistinguishedPlaylistKindMovies,
            "TVShows": ITLibDistinguishedPlaylistKindTVShows,
            "Music": ITLibDistinguishedPlaylistKindMusic,
            "AudioBooks": ITLibDistinguishedPlaylistKindAudioBooks,
            "Ringtones": ITLibDistinguishedPlaylistKindRingtones,
            "Podcasts": ITLibDistinguishedPlaylistKindPodcasts,
            "VoiceMemos": ITLibDistinguishedPlaylistKindVoiceMemos,
            "Purchases": ITLibDistinguishedPlaylistKindPurchases,
            "iTunesU": ITLibDistinguishedPlaylistKindiTunesU,
            "90sMusic": ITLibDistinguishedPlaylistKind90sMusic,
            "MyTopRated": ITLibDistinguishedPlaylistKindMyTopRated,
            "Top25MostPlayed": ITLibDistinguishedPlaylistKindTop25MostPlayed,
            "RecentlyPlayed": ITLibDistinguishedPlaylistKindRecentlyPlayed,
            "RecentlyAdded": ITLibDistinguishedPlaylistKindRecentlyAdded,
            "MusicVideos": ITLibDistinguishedPlaylistKindMusicVideos,
            "ClassicalMusic": ITLibDistinguishedPlaylistKindClassicalMusic,
            "LibraryMusicVideos": ITLibDistinguishedPlaylistKindLibraryMusicVideos,
            "HomeVideos": ITLibDistinguishedPlaylistKindHomeVideos,
            "Applications": ITLibDistinguishedPlaylistKindApplications,
            "LovedSongs": ITLibDistinguishedPlaylistKindLovedSongs,
            "MusicShowsAndMovies": ITLibDistinguishedPlaylistKindMusicShowsAndMovies
        }

        # create an inverse map
        distinguishedKindMapInverse = {}
        for k, v in distinguishedKindMap.items():
            distinguishedKindMapInverse[v] = k

        class PlayList:
            def __init__(self, name, description, master, playlist_id, playlist_persistent_id, visible, all_items,
                         distinguished_kind, music, movies, tv_shows, podcasts, audiobooks, folder,
                         parent_persistent_id, purchased_music):
                self.extra_attributes = {}
                self.tracks = []
                self.name = name
                self.description = description
                self.master = master
                self.playlist_id = playlist_id
                self.playlist_persistent_id = playlist_persistent_id
                self.visible = visible
                self.all_items = all_items
                self.distinguished_kind = distinguished_kind
                self.music = music
                self.movies = movies
                self.tv_shows = tv_shows
                self.podcasts = podcasts
                self.audiobooks = audiobooks
                self.folder = folder
                self.parent_persistent_id = parent_persistent_id
                self.purchased_music = purchased_music

            def set_track_indexes(self, library, track_list):
                for track_id in track_list:
                    self.tracks.append( (track_id, library.track_map[track_id] ))

            def add_extra_attribute(self, key, value):
                self.extra_attributes[key] = value

            def add_extra_attributes(self, attributes):
                for key, value in attributes.items():
                    self.extra_attributes[key] = value

            def get_as_dict(self, add_distingished_kind_label = False):
                playlist_dict = {}

                def add_non_None_attribute(key, value):
                    if value is not None:
                        playlist_dict[key] = value

                add_non_None_attribute('name', self.name)
                add_non_None_attribute('description', self.description)
                add_non_None_attribute('master', self.master)
                add_non_None_attribute('playlist_id', self.playlist_id)
                add_non_None_attribute('playlist_persistent_id', self.playlist_persistent_id)
                add_non_None_attribute('visible', self.visible)
                add_non_None_attribute('all_items', self.all_items)
                add_non_None_attribute('distinguished_kind', self.distinguished_kind)
                add_non_None_attribute('music', self.music)
                add_non_None_attribute('movies', self.movies)
                add_non_None_attribute('tv_shows', self.tv_shows)
                add_non_None_attribute('podcasts', self.podcasts)
                add_non_None_attribute('audiobooks', self.audiobooks)
                add_non_None_attribute('folder', self.folder)
                add_non_None_attribute('parent_persistent_id', self.parent_persistent_id)
                add_non_None_attribute('purchased_music', self.purchased_music)
                add_non_None_attribute('display_path', self.display_path)

                #add the individual tracks
                if self.tracks:
                    playlist_dict['tracks'] = []
                    for id, track in self.tracks:
                        track_dict = track.get_as_dict()
                        playlist_dict['tracks'].append(track_dict)
                """ this code puts just the track file name
                if self.tracks:
                    playlist_dict['tracks'] = []
                    for id, track in self.tracks:
                        if track.location:
                            playlist_dict['tracks'].append(track.location)
                """


                for key, value in self.extra_attributes:
                    playlist_dict[key] = value

                # if they want a text representation, look it up
                if add_distingished_kind_label and 'distinguished_kind' in playlist_dict:
                    if playlist_dict['distinguished_kind'] in distinguishedKindMapInverse:
                        playlist_dict['distinguished_kind_label'] = distinguishedKindMapInverse[playlist_dict['distinguished_kind']]

                return playlist_dict

        attribut_name_list_len = len(attribut_name_list)

        missing_attribute_tags = {}

        """Creates playlists list"""
        main_dict = self.lib.findall('dict')

        sub_array = main_dict[0].findall('array')
        sub_array_childrens = list(sub_array[0])

        for array in sub_array_childrens:
            playlist_attributes = list(array)
            att_list = [None] * attribut_name_list_len

            extra_attributes = {}
            track_list = []
            for att_ind in range(0, len(playlist_attributes), 2):
                if playlist_attributes[att_ind].text == "Playlist Items" and playlist_attributes[att_ind+1].tag == "array":
                    tracks_sub_array = list(playlist_attributes[att_ind+1])

                    for k in range(len(tracks_sub_array)):
                        track_tags = list(tracks_sub_array[k])
                        assert len(track_tags) == 2
                        assert track_tags[0].tag == 'key' and track_tags[0].text == "Track ID"
                        assert track_tags[1].tag == 'integer'
                        track_list.append(int(track_tags[1].text))

                        #self.complete_playlist.append([cur_playlist_name, track_tags[1].text])
                else:
                    try:
                        #print("Looking at "+playlist_attributes[att_ind].text)
                        tag_index = attribut_name_list.index(playlist_attributes[att_ind].text)
                    except ValueError:
                        missing_attribute_tags[playlist_attributes[att_ind].text] = True
                        extra_attributes[playlist_attributes[att_ind].text] = self.get_plist_attr_value(playlist_attributes[att_ind].text, playlist_attributes[att_ind+1])
                        continue
                    att_list[tag_index] = self.get_plist_attr_value(playlist_attributes[att_ind].text, playlist_attributes[att_ind+1])

            new_playlist = PlayList(*att_list)
            new_playlist.set_track_indexes(self, track_list)
            if len(extra_attributes) > 0:
                new_playlist.add_extra_attributes(extra_attributes)
            self.playlists.append(new_playlist)
            self.playlist_by_persistent_id[new_playlist.playlist_persistent_id] = new_playlist

        if len(missing_attribute_tags) > 0:
            print("missing attribute handling: ", missing_attribute_tags.keys())

    def generate_playlist_dislay_paths(self):
        for playlist in self.playlists:
            display_path  = "/"+playlist.name
            parent_id = playlist.parent_persistent_id
            while parent_id:
                parent_playlist = self.playlist_by_persistent_id[parent_id]
                display_path = '/' + parent_playlist.name + display_path
                parent_id = parent_playlist.parent_persistent_id
            playlist.display_path = display_path

    def get_playlists(self):
        """Returns playlists list"""
        return self.playlists

    def get_song_list(self):
        """Returns playlists list"""
        return self.song_list

    def get_movie_list(self):
        """Returns playlists list"""
        return self.movie_list

    def get_podcast_list(self):
        """Returns playlists list"""
        return self.podcast_list

    def get_tvshow_list(self):
        """Returns playlists list"""
        return self.tvshow_list

    def get_audiobook_list(self):
        """Returns playlists list"""
        return self.audiobook_list


    def read_tracks(self):
        """Generate tracks list"""
        attribut_name_list = ["Track ID", "Size", "Total Time", "Date Modified",
                              "Date Added", "Bit Rate", "Sample Rate", "Play Count",
                              "Play Date", "Play Date UTC", "Skip Count", "Skip Date",
                              "Rating", "Album Rating", "Persistent ID", "Track Type",
                              "File Folder Count", "Library Folder Count", "Name",
                              "Artist", "Kind", "Location", "Album", 'Genre', 'Year',
                              'Release Date', 'Artwork Count', 'Sort Artist', 'Sort Name',
                              'Content Rating', 'Purchased', 'Has Video', 'HD', 'Movie',
                              'Album Artist', 'Composer', 'Disc Number', 'Disc Count',
                              'Track Number', 'Track Count', 'Normalization', 'Sort Album',
                              'Loved', 'Compilation', 'Sort Album Artist', 'Series',
                              'Episode Order', 'TV Show', 'Protected', 'Video Width',
                              'Video Height', 'Season', 'BPM', 'Podcast', 'Unplayed',
                              'Comments', 'Part Of Gapless Album', 'Work', 'Clean',
                              'Explicit', 'Sort Composer']

        class Track:
            def __init__(self, track_id, size, total_time, date_modified,
                         date_added, bitrate, sample_rate, play_count, play_date,
                         play_date_utc, skip_count, skip_date, rating,
                         album_rating, persistent_id, track_type,
                         file_folder_count, library_folder_count, name, artist,
                         kind, location, album, genre, year, release_date, artwork_count,
                         sort_artist, sort_name, content_rating, purchased, has_video, hd,
                         movie, album_artist, composer, disc_number, disc_count,
                         track_number, track_count, normalization, sort_album, loved,
                         compilation, sort_album_artist, series, episode_order, tv_show,
                         protected, video_width, video_height, season, bpm, podcast, unplayed,
                         comments, part_of_gapless_album, work, clean, explicit, sort_composer):
                self.extra_attributes = {}
                self.track_id = track_id
                self.size = size
                self.total_time = total_time
                self.date_modified = date_modified
                self.date_added = date_added
                self.bitrate = bitrate
                self.sample_rate = sample_rate
                self.play_count = play_count
                self.play_date = play_date
                self.play_date_utc = play_date_utc
                self.skip_count = skip_count
                self.skip_date = skip_date
                self.rating = rating
                self.album_rating = album_rating
                self.persistent_id = persistent_id
                self.track_type = track_type
                self.file_folder_count = file_folder_count
                self.library_folder_count = library_folder_count
                self.name = name
                self.artist = artist
                self.kind = kind
                self.location = location
                self.album = album

                self.genre = genre
                self.year = year
                self.release_date = release_date
                self.artwork_count = artwork_count
                self.sort_artist = sort_artist
                self.sort_name = sort_name
                self.content_rating = content_rating
                self.purchased = purchased
                self.has_video = has_video
                self.hd = hd
                self.movie = movie
                self.album_artist = album_artist
                self.composer = composer
                self.disc_number = disc_number
                self.disc_count = disc_count
                self.track_number = track_number
                self.track_count = track_count
                self.normalization = normalization
                self.sort_album = sort_album
                self.loved = loved
                self.compilation = compilation
                self.sort_album_artist = sort_album_artist
                self.series = series
                self.episode_order = episode_order
                self.tv_show = tv_show
                self.protected = protected
                self.video_width = video_width
                self.video_height = video_height
                self.season = season
                self.bpm = bpm
                self.podcast = podcast
                self.unplayed = unplayed
                self.comments = comments
                self.part_of_gapless_album = part_of_gapless_album
                self.work = work
                self.clean = clean
                self.explicit = explicit
                self.sort_composer = sort_composer
                if self.location:
                    self.location = urllib.request.unquote(self.location)

            def add_extra_attribute(self, key, value):
                self.extra_attributes[key] = value

            def add_extra_attributes(self, attributes):
                for key, value in attributes.items():
                    self.extra_attributes[key] = value

            def get_as_dict(self):
                track_dict = {}

                def add_non_None_attribute(key, value):
                    if value is not None:
                        track_dict[key] = value

                add_non_None_attribute('track_id', self.track_id)
                add_non_None_attribute('size', self.size)
                add_non_None_attribute('total_time', self.total_time)
                add_non_None_attribute('date_modified', self.date_modified)
                add_non_None_attribute('date_added', self.date_added)
                add_non_None_attribute('bitrate', self.bitrate)
                add_non_None_attribute('sample_rate', self.sample_rate)
                add_non_None_attribute('play_count', self.play_count)
                add_non_None_attribute('play_date', self.play_date)
                add_non_None_attribute('play_date_utc', self.play_date_utc)
                add_non_None_attribute('skip_count', self.skip_count)
                add_non_None_attribute('skip_date', self.skip_date)
                add_non_None_attribute('rating', self.rating)
                add_non_None_attribute('album_rating', self.album_rating)
                add_non_None_attribute('persistent_id', self.persistent_id)
                add_non_None_attribute('track_type', self.track_type)
                add_non_None_attribute('file_folder_count', self.file_folder_count)
                add_non_None_attribute('library_folder_count', self.library_folder_count)
                add_non_None_attribute('name', self.name)
                add_non_None_attribute('artist', self.artist)
                add_non_None_attribute('kind', self.kind)
                add_non_None_attribute('location', self.location)
                add_non_None_attribute('album', self.album)

                add_non_None_attribute('genre', self.genre)
                add_non_None_attribute('year', self.year)
                add_non_None_attribute('release_date', self.release_date)
                add_non_None_attribute('artwork_count', self.artwork_count)
                add_non_None_attribute('sort_artist', self.sort_artist)
                add_non_None_attribute('sort_name', self.sort_name)
                add_non_None_attribute('content_rating', self.content_rating)
                add_non_None_attribute('purchased', self.purchased)
                add_non_None_attribute('has_video', self.has_video)
                add_non_None_attribute('hd', self.hd)
                add_non_None_attribute('movie', self.movie)
                add_non_None_attribute('album_artist', self.album_artist)
                add_non_None_attribute('composer', self.composer)
                add_non_None_attribute('disc_number', self.disc_number)
                add_non_None_attribute('disc_count', self.disc_count)
                add_non_None_attribute('track_number', self.track_number)
                add_non_None_attribute('track_count', self.track_count)
                add_non_None_attribute('normalization', self.normalization)
                add_non_None_attribute('sort_album', self.sort_album)
                add_non_None_attribute('loved', self.loved)
                add_non_None_attribute('compilation', self.compilation)
                add_non_None_attribute('sort_album_artist', self.sort_album_artist)
                add_non_None_attribute('series', self.series)
                add_non_None_attribute('episode_order', self.episode_order)
                add_non_None_attribute('tv_show', self.tv_show)
                add_non_None_attribute('protected', self.protected)
                add_non_None_attribute('video_width', self.video_width)
                add_non_None_attribute('video_height', self.video_height)
                add_non_None_attribute('season', self.season)
                add_non_None_attribute('bpm', self.bpm)
                add_non_None_attribute('podcast', self.podcast)
                add_non_None_attribute('unplayed', self.unplayed)
                add_non_None_attribute('comments', self.comments)
                add_non_None_attribute('part_of_gapless_album', self.part_of_gapless_album)
                add_non_None_attribute('work', self.work)
                add_non_None_attribute('clean', self.clean)
                add_non_None_attribute('explicit', self.explicit)
                add_non_None_attribute('sort_composer', self.sort_composer)

                for key, value in self.extra_attributes:
                    track_dict[key] = value

                return track_dict

        attribut_name_list_len = len(attribut_name_list)

        missing_attribute_tags = {}

        # Create tracks list with attributes
        main_dict = self.lib.findall('dict')

        sub_array = main_dict[0].findall('dict')
        sub_array_childrens = list(sub_array[0])

        for track in sub_array_childrens:
            att_list = [None] * attribut_name_list_len

            if track.tag == "dict":
                extra_attributes = {}
                track_attributes = list(track)
                for att_ind in range(0, len(track_attributes), 2):
                    try:
                        tag_index = attribut_name_list.index(track_attributes[att_ind].text)
                    except ValueError:
                        missing_attribute_tags[track_attributes[att_ind].text] = True
                        extra_attributes[track_attributes[att_ind].text] = self.get_plist_attr_value(track_attributes[att_ind].text, track_attributes[att_ind+1])
                        continue
                    att_list[tag_index] = self.get_plist_attr_value(track_attributes[att_ind].text, track_attributes[att_ind+1])

                new_track = Track(*att_list)
                if len(extra_attributes) > 0:
                    new_track.add_extra_attributes(extra_attributes)

                self.track_map[new_track.track_id] = new_track
                if new_track.location and new_track.location.find('/Audiobooks/') >= 0:
                    self.audiobook_list.append(new_track)
                elif new_track.movie:
                    self.movie_list.append(new_track)
                elif new_track.podcast:
                    self.podcast_list.append(new_track)
                elif new_track.tv_show:
                    self.tvshow_list.append(new_track)
                else:
                    self.song_list.append(new_track)

        if len(missing_attribute_tags) > 0:
            print("missing attribute handling: ", missing_attribute_tags.keys())


def get_size(input_size):
    if input_size is None:
        return "unknown"
    """Returns the size of a track in a human-readable way"""
    return float("{0:.2f}".format(int(input_size) / 1E6))


def get_total_time(input_time):
    if input_time is None:
        return 0
    """Returns the duration of a track in a human-readable way"""
    return int(int(input_time) / 1000)


def get_rating(input_rating):
    """ Returns stars iTunes rating"""
    if input_rating:
        return (int(input_rating) / 100) * 5
    else:
        return input_rating


def get_track_path(input_url):
    """Returns the path of a track"""
    return unquote(urlparse(input_url).path[1:])
