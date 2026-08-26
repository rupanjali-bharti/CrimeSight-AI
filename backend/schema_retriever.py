import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SchemaRetriever:
    def __init__(self, catalog_path: str = "schema_catalog.json"):
        if not os.path.exists(catalog_path):
            raise FileNotFoundError(f"{catalog_path} not found. Run extract_schema.py first.")
            
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
            
        self.descriptions = [item["search_text"] for item in self.catalog]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.descriptions)

    def get_relevant_schema(self, query: str, top_k: int = 8) -> str:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        
        top_indices = scores.argsort()[-top_k:][::-1]
        
        selected_lines = set()
        for idx in top_indices:
            selected_lines.add(self.catalog[idx]["schema_line"])
            
        # Fallback default core relationships if query is too brief
        selected_lines.add("Entity -[:COVERS_OFFENCE]-> Entity")
        selected_lines.add("Entity -[:PROTECTS_AGAINST]-> Entity")
        
        relationships_block = "\n".join(sorted(list(selected_lines)))
        
        dynamic_schema = f"""
Node properties:
Entity {{name: STRING, type: STRING, section: STRING, reference: STRING, value_limit: STRING}}

Relationship properties:
{relationships_block}
"""
        return dynamic_schema.strip()

# Singleton instance
schema_retriever = SchemaRetriever()