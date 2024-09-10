from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time 

from ContactItem import ContactItem

class ContactScraping():
    
    def __init__(self, contact_storage, contactProcessing, contactLinkModel):
        self.contact_storage = contact_storage
        self.contactProcessing = contactProcessing
        self.contactLinkModel = contactLinkModel
        self.contactLinkModel.load_from_local()
        
        # IP address and port and server of the Selenium hub and browser options
        self.HUB_HOST = "192.168.3.32"
        self.HUB_PORT = 4444
        self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
        self.options = webdriver.ChromeOptions()
        self.driver = None
        
    def scraping_contact(self, _url):
        try:
            self.driver = webdriver.Remote(command_executor=self.server, options=self.options)
            
            self.driver.get(_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
             )
            
            _url = self.driver.current_url
            
            contact_item = ContactItem(url=_url)
            
            contenu_html = self.driver.page_source
            
            contact_inf_result_0 = self.contactProcessing.extract_contact_information(contenu_html, _url)
            
            if contact_inf_result_0["status"] == "success":
                
                contact_inf_result_0["value"].add_contact_sources()
                contact_item.concatenate_lists(contact_inf_result_0["value"])

                # contact_links = self.contactProcessing.extract_contact_links(contenu_html)
                contact_links = self.contactLinkModel.get_contact_links(contenu_html)
                
                i=0
                current_url_contact= None
                for contact_link in contact_links:
                    try:
                        if i != 0:
                            self.driver.get(_url)
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                             )

                        self.go_to_contact_page(contact_link, _url)
                        WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                                     )
                        
                        contenu_html = self.driver.page_source
                        
                        current_url_contact = self.driver.current_url

                        contact_inf_result_1 = self.contactProcessing.extract_contact_information(contenu_html, current_url_contact, contact_link)
                        
                        if contact_inf_result_1["status"] == "success" :
                            
                            contact_inf_result_1["value"].add_contact_sources()
                            contact_item.concatenate_lists(contact_inf_result_1["value"])
                        else:
                            with self.contact_storage.lock_file_errors:
                                self.contact_storage.write_error(_url,"Error",contact_inf_result_1["value"])

                    except Exception as e:
                        error_message = f"==>>> Error : {e.args[0]} \n=> in for contact_link in contact_links:...\n=>(current_url_contact == {current_url_contact})\n=> (contact_link = {contact_link})"
                        print(error_message)
                        
                        with self.contact_storage.lock_file_errors:
                            self.contact_storage.write_error(_url, "Error",error_message)
                        
                    finally:
                        i=i+1

                print(contact_item)

                return contact_item
            
            else:
                with self.contact_storage.lock_file_errors:
                    self.contact_storage.write_error(_url, "Error",contact_inf_result_0["value"])
                    return None
                
        except Exception as e:
            error_message = f"==>>> Error : {e.args[0]}\n=> in scraping_contact() at ContactScraping"
            print(error_message)
            
            with self.contact_storage.lock_file_errors:
                self.contact_storage.write_error(_url, "Error",error_message)
            return None
            
        finally:
            self.driver.quit()
            
    def go_to_contact_page(self, contact_link, base_url):
        try:
            mode = None
            # with RE ( contact_link == hrefCentent )
            # select contact link with hrefCentent
            link_elements_href = self.driver.find_elements(By.CSS_SELECTOR, f'[href="{contact_link}"]')
            if link_elements_href and len(link_elements_href) > 0:
                link_element_href = link_elements_href[0]
                self.driver.execute_script("arguments[0].click();", link_element_href)
                mode = "href_1"
            else:
                # with RE or with contact_link_extraction_model (BERT) ==> contact_link == (hrefCentent, linkName)
                # select contact link with hrefCentent
                link_elements_href = self.driver.find_elements(By.CSS_SELECTOR, f'[href="{contact_link[0]}"]')
                if link_elements_href and len(link_elements_href) > 0:
                    link_element_href = link_elements_href[0]
                    self.driver.execute_script("arguments[0].click();", link_element_href)
                    mode = "href_2"
                else:
                    # select contact link with linkName (linkContent)
                    link_elements_text = self.driver.find_elements(By.XPATH, f'//a[contains(text(), "{contact_link[1]}")]')
                    if link_elements_text and len(link_elements_text) > 0:
                        link_element_text = link_elements_text[0]
                        self.driver.execute_script("arguments[0].click();", link_element_text)
                        mode = "text"
                    else:
                        Warning_value = f"==>>> Warning : contact link not found => contact_link == {contact_link} \n=> base_url == {base_url}"
                        with self.contact_storage.lock_file_errors:
                                self.contact_storage.write_error(self.driver.current_url, "Warning",Warning_value)
                            
                        print(f"@"*100)
                        print(f":( :( :( {Warning_value}")
                        print(f"@"*100)

            current_url = self.driver.current_url
            if current_url == base_url:
                Warning_value = f"==>>> Warning : Unable to access contact page => contact_link == {contact_link} \n=> base_url == {base_url}"
                with self.contact_storage.lock_file_errors:
                    self.contact_storage.write_error(self.driver.current_url, "Warning", Warning_value)
                            
            print(f"$"*100)
            print(f"mode = {mode} || contact_link = {contact_link}")
            print(f"$"*100)
            time.sleep(1)
            
        except Exception as e:
            error_message = f"==>>> Error : {e.args[0]} \n=> in go_to_contact_page() at ContactScraping"
            print(error_message)
            with self.contact_storage.lock_file_errors:
                self.contact_storage.write_error(self.driver.current_url, "Error", error_message)