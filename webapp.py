# importing the dependencies
import string
import math
import spacy
from flask import Flask, render_template, request

# NLP Model
nlp = spacy.load('en_core_web_sm')
# Stop Words
STOP_WORDS = nlp.Defaults.stop_words

# defining a class for the extraction based text summarization
class Summary:
    def __init__(self, text):
        '''basic class variables'''
        self.text = text
        self.words = self.get_words()
        self.len_orig = len(self.words)
        self.freq_dict = self.get_freq_dict()
        self.original_sents = self.get_sents()
        self.sent_score = self.get_sent_score()
        self.summary = self.get_summary()
        self.summ_len = self.get_summary_len()

    def get_words(self):
        '''word tokenzation'''
        doc = nlp(self.text)
        words = [x for x in doc]
        return words
    
    def get_freq_dict(self):
        '''frequency of the each words'''
        freq_dict = {}
        doc = nlp(self.text)
        words = [x.lemma_.lower() for x in doc if x.text.lower() not in string.punctuation and x.text.lower() not in STOP_WORDS]
        for x in words:
            if x not in freq_dict:
                freq_dict[x] = 1
            elif x in freq_dict:
                freq_dict [x] += 1
            else:
                pass
        max_freq = max(freq_dict.values())
        freq_dict = {word: freq/max_freq for word, freq in freq_dict.items()}
        return freq_dict
    
    def get_sents(self):
        '''sentence tokenization'''
        doc = nlp(self.text)
        original_sents = [x for x in doc.sents]
        return original_sents

    def get_sent_score(self):
        '''getting the sentence score'''
        processed_sents = []
        for sent in self.original_sents:
            new_sent = [word.lemma_.lower() for word in sent if word.text.lower() not in string.punctuation and word.text.lower() not in STOP_WORDS]
            processed_sents.append(new_sent)
        sent_score = {}
        for i in range(len(self.original_sents)):
            sent_score[self.original_sents[i]] = 0
            for word in processed_sents[i]:
                if word in self.freq_dict:
                    sent_score[self.original_sents[i]] += self.freq_dict[word] 
        sent_score = {sent: score for sent, score in sorted(sent_score.items(), key=lambda item: item[1], reverse=True)}
        return sent_score 
    
    def get_summary(self):
        '''getting the actual summary'''
        n_word_summ = math.floor(self.len_orig * 0.3)
        summary_sents = []
        for sent in self.sent_score.keys():
            summary_sents.append(sent)
            temp_summ = nlp(' '.join([x.text for x in summary_sents]))
            word_count = len([x for x in temp_summ])
            if word_count >= n_word_summ:
                break 
        idx = [self.original_sents.index(sent) for sent in summary_sents]
        sorted_idx = sorted(idx)
        final_summary_sents = [self.original_sents[idx].text for idx in sorted_idx]
        summary = ' '.join(final_summary_sents)
        return summary
    
    def get_summary_len(self):
        '''getting the summary length'''
        doc = nlp(self.summary)
        summ_len = len([x for x in doc])
        return(summ_len)

# defining the flask app
app = Flask(__name__)

# flask routs 
@app.route('/', methods=['GET', 'POST'])
def index():
    text = None
    text_len = None
    summ = None
    summ_len = None
    reduction_perc = None
    if request.method == 'POST':
        text_obj = Summary(request.form.get('text'))
        text = text_obj.text.split('\r\n')
        text_len = text_obj.len_orig
        summ = text_obj.summary.replace('\r\n', ' ')
        summ_len = text_obj.summ_len
        reduction_perc = round((text_len-summ_len)*100/text_len)
    return render_template("index.html", 
                           text=text,
                           text_len=text_len,
                           summ=summ,
                           summ_len=summ_len, 
                           red_perc=reduction_perc)

# running the app 
if __name__ == '__main__':
    app.run(debug=True)