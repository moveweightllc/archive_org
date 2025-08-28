# encoding: UTF-8
# VERSION: 0.9
# AUTHORS: moveweight (https://github.com/moveweightllc)

from novaprinter import prettyPrinter
import urllib.parse
import urllib.request
import json

class archive_org(object):
    name = 'Archive.org'
    url = 'https://archive.org'
    version = '0.9'
    supported_categories = {
        'all': 'all',
        'books': 'texts',
        'games': 'software',
        'movies': 'movies',
        'music': 'audio',
        'pictures': 'image',
        'software': 'software',
        'tv shows': 'movies'
    }

    api_base = 'https://archive.org/advancedsearch.php'
    user_agent = 'qBittorrent/5.1.0'
    referer = 'https://archive.org/'

    def can_handle_url(self, url):
        return url.startswith(self.url)

    def __init__(self):
        pass

    def download_torrent(self, info):
        print(f"Download requested for {info}")
        pass

    def search(self, what, cat='all'):
        page = 1
        while True:
            # Build mediatype filter if category selected
            category_filter = ''
            if cat != 'all':
                mediatype = self.supported_categories.get(cat.lower(), 'all')
                if mediatype != 'all':
                    category_filter = f' AND mediatype:"{mediatype}"'

            # Build search query string
            search = f'({what}) AND format:"*torrent*"{category_filter}'
            url = (
                f'{self.api_base}?q={urllib.parse.quote(search)}'
                f'&fl[]=creator&fl[]=identifier&fl[]=item_size&fl[]=title&fl[]=mediatype'
                f'&sort[]=downloads+desc&rows=50&page={page}&output=json'
            )

            try:
                headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'application/json',
                    'Referer': self.referer
                }
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as response:
                    data = response.read().decode('utf-8')

                parsed = json.loads(data)
                docs = parsed.get('response', {}).get('docs', [])
                if not docs:
                    break

                for doc in docs:
                    identifier = doc.get('identifier')
                    if not identifier:
                        continue

                    title = doc.get('title', 'Unknown')
                    creator = doc.get('creator')
                    if creator:
                        if isinstance(creator, list):
                            creator = ', '.join(creator)
                        title += f' [{creator}]'

                    size = str(doc.get('item_size', -1))
                    result = {
                        'name': title,
                        'link': f'https://archive.org/download/{identifier}/{identifier}_archive.torrent',
                        'desc_link': f'https://archive.org/details/{identifier}',
                        'size': size if size.isdigit() else '-1',
                        'seeds': '-1',
                        'leech': '-1',
                        'engine_url': self.url
                    }
                    prettyPrinter(result)

                if len(docs) < 50:
                    break
                page += 1

            except Exception as e:
                print(f"Archive.org plugin error: {str(e)}")
                break

