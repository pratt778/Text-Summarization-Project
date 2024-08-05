import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict


class AdvancedTextRankSummarizer:
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_text(self, text):
        sentences = sent_tokenize(text)
        cleaned_sentences = []
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            pos_tags = nltk.pos_tag(words)
            words = [self.lemmatizer.lemmatize(word) for word, pos in pos_tags 
                     if word.isalnum() and word not in self.stop_words and pos in {'NN', 'JJ', 'NNP'}]
            cleaned_sentences.append(words)
        
        return sentences, cleaned_sentences

    def calculate_similarity(self, sent1, sent2):
        tfidf = TfidfVectorizer().fit_transform([' '.join(sent1), ' '.join(sent2)])
        cosine_sim = (tfidf * tfidf.T).toarray()[0, 1]
        return cosine_sim

    def build_similarity_matrix(self, cleaned_sentences):
        n = len(cleaned_sentences)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self.calculate_similarity(cleaned_sentences[i], cleaned_sentences[j])
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
        
        return similarity_matrix

    def textrank(self, similarity_matrix, eps=1e-8, max_iter=100, damping_factor=0.85):
        n = len(similarity_matrix)
        p = np.ones(n) / n
        
        for _ in range(max_iter):
            prev_p = p.copy()
            for i in range(n):
                summation = np.sum(similarity_matrix[i] * prev_p / (np.sum(similarity_matrix, axis=1) + eps))
                p[i] = (1 - damping_factor) / n + damping_factor * summation
            
            if np.sum(np.abs(p - prev_p)) < eps:
                break
        
        return p

    def extract_top_sentences(self, sentences, scores, num_sentences):
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return [s for _, s in ranked_sentences[:num_sentences]]

    def keyword_extraction(self, cleaned_sentences, scores, num_keywords=5):
        word_scores = defaultdict(float)
        for i, sentence in enumerate(cleaned_sentences):
            for word in sentence:
                word_scores[word] += scores[i]
        
        return sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:num_keywords]

    def summarize(self, text, num_sentences=3, num_keywords=5):
        original_sentences, cleaned_sentences = self.preprocess_text(text)
        similarity_matrix = self.build_similarity_matrix(cleaned_sentences)
        scores = self.textrank(similarity_matrix)
        
        summary = self.extract_top_sentences(original_sentences, scores, num_sentences)
        keywords = self.keyword_extraction(cleaned_sentences, scores, num_keywords)
        
        return ' '.join(summary), [word for word, _ in keywords]