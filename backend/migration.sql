CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE candidates
ADD COLUMN embedding vector(1536);

CREATE INDEX candidate_embedding_idx
ON candidates
USING ivfflat (embedding vector_cosine_ops);