
import json
from pathlib import Path
from database import db

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

DATASET_DIR = Path(__file__).resolve().parent / "dataset"

FILES = {
    "BNS 2023": DATASET_DIR / "BNS.json",
    "BNSS 2023": DATASET_DIR / "BNSS.json",
    "BSA 2023": DATASET_DIR / "BSA.json",
}

BATCH_SIZE = 500


# ---------------------------------------
# LOAD JSON FILE
# Supports:
# 1. Normal JSON arrays
# 2. A single JSON object
# 3. Multiple comma-separated JSON objects
# 4. JSONL-style records
# ---------------------------------------

def load_json_records(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw = file_path.read_text(encoding="utf-8").strip()

    if not raw:
        raise ValueError(f"File is empty: {file_path.name}")

    try:
        data = json.loads(raw)

        if isinstance(data, dict):
            return [data]

        if isinstance(data, list):
            return data

        raise ValueError("JSON must contain an object or array.")

    except json.JSONDecodeError:
        # Handle comma-separated objects without [ ]
        decoder = json.JSONDecoder()
        records = []
        position = 0

        while position < len(raw):
            # Skip whitespace, commas and outer array brackets
            while position < len(raw) and raw[position] in " \t\r\n,[]":
                position += 1

            if position >= len(raw):
                break

            record, position = decoder.raw_decode(raw, position)

            if isinstance(record, dict):
                records.append(record)
            elif isinstance(record, list):
                records.extend(record)
            else:
                raise ValueError("Unexpected JSON record type.")

        return records


# ---------------------------------------
# CREATE NEO4J CONSTRAINTS
# ---------------------------------------

def create_constraints():

    queries = [
        """
        CREATE CONSTRAINT act_name_unique IF NOT EXISTS
        FOR (a:Act)
        REQUIRE a.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT chapter_identity_unique IF NOT EXISTS
        FOR (c:Chapter)
        REQUIRE (c.act_name, c.name) IS UNIQUE
        """,

        """
        CREATE CONSTRAINT section_identity_unique IF NOT EXISTS
        FOR (s:Section)
        REQUIRE (s.act_name, s.section_number) IS UNIQUE
        """
    ]

    for query in queries:
        db.query(query)

    print("Neo4j constraints created/verified.")


# ---------------------------------------
# IMPORT A BATCH INTO NEO4J
# ---------------------------------------

def import_batch(records):

    query = """
    UNWIND $records AS record

    MERGE (a:Act {
        name: record.act
    })

    MERGE (c:Chapter {
        act_name: record.act,
        name: record.chapter
    })

    MERGE (a)-[:HAS_CHAPTER]->(c)

    MERGE (s:Section {
        act_name: record.act,
        section_number: record.section_number
    })

    SET s.chunk_id = record.chunk_id,
        s.title = record.section_title,
        s.text = record.text,
        s.source_label = record.source_label

    MERGE (c)-[:HAS_SECTION]->(s)
    """

    db.query(query, {"records": records})


# ---------------------------------------
# VALIDATE RECORDS
# ---------------------------------------

def validate_records(records, file_name):

    required_fields = [
        "chunk_id",
        "text",
        "section_number",
        "section_title",
        "chapter",
        "act",
        "source_label"
    ]

    for index, record in enumerate(records):

        missing = [
            field for field in required_fields
            if field not in record or record[field] is None
        ]

        if missing:
            raise ValueError(
                f"{file_name}: Record {index} is missing {missing}"
            )

        # Check that the record belongs to the expected Act
        expected_act = {
            "BNS.json": "BNS 2023",
            "BNSS.json": "BNSS 2023",
            "BSA.json": "BSA 2023"
        }[file_name]

        if record["act"] != expected_act:
            raise ValueError(
                f"{file_name}: Unexpected act name "
                f"'{record['act']}' in record {index}"
            )


# ---------------------------------------
# PROCESS EACH DATASET IN BATCHES
# ---------------------------------------

def import_dataset(act_name, file_path):

    print(f"\nImporting {act_name}...")

    records = load_json_records(file_path)

    if not records:
        print(f"No records found in {file_path.name}")
        return

    validate_records(records, file_path.name)

    total = len(records)

    print(f"Total records: {total}")

    for start in range(0, total, BATCH_SIZE):

        batch = records[start:start + BATCH_SIZE]

        import_batch(batch)

        completed = min(start + BATCH_SIZE, total)

        print(f"Imported {completed}/{total} sections")

    print(f"{act_name} import completed.")


# ---------------------------------------
# VERIFY GRAPH
# ---------------------------------------

def show_graph_summary():

    query = """
    MATCH (a:Act)
    OPTIONAL MATCH (a)-[:HAS_CHAPTER]->(c:Chapter)
    OPTIONAL MATCH (c)-[:HAS_SECTION]->(s:Section)

    RETURN
        a.name AS act,
        count(DISTINCT c) AS chapters,
        count(DISTINCT s) AS sections

    ORDER BY act
    """

    results = db.query(query)

    print("\n========== GRAPH SUMMARY ==========")

    for result in results:
        print(result)

    print("===================================")


# ---------------------------------------
# MAIN
# ---------------------------------------

def main():

    try:
        create_constraints()

        for act_name, file_path in FILES.items():
            import_dataset(act_name, file_path)

        show_graph_summary()

        print("\nAll legal datasets imported successfully!")

    except Exception as error:
        print("\nIMPORT FAILED:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
