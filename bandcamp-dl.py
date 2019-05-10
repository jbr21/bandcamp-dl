import argparse as ap
import requests
import re
import urllib.request
import shutil

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

regex = r"(https:\/\/t4.bcbits.com\/stream\/[a-z0-9]{32}\/mp3-128\/[0-9]{10}\?p=[0-9]&ts=[0-9]{10}&t=[a-z0-9]{40}&token=[0-9]{10}_[a-z0-9]{40})"

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    r = requests.get(args.url, headers=request_header)
    html = r.text
    song_url = re.findall(regex, html)[0]
    
    with urllib.request.urlopen(song_url) as song_response, open("out.mp3", "wb") as out_file:
        shutil.copyfileobj(song_response, out_file)

if __name__ == "__main__":
    main()