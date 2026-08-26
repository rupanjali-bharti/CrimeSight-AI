import json
from database import db

def extract_database_schema():
    print("Extracting distinct relationship types and sample connections...")
    
    query = """
    MATCH (n:Entity)-[r]->(m:Entity)
    RETURN DISTINCT type(r) AS rel_type, 
           n.type AS source_type, 
           m.type AS target_type
    """
    
    results = db.query(query)
    
    schema_records = []
    for row in results:
        rel_type = row["rel_type"]
        src = row.get("source_type") or "Entity"
        tgt = row.get("target_type") or "Entity"
        
        # Build a natural language descriptor for semantic search
        readable_rel = rel_type.replace("_", " ").lower()
        description = f"Entity of type {src} {readable_rel} Entity of type {tgt} (Cypher: (:{src})-[:{rel_type}]->(:{tgt}))"
        
        schema_records.append({
            "rel_type": rel_type,
            "schema_line": f"Entity -[:{rel_type}]-> Entity",
            "search_text": description
        })
    
    with open("schema_catalog.json", "w", encoding="utf-8") as f:
        json.dump(schema_records, f, indent=2)
        
    print(f"Extracted {len(schema_records)} distinct schema patterns to schema_catalog.json")

if __name__ == "__main__":
    extract_database_schema()