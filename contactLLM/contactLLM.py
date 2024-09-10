from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import time
import json

# contactLLM.
from contactLLM.pageProcessing import PageProcessing
from contactLLM.sentenceProcessing import SentenceProcessing

class ContactLLM:

    def __init__(self, llm_name = "llama3", _base_url="http://192.168.3.32:11000"):
        self.pageProcessing = PageProcessing()
        self.sentenceProcessing = SentenceProcessing()
        self.llm_name = llm_name
        self.llm = ChatOllama(model = self.llm_name,
                     format = "json",
                     temperature = 1,
                     num_gpu = 0, # To use CPU only
                     # callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]),
                     max_new_tokens = 255,
                     base_url=_base_url
                )
        self.messages = [
                (
                    "system","""You are an agent tasked with extracting contact information (emails, phone and fax and whatsapp numbers) from a text of contact page. For example:
                                Example (text of contact page) :
                                    * Lanarkshire G32 8FG Telephone Number |&| 06 82 10 33 81 |&| News desk |&| 0111 222 3333 |&| abdelghaffour@gmail.com |&| fax : +971-3-4444111 |&| business with. or Newspaper Sales |&| mouhsine.abdo@usmba.ac.ma |&| Advertising - Kirsty McKinney - +212 682103381 | Craig Anderson - 0111 222 3333 | abdo@gmail.com |&| Digital Subscriptions - 0800 788 0800 (Mon-Fri, 9-5.30pm)*
                                
                                Your task is to extract the contact information and format it into the following JSON object:
                                    [
                                         "emails": ["abdelghaffour@gmail.com", "mouhsine.abdo@usmba.ac.ma", "abdo@gmail.com"],
                                         "phones": ["06 82 10 33 81", "0111 222 3333", "+971-3-4444111", "+212 682103381", "0800 788 0800"]
                                    ]
                                => Make sure the value of the key "phones" contain a phone, fax and whatsapp numbers.
                                => Make sure to identify and extract the relevant information accurately.
                                    """
                ),
                (
                    "human","""Extract the contact information (emails, phones) and format it into a JSON object from the following text (Make sure  don't create an other key, juste 'emails' and 'phones' and the value of the key "phones" contain all phone, fax and whatsapp numbers in the text contact page) :"""
                ),
                (
                    "human","{htmlCode}"
                )
            ]

        self.template = ChatPromptTemplate.from_messages(self.messages)
        self.chain = self.template | self.llm | StrOutputParser()
        
    def predict(self, html_source_code, execution_time=False):
        start = time.perf_counter()
        response = self.chain.invoke({ "htmlCode": html_source_code })
        end = time.perf_counter()
        parsed_json = json.loads(response)
        if execution_time :
            parsed_json["execution_time"] = f"{end - start} s | {(end - start)/60} min"
        return parsed_json

    def get_contact_informations(self, htmlContent):
        clean_html_text = self.pageProcessing.get_clean_html_text_from_source_page(htmlContent)
        chunks = self.sentenceProcessing.get_chunks_from_clean_html_text(clean_html_text)
        contact_informations = {}
        contact_informations["emails"] = []
        contact_informations["phones"] = []
        contact_informations["execution_times"] = []
        for chunk in chunks:
            infos = self.predict(chunk, execution_time=True)
            contact_informations["emails"] += infos["emails"]
            contact_informations["phones"] += infos["phones"]
            contact_informations["execution_times"] += [infos["execution_time"]]
        contact_informations["nb_chunks"] = len(chunks)

        context_emails = ["abdelghaffour@gmail.com", "mouhsine.abdo@usmba.ac.ma", "abdo@gmail.com"]
        context_phones = ["06 82 10 33 81", "0111 222 3333", "+971-3-4444111", "+212 682103381", "0800 788 0800"]
        
        contact_informations["emails"] = [ email for email in contact_informations["emails"] if email not in context_emails]
        contact_informations["phones"] = [ phone for phone in contact_informations["phones"] if phone not in context_phones]
        
        return contact_informations
       



