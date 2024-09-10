import threading
import pandas as pd

class SharedListURLs:
    def __init__(self):
        self.allURLs = ['http://hespress.com/',
                    'https://www.hibapress.com',
                    'https://www.goud.ma',
                    'http://lemonde.fr/',
                    'https://www.lematin.ma'
                    ]
        self.data = []
        self.lock = threading.Lock()
        self.nb_URLs=0
        
    def load_data(self) :
        file_xslx_name = "./links_data/WebSites.xlsx"

        def url_processing(url):
            if url.startswith("http//"):
                return url.replace("http//", "http://")
            elif url.startswith("https//"):
                return url.replace("https//", "https://")
            elif not url.startswith("http://") and not url.startswith("https://"):
                return "https://" + url
            else:
                return url

        df = pd.read_excel(file_xslx_name)
        
        df['url'] = df['domain'].apply(url_processing)

        self.allURLs = df['url'].tolist()
        self.nb_URLs = len(self.allURLs)
        
    def select_data(self, start, end):
        if end < self.nb_URLs:
            self.data = self.allURLs[start:end]
        else:
            self.data = self.allURLs[start:self.nb_URLs]