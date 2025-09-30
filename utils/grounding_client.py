import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_grounding_model():
    """Loads and caches the HuggingFace text-classification pipeline."""
    return pipeline("text-classification", model="dejanseo/query-grounding", top_k=None)

class GroundingModel:
    def __init__(self):
        self.classifier = load_grounding_model()

    def analyze_queries(self, queries: list) -> list:
        """Analyses a list of queries and returns their grounding scores."""
        scores = []
        model_outputs = self.classifier(queries)
        for output in model_outputs:
            grounding_score = 0.0
            for label in output:
                if label['label'] == 'grounded' or label['label'] == 'LABEL_1':
                    grounding_score = label['score']
                    break
            scores.append(grounding_score * 100)
        return scores
