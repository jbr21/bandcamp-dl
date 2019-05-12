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

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

album_data_regex = r"TralbumData = (\{(\s*?.*?)*?\});$"
track_info_regex = r"trackinfo: (\[\{.*\}\]),"

def download_track(url, out="out.mp3"):
    with urllib.request.urlopen(url) as r, open(out, "wb") as f:
        shutil.copyfileobj(r, f)

def get_track_info(album_data):
    track_raw = json.loads(re.search(track_info_regex, album_data, flags=re.DOTALL | re.MULTILINE).group(1))
    track_info = {
        "title": track_raw[0]['title'],
        "track-num": str(track_raw[0]['track_num']),
        "album": str(re.search(r'album_url: "\/album\/(.*)",', album_data).group(1)),
        "album-artist": str(re.search(r'artist: "(.*)",', album_data).group(1)),
        "mp3-url": track_raw[0]['file']['mp3-128']
    }
    return track_info

def set_tags(file, track_info):
    try:
        audio = ID3(file)
    except ID3NoHeaderError:
        audio = ID3()
    audio.add(TIT2(encoding=3, text=track_info['title']))
    audio.add(TPE2(encoding=3, text=track_info['album-artist']))
    audio.add(TALB(encoding=3, text=track_info['album']))
    audio.add(TRCK(encoding=3, text=track_info['track-num']))
    audio.save(file)

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    try:
        r = requests.get(args.url, headers=request_header)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    
    soup = BeautifulSoup(r.text, "html.parser")

    script = soup.find('script', text=re.compile('TralbumData'))
    album_data = re.search(album_data_regex, script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    track_info = get_track_info(album_data)
    file_path = ".\\test\\{}\\{}.mp3".format(track_info['album'], re.sub(r'[<>!?:"\\\/|*]', '', track_info['title']))

    download_track(track_info['mp3-url'], file_path)
    set_tags(file_path, track_info)

    # Dumping the HTML page into "output.html" for inspection
    # with open("output.html", "wb") as f:
        # f.write(soup.prettify().encode("utf-8"))

if __name__ == "__main__":
    main()
