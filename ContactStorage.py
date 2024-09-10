import threading
import csv

class ContactStorage:
    def __init__(self, file_path):
        self.file_path = f"{file_path}.csv"
        self.fieldnames = ['url', 'emails', 'telephones', 'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'contact_sources']
        self.file = open(self.file_path, 'a', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.lock_file = threading.Lock()
        
        # Check if the file is empty, then write the header
        if self.file.tell() == 0:
            self.writer.writeheader()
            
        ################################################## for : Errors file ##############################
        self.file_errors = open(f"{file_path}_errors.csv", 'a', newline='', encoding='utf-8')
        self.writer_errors = csv.DictWriter(self.file_errors, fieldnames=["url","type", "error_message"])
        self.lock_file_errors = threading.Lock()
        # Check if the file is empty, then write the header
        if self.file_errors.tell() == 0:
            self.writer_errors.writeheader()

    def insert_contact(self, contact_item):
        contact_data = {
            'url': contact_item.url,
            'emails': ', '.join(contact_item.emails),
            'telephones': ', '.join(contact_item.phones),
            'facebook': ', '.join(contact_item.facebook),
            'twitter': ', '.join(contact_item.twitter),
            'instagram': ', '.join(contact_item.instagram),
            'linkedin': ', '.join(contact_item.linkedin),
            'youtube': ', '.join(contact_item.youtube),
            'tiktok': ', '.join(contact_item.tiktok),
            'contact_sources': ', '.join(contact_item.contact_sources)
        }

        self.writer.writerow(contact_data)

    def close_file(self):
        self.file.close()
        
    ################################################## for : Errors file ##############################
    def write_error(self, url,type, error_message):
        error_content = {
            'url': url,
            'type': type,
            'error_message': error_message
            }
        
        self.writer_errors.writerow(error_content)
        
    def close_file_errors(self):
        self.file_errors.close()