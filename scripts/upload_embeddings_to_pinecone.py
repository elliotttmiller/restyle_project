import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import django
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
django.setup()

from backend.core.models import ItemEmbedding

# Pinecone config from environment
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX = os.environ["PINECONE_INDEX_NAME"]

# Initialize Pinecone (new client)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# Batch upserts for efficiency
BATCH_SIZE = 100

# Collect all embeddings and metadata
embeddings = ItemEmbedding.objects.select_related('item').all()

print(f"[DEBUG] Pinecone index: {PINECONE_INDEX}")
print(f"[DEBUG] Total embeddings found: {embeddings.count()}")

vectors = []
for emb in embeddings:
    item = emb.item
    # Prepare metadata (customize as needed)
    metadata = {
        "item_id": item.id,
        "title": item.title,
        "brand": getattr(item, 'brand', None),
        "category": getattr(item, 'category', None),
        "color": getattr(item, 'color', None),
        "size": getattr(item, 'size', None),
        "sku": getattr(item, 'sku', None),
        "is_sold": getattr(item, 'is_sold', None),
        "created_at": str(item.created_at) if hasattr(item, 'created_at') else None,
        "updated_at": str(item.updated_at) if hasattr(item, 'updated_at') else None,
    }
    # Pinecone expects (id, vector, metadata)
    vector_tuple = (str(item.id), list(emb.embedding), metadata)
    vectors.append(vector_tuple)

    # Upsert in batches
    if len(vectors) >= BATCH_SIZE:
        print(f"[DEBUG] Upserting batch of {len(vectors)} vectors...")
        print(f"[DEBUG] Sample vector: {vectors[0]}")
        response = index.upsert(vectors)
        print(f"[DEBUG] Upsert response: {response}")
        vectors = []

# Upsert any remaining vectors
if vectors:
    print(f"[DEBUG] Upserting final batch of {len(vectors)} vectors...")
    print(f"[DEBUG] Sample vector: {vectors[0]}")
    response = index.upsert(vectors)
    print(f"[DEBUG] Upsert response: {response}")

print("✅ All embeddings uploaded to Pinecone!") 