import argparse as ap
import requests
import re
import urllib.request
from shutil import copyfileobj
from bs4 import BeautifulSoup
import json

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

song_url_regex = r"(https:\/\/t4.bcbits.com\/stream\/[a-z0-9]{32}\/mp3-128\/[0-9]{0,12}\?p=[0-9]&ts=[0-9]{10}&t=[a-z0-9]{40}&token=[0-9]{10}_[a-z0-9]{40})"
album_data_regex = r"TralbumData = (\{(\s*?.*?)*?\});$"

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    soup = BeautifulSoup(requests.get(args.url, headers=request_header).text, "html.parser")

    script = soup.find('script', text=re.compile('TralbumData'))
    album_data = re.sub(r"([ ]+[\/]{2}.*\n)", '', re.search(album_data_regex, script.string, flags=re.DOTALL | re.MULTILINE).group(1))
    print(album_data)

    # Dumping the HTML page into "output.html" for inspection
    # with open("output.html", "wb") as f:
        # f.write(soup.prettify().encode("utf-8"))
    
    song_url = re.findall(song_url_regex, album_data)[0]
    with urllib.request.urlopen(song_url) as r, open("out.mp3", "wb") as f:
        copyfileobj(r, f)

if __name__ == "__main__":
    main()
