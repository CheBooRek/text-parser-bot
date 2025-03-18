from urllib.parse import urlparse


def validate_url(txt):

    try:
        url = urlparse(txt)
        if url.scheme == '' or url.netloc == '':
            return None
        else:
            return url
    except:
        return None
    

def build_filename(url, ext='pdf'):

    netloc = url.netloc.replace('.', '_')
    path = url.path.strip('/').replace('/', '_')
    nm = '_'.join([netloc, path])
    filename = f'{nm}.{ext}'

    return filename
