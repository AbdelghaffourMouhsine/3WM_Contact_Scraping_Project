import threading
from ContactProcessing import ContactProcessing
from ContactItem import ContactItem
from ContactScraping import ContactScraping

from contact_links_classification.ContactLinkModel import ContactLinkModel

class WorkerThread(threading.Thread):
    
    def __init__(self, thread_id, shared_list, contact_storage):
        super(WorkerThread, self).__init__()
        self.thread_id = thread_id
        self.shared_list = shared_list
        self.contact_storage = contact_storage
        self.contactProcessing = ContactProcessing()
        self.contactLinkModel = ContactLinkModel()
        self.contactScraping = ContactScraping(self.contact_storage, self.contactProcessing, self.contactLinkModel)
        
    def run(self):
        while True:
            try:
                # Access the shared list synchronously
                with self.shared_list.lock:
                    if not self.shared_list.data:
                        break  # The list is empty, the thread ends

                    url = self.shared_list.data.pop(0)

                    print(f"*"*100)
                    print(f"url_item = {url} ||| by_thread_id = {self.thread_id}")
                    print(f"*"*100)
                
                contact_item = self.contactScraping.scraping_contact(url)
                
                if contact_item :
                    # Store result in CSV file synchronously
                    with self.contact_storage.lock_file:
                        self.contact_storage.insert_contact(contact_item)

            except IndexError:
                pass  # La liste était probablement vide, pas besoin de gérer l'exception ici ???????????????????