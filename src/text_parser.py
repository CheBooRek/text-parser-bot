import os
import requests

from bs4 import BeautifulSoup
from fpdf import FPDF


class TextParser(object):
    
    def __init__(self):
        pass
    
    def __call__(self, url, unique=False, filename=None):
        """Run text parser logic"""
        html = self.download_html(url)
        text = self.extract_text_from_html(html, unique)
        
        if filename:
            self.write_to_file(text, filename)
        else:
            return text

    def download_html(self, url):
        """Download the HTML content of the given URL."""
        response = requests.get(url)
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
    
    @staticmethod
    def write_to_file(lines, filename, file_format='pdf'):
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

            text = '\n'.join(lines)#.encode('latin-1', 'replace').decode('latin-1')
            #text = text.encode('utf-8', 'replace').decode('utf-8')

            pdf.multi_cell(0, 10, txt=text)
            pdf.output(path)
                
        else:
            raise NotImplementedError('only txt and pdf format supported')
                
        print(f'File successfully written in {path}')


def main():
    # Input URL from the user
    url = input("Enter the URL of the page: ")
    filepath = input('Enter filename to save: ')
    
    try:
        text_parser = TextParser()
        text_parser(url, filepath=filepath)
    
    except requests.RequestException as e:
        print(f"Error downloading the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
