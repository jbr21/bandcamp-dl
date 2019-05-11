import argparse as ap
import requests
import re
import urllib.request
import shutil
from bs4 import BeautifulSoup
import json
# import mutagen

request_header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

song_url_regex = r"(https:\/\/t4.bcbits.com\/stream\/[a-z0-9]{32}\/mp3-128\/[0-9]{10}\?p=[0-9]&ts=[0-9]{10}&t=[a-z0-9]{40}&token=[0-9]{10}_[a-z0-9]{40})"
album_data_regex = r"TralbumData = (\{(\s*?.*?)*?\});$"

def get_tags():
    pass

def set_tags():
    pass

def main():
    parser = ap.ArgumentParser(description="Download music from Bandcamp at 128kbps")
    parser.add_argument('url', action="store", help="Given URL to Bandcamp track")
    args = parser.parse_args()

    r = requests.get(args.url, headers=request_header)
    soup = BeautifulSoup(r.text, "html.parser")

    script = soup.find('script', text=re.compile('TralbumData'))
    json_text = re.sub(r"([ ]+[\/]{2}.*\n)", '', re.search(album_data_regex, script.string, flags=re.DOTALL | re.MULTILINE).group(1))
    print(json_text)
    # json_data = json.loads(json_text)

    # print(soup.prettify())
    # with open("output.html", "wb") as f:
        # f.write(soup.prettify().encode("utf-8"))
    
    # song_url = re.findall(song_url_regex, html)[0]
    # with urllib.request.urlopen(song_url) as song_response, open("out.mp3", "wb") as out_file:
    #     shutil.copyfileobj(song_response, out_file)

if __name__ == "__main__":
    main()
