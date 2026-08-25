import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jConnection:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j AuraDB!")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, cypher_query: str, parameters: dict = None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result]

    def get_schema(self):
        """Fetches node labels and relationship types to understand graph structure."""
        labels_query = "CALL db.labels()"
        relationships_query = "CALL db.relationshipTypes()"
        
        labels = self.query(labels_query)
        relationships = self.query(relationships_query)
        
        return {
            "node_labels": [list(item.values())[0] for item in labels],
            "relationship_types": [list(item.values())[0] for item in relationships]
        }

# Singleton instance for easy import across modules
db = Neo4jConnection()

if __name__ == "__main__":
    # Test script execution
    print("Testing connection and fetching graph schema...")
    schema = db.get_schema()
    print("Graph Schema:", schema)