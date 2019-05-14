import argparse as ap
import requests
import re
import sys
import os
import json
import urllib.request
import shutil
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE2, TALB, TRCK
from bs4 import BeautifulSoup

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

url_regex = r'^(https:\/\/)?([a-zA-Z0-9]*?).bandcamp.com(\/album\/|\/track\/)[a-zA-Z0-9\-]+$'

def re_s(p: str, s: str, g = 0):
    return re.search(p, s, flags= re.S | re.M).group(g)

def clean_filename(name):
    return re.sub(r'[<>?:"\\\/|*]', '', name)

def check_dir(filepath):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Created {}\\".format(directory))

def download_track(trackinfo, albuminfo):
    if albuminfo['album_title'] is not None:
        filepath = ".\\out\\{}\\{}.mp3".format(clean_filename(albuminfo['album_title']), clean_filename(trackinfo['track_title']))
    else:
        filepath = ".\\out\\{}.mp3".format(clean_filename(trackinfo['track_title']))
    check_dir(filepath)
    with urllib.request.urlopen(trackinfo['mp3_url']) as r, open(filepath, "wb") as f:
        shutil.copyfileobj(r, f)
    set_tags(filepath, trackinfo, albuminfo)

def set_tags(filepath, trackinfo, albuminfo):
    try:
        audio = ID3(filepath)
    except ID3NoHeaderError:
        audio = ID3()
    if trackinfo['has_album'] is not False:
        audio.add(TALB(encoding=3, text=albuminfo['album_title']))
        audio.add(TRCK(encoding=3, text=trackinfo['track_num']))
    audio.add(TIT2(encoding=3, text=trackinfo['track_title']))
    audio.add(TPE2(encoding=3, text=albuminfo['album_artist']))
    audio.save(filepath)

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    if not re.match(url_regex, args.url):
        print("Invalid Bandcamp URL.")
        sys.exit(0)
    
    try:
        r = requests.get(args.url, headers=request_header)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    soup = BeautifulSoup(r.text, "html.parser")
    js_raw = soup.find('script', text=re.compile('var TralbumData =')).string
    current = json.loads(re_s(r'current: (\{.*?\}),', js_raw, 1))
    trackinfo_raw = json.loads(re_s(r'trackinfo: (\[\{.*\}\]),', js_raw, 1))
    band_name = re_s(r'var BandData = \{.*?name: \"(.*?)\",$', js_raw, 1)
    has_album = True if re_s(r'var EmbedData = {.*?\{ name\s?: \"(album|track)\"', js_raw, 1) == "album" else False
    is_album_page = True if current['type'] == "album" else False
    albuminfo = {
        "album_title": current['title'] if is_album_page else re_s(r'var EmbedData = \{.*?album_title\s?: \"(.*?)\"', js_raw, 1) if has_album else None,
        "album_artist": soup.find("span", { "itemprop": "byArtist" }).findChildren("a")[0].text
    }

    if is_album_page:
        print("{} by {}".format(current['title'], albuminfo['album_artist']))
    for i in range(len(trackinfo_raw)):
        if trackinfo_raw[i]['file'] is None:
            print("Track {}, \"{}\", has no mp3-128".format(trackinfo_raw[i]['track_num'], trackinfo_raw[i]['title']))
            continue
        trackinfo = {
            "track_title": trackinfo_raw[i]['title'],
            "track_artist": re_s(r'TralbumData = {.*?artist: \"(.*?)\",', js_raw, 1) if not is_album_page else None,
            "track_num": str(trackinfo_raw[i]['track_num']),
            "mp3_url": trackinfo_raw[i]['file']['mp3-128'],
            "has_album": has_album
        }
        print("({} of {}) Downloading {}".format(i + 1, len(trackinfo_raw), trackinfo['track_title']))
        download_track(trackinfo, albuminfo)
        print("Finished downloading {}".format(trackinfo['track_title']))

if __name__ == "__main__":
    main()
