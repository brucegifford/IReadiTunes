# -*- coding: utf-8 -*-
"""
Tool to get any information about iTunes tracks and playlists quickly and easily.
Mickael <mickael2054dev@gmail.com>
MIT License
"""

import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse


def lib_init():
    """Initilize the library, must be called at the very beginning"""
    lib_class = Library()
    return lib_class


class Library(object):
    def __init__(self):
        """Constructor"""
        self.lib = 0
        self.complete_playlist = []
        self.track_attr_list = []
        self.track_id_map = {}

    def parse(self, path_to_XML_file):
        """Reads xml file and generate tracks list"""
        tree = ET.parse(path_to_XML_file)
        self.lib = tree.getroot()
        self.read_tracks()

    def get_playlist_list(self):
        """Creates playlists list"""
        main_dict = self.lib.findall('dict')

        sub_array = main_dict[0].findall('array')
        sub_array_childrens = list(sub_array[0])

        # For each playlist
        playlist_name_list = []
        for array in sub_array_childrens:
            playlist = list(array)

            # Save name of playlists
            for i in range(len(playlist)):
                if playlist[i].text == "Name":
                    playlist_name_list.append(playlist[i + 1].text)
                    cur_playlist_name = playlist[i + 1].text

                # Get tracks
                if playlist[i].tag == "array":
                    sub_array = list(playlist[i])

                    for k in range(len(sub_array)):
                        track_tags = list(sub_array[k])

                        self.complete_playlist.append([cur_playlist_name,
                                                       track_tags[1].text])

        return playlist_name_list

    def get_track_list(self):
        """Returns playlists list"""
        return self.track_attr_list

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
                        extra_attributes[track_attributes[att_ind].text] = track_attributes[att_ind + 1].text
                        pass
                    else:
                        att_list[tag_index] = track_attributes[att_ind + 1].text

                new_track = Track(*att_list)
                if len(extra_attributes) > 0:
                    new_track.add_extra_attributes(extra_attributes)
                self.track_attr_list.append(new_track)
                self.track_id_map[new_track.track_id] = new_track

        if len(missing_attribute_tags) > 0:
            print("missing attribute handling: ", missing_attribute_tags.keys())


    def get_playlist_contents(self, playlist_name):
        """Returns tracks (with attributes) of given playlist"""
        playlist_with_attributes = []

        for track in self.complete_playlist:
            if track[0] == playlist_name:
                temp_track_ID = track[1]

                temp_track = self.track_id_map[temp_track_ID]
                playlist_with_attributes.append(temp_track)
                """
                for elem in self.track_attr_list:                    
                    if elem.track_id == temp_track_ID:
                        playlist_with_attributes.append(elem)
                        break
                """
        return playlist_with_attributes


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
