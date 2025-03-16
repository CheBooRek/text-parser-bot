import os
import re
import requests

from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urlparse
from fpdf import FPDF


def validate_url(txt):

    try:
        url = urlparse(txt)
        return url
    except:
        return None
    

class TextParser(object):
    
    def __init__(self, url=None, file_format='pdf'):
        
        self.url = url
        self.file_format = file_format
        self.texts = []
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

    def set_url(self, url):
        self.url = url

    def set_file_format(self, file_format):
        self.file_format = file_format
    
    def __call__(self, filename=None, unique=False):
        """Run text parser logic"""
        html = self.download_html(self.url)
        text = self.extract_text_from_html(html, unique)
        
        if filename:
            self.write_to_file(text, filename, self.file_format)
        else:
            return text
        
    def _validate_link(self, link, internal_only=False):

        pat = self.url if internal_only else 'http'
    
        if link.startswith(pat) and link.find('#') == -1:
            return link
        elif link.startswith('/') and link.find('#') == -1:
            return urljoin(self.url, link)
        
    @staticmethod
    def _remove_emojis(data):
        emoj = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            u"\xa0" # blanks
                        "]+", re.UNICODE)
        return re.sub(emoj, '', data)

    def download_html(self, url):
        """Download the HTML content of the given URL."""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        
        response.encoding = response.apparent_encoding

        return response.text
    
    def extract_text_from_html(self, html, unique=False):
        """Extract all text from the HTML content."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Get the text from the remaining HTML
        text = soup.get_text(separator=' ')

        # Clean up the text by removing extra whitespace
        lines_raw = (line.strip() for line in text.splitlines())
        
        lines = []
        
        for line_raw in lines_raw:
            line = ' '.join([phrase.strip() for phrase in line_raw.split("  ") if phrase])
            if line:
                lines.append(line)

        if unique:
            lines = [*dict.fromkeys(lines)]

        print('Text extracted!')

        return lines
    
    def get_html_links(self, html, internal_only=False):

        links = []
        soup = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('a'))

        for link in soup:
            if link.has_attr('href'):
                href = self._validate_link(link['href'], internal_only)
                if href:
                    links.append(href)

        links = [*dict.fromkeys(links)]

        return links
    
    def write_to_file(self, lines, filename, file_format='pdf'):
        """Write parsed text to file on provided path"""
        path = os.path.join('texts/', filename)

        if file_format == 'txt':
            with open(path, 'w') as f:
                for line in lines:
                    f.write(f"{line}\n")

        elif file_format == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("Arial", "", "fonts/arial.ttf", uni=True)
            pdf.set_font("Arial", size=12)

            text_raw = '\n'.join(lines)#.encode('latin-1', 'replace').decode('latin-1')
            text = self._remove_emojis(text_raw)
            #text = text.encode('utf-8', 'replace').decode('utf-8')

            pdf.multi_cell(0, 10, txt=text)
            pdf.output(path)
                
        else:
            raise NotImplementedError('only txt and pdf format supported')
                
        print(f'File successfully written in {path}')


def main():
    # Input URL from the user
    url = input("Enter the URL of the page: ")
    filename = input('Enter filename to save: ')
    file_format = input('Choose file format (pdf/txt): ')
    
    try:
        text_parser = TextParser(url=url, file_format=file_format)
        text_parser(filename=filename, unique=True)
    
    except requests.RequestException as e:
        print(f"Error downloading the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
