import argparse as ap
import requests
import re
import urllib.request
import sys
import shutil
from bs4 import BeautifulSoup
import json
import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE2, TALB, TRCK
import os

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

url_regex = r"^(https:\/\/)?([a-zA-Z0-9]*?).bandcamp.com(\/album\/|\/track\/)[a-zA-Z0-9\-]+$"
album_data_regex = r"TralbumData = (\{(\s*?.*?)*?\});$"
track_info_regex = r"trackinfo: (\[\{.*\}\]),"
current_regex = r"current: (\{.*?\}),"

def download_track(url, out=".\\out\\out.mp3"):
    with urllib.request.urlopen(url) as r, open(out, "wb") as f:
        shutil.copyfileobj(r, f)

def check_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Created {}\\".format(directory))
    else:
        return

def get_album_info(album_raw, is_album):
    if is_album is True:
        current_raw = json.loads(re.search(current_regex, album_raw, flags=re.DOTALL | re.MULTILINE).group(1))
        album_info = {
            "album": current_raw['title'],
            "album-artist": current_raw['artist']
        }
    else:
        album_info = {
            "album": str(re.search(r'album_url: "\/album\/(.*)",', album_raw).group(1)),
            "album-artist": str(re.search(r'artist: "(.*)",', album_raw).group(1))
        }
    return album_info

def get_track_info(album_raw, i=0):
    track_raw = json.loads(re.search(track_info_regex, album_raw, flags=re.DOTALL | re.MULTILINE).group(1))
    track_info = {
        "title": track_raw[i]['title'],
        "track-num": str(track_raw[i]['track_num']),
        "mp3-url": track_raw[i]['file']['mp3-128']
    }
    return track_info

def set_tags(file, track_info, album_info):
    try:
        audio = ID3(file)
    except ID3NoHeaderError:
        audio = ID3()
    audio.add(TIT2(encoding=3, text=track_info['title']))
    audio.add(TPE2(encoding=3, text=album_info['album-artist']))
    audio.add(TALB(encoding=3, text=album_info['album']))
    audio.add(TRCK(encoding=3, text=track_info['track-num']))
    audio.save(file)

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    if re.match(url_regex, args.url):
        try:
            r = requests.get(args.url, headers=request_header)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find('script', text=re.compile('TralbumData'))
        album_raw = re.search(album_data_regex, script.string, flags=re.DOTALL | re.MULTILINE).group(1)
        track_raw = json.loads(re.search(track_info_regex, album_raw, flags=re.DOTALL | re.MULTILINE).group(1))
        if "/album/" in args.url:
            album_info = get_album_info(album_raw, True)
        else:
            album_info = get_album_info(album_raw, False)
        album_dir_name = re.sub(r'[<>!?:"\\\/|*]', '', album_info['album'])
        
        check_dir(".\\out\\{}\\".format(album_dir_name))
        for track in range(len(track_raw)):
            track_info = get_track_info(album_raw, track)
            file_path = ".\\out\\{}\\{}.mp3".format(album_dir_name, re.sub(r'[<>!?:"\\\/|*]', '', track_info['title']))
            
            print("({} of {}) Downloading {}. {}".format(track + 1, len(track_raw), track_info['track-num'], track_info['title']))
            download_track(track_info['mp3-url'], file_path)
            print("Finished downloading {}. {}".format(track_info['track-num'], track_info['title']))
            set_tags(file_path, track_info, album_info)

    else:
        print("{} is not a valid track or album URL".format(args.url))
        sys.exit(1)

if __name__ == "__main__":
    main()
