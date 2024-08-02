import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import networkx as nx

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words('english'))
    
    def clean_sentence(sentence):
        words = word_tokenize(sentence.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        return ' '.join(words)
    
    cleaned_sentences = [clean_sentence(sentence) for sentence in sentences]
    return sentences, cleaned_sentences

def build_similarity_matrix(sentences):
    vectorizer = CountVectorizer().fit_transform(sentences)
    vectors = vectorizer.toarray()
    similarity_matrix = cosine_similarity(vectors)
    return similarity_matrix

def rank_sentences(similarity_matrix):
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((score, idx) for idx, score in scores.items()), reverse=True)
    return ranked_sentences

def generate_summary(text, num_sentences=5):
    sentences, cleaned_sentences = preprocess_text(text)
    similarity_matrix = build_similarity_matrix(cleaned_sentences)
    ranked_sentences = rank_sentences(similarity_matrix)
    
    summary_sentences = sorted(ranked_sentences[:num_sentences], key=lambda x: x[1])
    summary = ' '.join([sentences[idx] for _, idx in summary_sentences])
    print(summary)
    return summary
