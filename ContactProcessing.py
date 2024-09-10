import re
#import phonenumbers
#from phonenumbers import PhoneNumberMatcher
from ContactItem import ContactItem

from contactLLM.contactLLM import ContactLLM
from nerPhoneModel.phoneModel import PhoneModel

class ContactProcessing:
    def __init__(self):
        self.contactLLM = ContactLLM()
        self.nerPhoneModel = PhoneModel()
        
    def extract_emails_phone_numbers_with_LLM(self, htmlContent):
        return self.contactLLM.get_contact_informations(htmlContent)
        
    def extract_phone_numbers_with_ner_model(self, htmlContent):
        return self.nerPhoneModel.get_phone_numbers(htmlContent)
        
    def extract_emails(self, contenu_html):
        pattern_email = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}')
        emails = pattern_email.findall(contenu_html)
        return emails
        
    def extract_phone_numbers(self, contenu_html):
        telephones = set()
        matches = PhoneNumberMatcher(contenu_html, "MA")
        for match in matches:
            phone_number = match.number
            formatted_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            telephones.add(formatted_number)
        return telephones
        
    def extract_social_network_links(self, contenu_html):
        social_networks = ['facebook','twitter','instagram','linkedin','youtube',"tiktok"]
        social_network_links = {}

        for network in social_networks: 
            pattern_network = re.compile(f'<a .*href="(https?://[^"]*{network}\.com[^"]*)"')
            network_links = pattern_network.findall(contenu_html)
            social_network_links[network] = set(network_links)
        return social_network_links
                
    def extract_contact_information(self, contenu_html, _url, contact_link_inf = None):
        try:
            _emails = self.extract_emails(contenu_html)
            # phones = self.extract_phone_numbers(contenu_html)  # with PhoneNumberMatcher
            phones = self.extract_phone_numbers_with_ner_model(contenu_html)
            
            if phones :
                phones_emails = self.extract_emails_phone_numbers_with_LLM(contenu_html)
                if phones_emails and "phones" in phones_emails.keys() and "emails" in phones_emails.keys():
                    print(phones_emails)
                    _emails += phones_emails["emails"]
                    phones = phones + phones_emails["phones"]
                
            social_network_links = self.extract_social_network_links(contenu_html)

            contact_inf = ContactItem(
                    url= _url,
                    emails= list(set(_emails)),
                    phones= list(set(phones)),
                    facebook= list(social_network_links["facebook"]),
                    twitter= list(social_network_links["twitter"]),
                    instagram= list(social_network_links["instagram"]),
                    linkedin= list(social_network_links["linkedin"]),
                    youtube= list(social_network_links["youtube"]),
                    tiktok= list(social_network_links["tiktok"])
                )

            result = {}
            result["status"] = "success"
            result["value"] = contact_inf
            return result

        except Exception as e:
            if contact_link_inf :
                error_message = f"==>>> Error : {e.args[0]} \n=> in extract_contact_information() at ContactProcessing\n=>(current_contact_link = {_url})\n=> contact_link_inf = {contact_link_inf})"
            else:
                error_message = f"==>>> Error : {e.args[0]} \n=> in extract_contact_information() at ContactProcessing\n=> (current_link = {_url})"
                
            print(error_message)
            result = {}
            result["status"] = "error"
            result["value"] = error_message
            return result
                        
    def extract_contact_links(self, contenu_html):
        pattern_href = re.compile(r'<a .*href="([^"]*[cC][oO][nN][tT][aA][cC][tT][^"]*)"')
        liens_trouves_href = pattern_href.findall(contenu_html)

        if liens_trouves_href:
            return liens_trouves_href
        else:
            terms_related_to_contact = ['contact', 'contactez-nous','Contactez nous', 'nous contacter', 'الإتصال', 'Qui sommes-nous', 'اتصل بنا',
                "Contact",
                "Contactez-nous",
                "Contactez nous",
                "Nous contacter",
                "Nous joindre",
                "Pour nous contacter",
                "Coordonnées",
                "Informations de contact",
                "Service client",
                "Support",
                "Aide",
                "Formulaire de contact",
                "Adresse",
                "Page de contact",
                "Qui sommes-nous",
                "Qui sommes nous",
                "Rejoignez-nous",
                "Travaillez avec nous",
                "الإتصال",
                "تواصل معنا",
                "اتصل بنا",
                "تواصل",
                "تواصلوا معنا",
                "معلومات الاتصال",
                "خدمة العملاء",
                "الدعم",
                "المساعدة",
                "نموذج الاتصال",
                "العنوان",
                "صفحة الاتصال",
                "من نحن",
                "الأسئلة الشائعة",
                "نشرة إخبارية",
                "انضم إلينا",
                "اعمل معنا",
                "Contact",
                "Contact us",
                "Get in touch",
                "Reach out to us",
                "Contact information",
                "Customer service",
                "Support",
                "Help",
                "Contact form",
                "Address",
                "Contact page",
                "About",
                "About us",
                "Join us",
                "Work with us"
                ]
            
            pattern_text = re.compile(r'<a [^>]*href="([^"]*)"[^>]*>.*({}).*<\/a>'.format('|'.join(terms_related_to_contact)), re.IGNORECASE)
            liens_trouves_text = pattern_text.findall(contenu_html)
            return liens_trouves_text