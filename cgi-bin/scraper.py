import os
import sys
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, website_url, site_name):
        self.website_url = website_url
        self.site_name = site_name
        self.base_url = self.get_base_url()

    def get_base_url(self):
        host = os.environ.get('HTTP_HOST', 'localhost')
        port = os.environ.get('SERVER_PORT', '8000')   
        protocol = 'http://'  
        return f"{protocol}{host}:{port}/"

    def create_directory(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def download_file(self, url, folder):
        file_name = os.path.basename(urllib.parse.urlparse(url).path)
        if not file_name:
            file_name = 'index.html'
        file_path = os.path.join(folder, file_name)

        try:
            urllib.request.urlretrieve(url, file_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    def categorize_and_download(self, resource_url):
        parsed_url = urllib.parse.urlparse(resource_url)
        resource_path = parsed_url.path

        if resource_path.endswith(('.css')):
            folder = os.path.join(self.site_name, 'css')
        elif resource_path.endswith(('.js')):
            folder = os.path.join(self.site_name, 'js')
        elif resource_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):  
            folder = os.path.join(self.site_name, 'images')
        elif resource_path.endswith(('.woff', '.woff2', '.ttf', '.otf')):
            folder = os.path.join(self.site_name, 'fonts')
        elif resource_path.endswith(('.ico', '.icon', '.webapp')):
            folder = os.path.join(self.site_name, 'logos')
        elif resource_path.endswith(('.php', '.py', '.java', '.rb', '.go', '.c', '.cpp')):
            folder = os.path.join(self.site_name, 'languages')
        elif resource_path.endswith(('.html')):
            folder = os.path.join(self.site_name, 'html')
        else:
            folder = os.path.join(self.site_name, 'documents')

        self.create_directory(folder)
        self.download_file(resource_url, folder)

    def scrape_website(self):
        self.create_directory(self.site_name)

        try:
            response = urllib.request.urlopen(self.website_url)
            soup = BeautifulSoup(response, 'html.parser')

            self.download_file(self.website_url, self.site_name)

            for link in soup.find_all(['link', 'script', 'img']):
                resource_url = None
                if link.name == 'link' and link.get('href'):
                    resource_url = link['href']
                elif link.name == 'script' and link.get('src'):
                    resource_url = link['src']
                elif link.name == 'img' and link.get('src'):
                    resource_url = link['src']

                if resource_url:
                    resource_url = urllib.parse.urljoin(self.website_url, resource_url)
                    self.categorize_and_download(resource_url)

            self.generate_html_page()
        except Exception as e:
            print(f"Failed to scrape {self.website_url}: {e}")

    def generate_html_page(self):
        print("Content-type: text/html\n")
        print(f"""
        <html>
        <head>
            <style>
                #loader {{
                    display: none;
                    position: fixed;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                    z-index: 1000;
                    font-size: 24px;
                }}
            </style>
            <script>
                function showLoader() {{
                    document.getElementById('loader').style.display = 'block';
                }}
                function hideLoader() {{
                    document.getElementById('loader').style.display = 'none';
                }}
                function openWebsite() {{
                    window.open('{self.base_url}{self.site_name}/index.html', '_blank');
                }}
                window.onload = hideLoader;
            </script>
        </head>
        <body>
            <div id="loader">Loading...</div>
            <button onclick="showLoader(); openWebsite();">Open Scraped Website</button>
        </body>
        </html>
        """)

def main():
    query_string = os.environ.get('QUERY_STRING', '')
    params = urllib.parse.parse_qs(query_string)

    website_url = params.get('website_url', [None])[0]
    site_name = params.get('site_name', [None])[0]

    if website_url and site_name:
        scraper = WebScraper(website_url, site_name)
        scraper.scrape_website()
    else:
        print("Content-type: text/html\n")
        print("Error: Missing website URL or site name.")

if __name__ == "__main__":
    main()
