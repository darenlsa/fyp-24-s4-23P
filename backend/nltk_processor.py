import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

def process_message(message):
    # Tokenize the message and remove stopwords
    tokens = word_tokenize(message.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stopwords.words('english')]
    return " ".join(filtered_tokens)
