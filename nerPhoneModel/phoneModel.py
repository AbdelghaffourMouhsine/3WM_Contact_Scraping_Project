import torch
from transformers import (
    AutoModelForTokenClassification,
    BertTokenizer)

from nerPhoneModel.buildCustomData import BuildCustomData

class PhoneModel:
    def __init__(self):
        self.model_path = "./nerPhoneModel/models/fine_tuned_ner_model_for_phone_numbers_12_1500_max_len_webIemData_50_epochs"
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_path)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
        self.max_len = self.model.config.max_position_embeddings
        self.max_phone_len = 8
        self.buildCustomData = BuildCustomData()
        
    def contains_letters(self, word):
        return any(char.isalpha() for char in word)
    
    def contains_numbers(self, word):
        return any(char.isdigit() for char in word)
        
    def count_numbers(self, word):
        i=0
        for char in word:
            if char.isdigit():
                i += 1
        return i
        
    def predict(self, sentence):
        # Tokenization de la phrase
        input_data = self.tokenizer.encode_plus(
                    sentence,
                    add_special_tokens=True,
                    # return_token_type_ids=False,
                    truncation=True,
                    max_length= self.max_len,
                    padding="max_length",
                    return_tensors="pt"
                )
        
        # Passer les données au modèle pour obtenir les étiquettes
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_data["input_ids"],
                attention_mask=input_data["attention_mask"]
            )
        
        # Obtenir les prédictions des étiquettes
        predicted_labels = torch.argmax(outputs.logits, dim=2).squeeze().tolist()
        
        # Transformer les indices en étiquettes
        index_to_label = {0: "O", 1: "B-PHONE", 2: "I-PHONE"}
        predicted_labels_named = [index_to_label[label] for label in predicted_labels]
        
        # Extraire les tokens
        tokens = self.tokenizer.convert_ids_to_tokens(input_data["input_ids"].squeeze())
        phone_numbers = self.extract_phones(tokens,predicted_labels_named)
        return phone_numbers
        
    def extract_phones(self, tokens, predicted_labels_named):
        # Reconstituer les entités de type téléphone
        phone_numbers = []
        current_number = []
        last_type = None
        
        for token, label in zip(tokens, predicted_labels_named):
            # Fusion des sous-mots sans espace pour maintenir la cohérence des numéros de téléphone
            token = token.replace("#", "")
            token = token.replace("[CLS]", "")
            token = token.replace("[SEP]", "")
            clean_token = token.replace("[PAD]", "")
            
            if label == "B-PHONE" :
                if current_number and self.count_numbers("".join(current_number)) > self.max_phone_len: # New number coming
                    phone_numbers.append("".join(current_number))
                    current_number = []
                    if len(clean_token) > 0 :
                        current_number.append(clean_token)
                elif current_number and last_type == "digit": # new digit in the same number
                    if len(clean_token) > 0 :
                        current_number.append(clean_token)
                else:                                         # 
                    if len(clean_token) > 0 :
                        current_number= [clean_token]
                last_type = "digit"
                
            elif label == "I-PHONE":
                if len(clean_token) > 0 :
                    current_number.append(clean_token)
                    last_type = "digit"
                    
            elif current_number and not self.contains_letters(clean_token) and last_type == "digit":  # if label == 'O'
                if len(clean_token) > 0 :
                        current_number.append(clean_token)
            elif current_number:
                phone_numbers.append("".join(current_number))
                current_number = []
                last_type = "alpha"
                
            if self.contains_letters(clean_token):
                last_type = "alpha"
                
        # Ajouter le dernier numéro s'il existe
        if current_number:
            phone_numbers.append("".join(current_number))
        
        return [phone for phone in phone_numbers if self.count_numbers(phone) > self.max_phone_len]

    def get_phone_numbers(self, htmlContent):
        chunks = self.buildCustomData.extract_chunks(htmlContent)
        phones = []
        for chunk in chunks:
            new_sentence = self.buildCustomData.input_sentence_processing(chunk)
            predicted_phones = self.predict(new_sentence)
            phones = phones + predicted_phones
        return list(set(phones))