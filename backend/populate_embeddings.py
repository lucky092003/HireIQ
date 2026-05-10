"""
Seed embeddings script - Populate candidate embeddings in PostgreSQL
Run this after seeding candidates table with sample data
"""

import os
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
)


def get_embedding(text: str) -> list:
    """Generate embedding for text using OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def populate_embeddings():
    """Fetch all candidates and populate their embeddings"""
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # Get all candidates without embeddings
    cur.execute("SELECT id, name, title, skills FROM candidates WHERE embedding IS NULL")
    candidates = cur.fetchall()
    
    print(f"Found {len(candidates)} candidates without embeddings")
    
    for idx, (cid, name, title, skills) in enumerate(candidates):
        # Combine all text fields for embedding
        text_to_embed = f"{name} {title} {skills}"
        
        # Get embedding
        embedding = get_embedding(text_to_embed)
        
        # Update database
        cur.execute(
            "UPDATE candidates SET embedding = %s WHERE id = %s",
            (embedding, cid)
        )
        conn.commit()
        
        print(f"[{idx + 1}/{len(candidates)}] Embedded: {name}")
    
    cur.close()
    conn.close()
    
    print("\n✅ All candidates embeddings populated successfully!")


if __name__ == "__main__":
    populate_embeddings()
