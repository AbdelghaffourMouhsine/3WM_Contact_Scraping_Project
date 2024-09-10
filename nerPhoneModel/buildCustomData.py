from bs4 import BeautifulSoup

class BuildCustomData:
    def __init__(self):
        self.MIN_LENGTH_PHONE = 8
        
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
        
    def word_process(self, word):
        new_word = ""
        if self.contains_letters(word) or (not self.contains_numbers(word)):
            if word[0].isdigit():
                last_type = "digit"
            elif word[0].isalpha():
                last_type = "alpha"
            else:
                last_type = "other"
                
            for char in word:
                if (char.isdigit() and last_type == "digit") or (char.isalpha() and last_type == "alpha"): # the same type
                    new_word += char
                elif char.isdigit() and last_type != "digit":
                    new_word += " " + char
                    last_type = "digit"
                elif char.isalpha() and last_type != "alpha":
                    new_word += " " + char
                    last_type = "alpha"
                elif last_type == "other" and (char not in [":",",","،","."]):
                    new_word += char
                elif last_type == "alpha" and (char not in [":",",","،","."]):
                    new_word += " " + char
                    last_type = "other"
                elif last_type == "digit" :
                    new_word += char
                    last_type = "other"
        else:
            new_word = word
        return new_word.strip()
        
    def sentence_process(self, sentence) :
        words = sentence.split(' ')
        new_words = []
        for word in words:
            if word !="":
                new_word = self.word_process(word)
                if new_word != '':
                    for wrd in new_word.split(' '):
                        new_words.append(wrd)
            
        new_sentence = ""
        for index, word in enumerate(new_words):
            if not self.contains_letters(word):  # word = number or [+ ( ) - . , ...]
                if len(new_sentence) > 0 :
                    if self.contains_letters(new_sentence.split(' ')[-1]) : # or (not self.contains_numbers(new_sentence.split(' ')[-1])) or (not self.contains_numbers(word))
                        new_sentence += " "+word
                    elif self.contains_numbers(new_sentence.split(' ')[-1]) and self.count_numbers(new_sentence.split(' ')[-1]) > self.MIN_LENGTH_PHONE and self.count_numbers(word) > self.MIN_LENGTH_PHONE :
                        new_sentence += " "+word
                    else:
                        new_sentence += word
                else:
                    new_sentence += word
            else :
                if len(new_sentence) > 0 :
                    new_sentence += " "+word
                else :
                    new_sentence += word
        
        return new_sentence.strip()
        
    def phone_process_sentence(self, sentence):
        words = sentence.split(' ')
        new_sentence = ""
        for word in words:
            new_word = word
            if(self.contains_numbers(word) and len(word) > self.MIN_LENGTH_PHONE): # if word is a phone number
                separators = list(set([char for char in word if not char.isdigit()]))
                separators_min_len_elems = {}
                for sep in separators:
                    liste_elems = [elem for elem in word.split(sep) if elem.strip() != ""]
                    liste_len_elems = [self.count_numbers(elem) for elem in liste_elems]
                    test_result = all([l > self.MIN_LENGTH_PHONE for l in liste_len_elems]) and len(liste_len_elems)>1
                    
                    if test_result:
                        separators_min_len_elems[sep] = min(liste_len_elems)
                
                if len(separators_min_len_elems) > 0:
                    sep_has_max_min_len_elems = max(separators_min_len_elems, key=separators_min_len_elems.get)
                    new_word = f" {sep_has_max_min_len_elems} ".join([elem for elem in word.split(sep_has_max_min_len_elems) if elem.strip() != ""])
            
            new_sentence +=  " " + new_word
        return new_sentence.strip()
        
    def get_label_sentence(self, sentence) :
        words = sentence.split(' ')
        labels = []
        for word in words :
            if self.contains_numbers(word) and ( not self.contains_letters(word)):
                if self.count_numbers(word) > self.MIN_LENGTH_PHONE:
                    if len([c for c in word if c == '/']) != 2 and len(set([c for c in word if c.isdigit()])) > 2: # not a date & have more than 2 number type
                        label = 'PHONE'
                    else:
                        label = 'O'
                else:
                    label = 'O'
            else :
                label = 'O'
            labels.append(label)
        return labels

    def clean_phone(self, phone_number):
        start_index = -1;
        end_index = -1
        len_phone = len(phone_number)
        for i, char in enumerate(phone_number):
            if ( char.isdigit() or char in ["+","(","-"] ) and start_index == -1:
                start_index = i
                
            if ( phone_number[len_phone-1 - i].isdigit() or phone_number[len_phone-1 - i] == ")" ) and end_index == -1:
                end_index = len_phone - i
                
            if start_index != -1 and end_index != -1:
                break
        return phone_number[start_index:end_index]
        
    def get_items(self, row, column_sentence_name = "phrases") :   
        sentence_id = row['id']
        sentence = row[column_sentence_name]
        process_sentence = self.sentence_process(sentence)
        process_sentence = self.phone_process_sentence(process_sentence)
        label_sentence = self.get_label_sentence(process_sentence)
        sentence_split = process_sentence.split()
    
        items = []
    
        for word, label in zip(sentence_split, label_sentence):
            if label == "PHONE":
                word = self.clean_phone(word)
            word_info = {
                'sentence_id': sentence_id,
                'word': word.strip(),
                'label': label
            }
            items.append(word_info)
        
        return items

    def filter_items(self, items):
        return [item for item in items if self.contains_numbers(item["word"]) or self.contains_letters(item["word"])]
        
    def update_label(self, file_name, new_label, row_index):
        df = pd.read_csv(file_name)
        if row_index < 0 or row_index >= len(df):
            print("L'indice de ligne est invalide.")
        df.loc[row_index, 'label'] = new_label
        if new_label == "PHONE":
            word = df.loc[row_index, 'word']
            word = self.clean_phone(word)
            df.loc[row_index, 'word'] = word
        df.to_csv(file_name, index=False)
        print("La valeur de 'label' a été mise à jour avec succès.")
        
    def input_sentence_processing(self, sentence):
        process_sentence = self.sentence_process(sentence)
        process_sentence = self.phone_process_sentence(process_sentence)
        words = process_sentence.split()
        new_words = []
        for word in words:
            if self.count_numbers(word) > self.MIN_LENGTH_PHONE:
                word = self.clean_phone(word)
            if self.contains_numbers(word) or self.contains_letters(word):
                new_words.append(word)
        
        return " ".join(new_words)

    def extract_chunks(self, contenu_html, max_len_chunk = 300, pad = 10):
        soup = BeautifulSoup(contenu_html, 'html.parser')
        text = soup.text
        new_text = ' '.join([n.strip() for n in text.split('\n') if n != ''])
        text_list = new_text.split()
        len_text_list = len(text_list)
        n_chunks= int(len_text_list / max_len_chunk)+1
        
        chunks = []
        for i in range(n_chunks):
            if i == 0:
                start = i*max_len_chunk
                end = min((i+1)*max_len_chunk,len_text_list)
            else:
                start = end - pad
                end = min(((i+1)*max_len_chunk) - pad , len_text_list)
                
            chunk = text_list[start:end]
            chunks.append(' '.join(chunk))
            
            if i == n_chunks-1 and end != len_text_list and len(chunk)==max_len_chunk:
                start = end - pad
                end = len_text_list
                chunk = text_list[start:end]
                chunks.append(' '.join(chunk))
        return chunks