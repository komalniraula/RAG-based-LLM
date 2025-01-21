import os
from dotenv import load_dotenv
import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
from groq import Groq
import torch

# Load the environment variables from the .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load embeddings and models
load_directory = "./Embeddings - gte-large-en-v1.5"
EMBEDDING_MATRIX = np.load(f'{load_directory}/embeddings.npy')
print("Embedding matrix shape:", EMBEDDING_MATRIX.shape)

with open(f'{load_directory}/splits.npy', 'rb') as f:
    SPLITS = np.load(f, allow_pickle=True)
print("Splits loaded from disk.")

INDEX = faiss.read_index(f'{load_directory}/faiss_index.index')
print("Faiss index loaded from disk.")

load_directory = "./saved_embedding_model"
TOKENIZER = AutoTokenizer.from_pretrained(load_directory, trust_remote_code=True)
MODEL = AutoModel.from_pretrained(load_directory, trust_remote_code=True)
MODEL.eval()

groq_api_key = GROQ_API_KEY

# Function to embed queries
def embed_query(query):
    inputs = TOKENIZER(query, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embeddings = MODEL(**inputs).last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return embeddings

# Function to search the index
def search_index(query, top_k=5):
    query_embedding = embed_query(query)
    query_embedding = np.expand_dims(query_embedding, axis=0).astype('float32')
    distances, indices = INDEX.search(query_embedding, top_k)
    return [SPLITS[idx] for idx in indices[0]]

def get_response(formatted_string):
    client = Groq(api_key=groq_api_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": formatted_string}],
        model="llama3-8b-8192",
    )
    result = chat_completion.choices[0].message.content
    return result
