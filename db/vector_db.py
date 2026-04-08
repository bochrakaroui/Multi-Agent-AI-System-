import chromadb
from chromadb.utils import embedding_functions
import uuid


#saves sata to disk in a  file called chroma_data
chroma_client = chromadb.PersistentClient(path='./chroma_data')

#uses all-MiniLM-L6-v2 model for embeddings by default
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name='fitness_notes',
    embedding_function=embedding_fn,
    metadata={'hnsw:space': 'cosine'}  # Cosine similarity for text
)


def add_note_to_vector_store(note_id: str, user_id: str, content: str,
                              category: str = 'general'):
    collection.add(
        ids=[note_id],
        documents=[content],
        metadatas=[{
            'user_id': user_id,
            'category': category
        }]
    )

#returns the text content of the 4 most relevant notes 
def search_notes(user_id: str, query: str, n_results: int = 2) -> list[str]:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={'user_id': user_id}  # Filter by user
        )
        # Return just the text content
        return results['documents'][0] if results['documents'] else []
    except Exception:
        # Returns empty list if no notes exist yet for this user
        return []

def delete_note_from_vector_store(note_id: str):
    try:
        collection.delete(ids=[note_id])
    except Exception:
        pass  # Note might not exist, ignore errors

def get_note_count(user_id: str) -> int:
    """Return the total number of notes stored for a specific user."""
    try:
        results = collection.get(where={'user_id': user_id})
        return len(results['ids'])
    except Exception:
        return 0

if __name__ == '__main__':
    # Add some test notes
    add_note_to_vector_store('n1', 'user-001', 'Did 5x5 squats at 100kg. Left knee felt a little sore.')
    add_note_to_vector_store('n2', 'user-001', 'Ate 180g of chicken breast with rice for lunch.')
    add_note_to_vector_store('n3', 'user-001', 'Slept 7 hours. Feeling well rested today.')
    add_note_to_vector_store('n4', 'user-001', 'Ran 5km in 28 minutes. Cardio felt easy.')

    # Search semantically
    results = search_notes('user-001', 'joint pain or injury')
    print('Search results for joint pain:')
    for r in results:
        print(' -', r)
