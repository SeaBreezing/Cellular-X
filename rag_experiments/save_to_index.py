# this file is used for preprocessing 3gpp documents into data chunks for RAG

import os
import time
import openai
openai.api_key = "your_api_key"
openai.base_url="your_url"

from llama_index.llms.openai import OpenAI
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter, MarkdownNodeParser

# Load data and do chunking
W = 42

# dimension of  text-embedding-ada-002 is fixed to 1536
embed_model = OpenAIEmbedding(mode="similarity", model="text-embedding-ada-002")
Settings.embed_model = embed_model
text_splitter = TokenTextSplitter(chunk_size=W, chunk_overlap=20)
# node_parser = MarkdownNodeParser(text_splitter=text_splitter)

documents = []
nodes = []
selected_files = ['36211-g80_s06-s08.md', '36101-gi0_cover.md', '36104-ge0.md', '36211-g80_s00-s05.md', '36101-gi0_sAnnexes.md', '36101-gi0_s00-07.md', '36211-g80_cover.md', '36101-gi0_s08-XX.md', '36211-g80_s09-sxx.md']
for r in range(15, 18):
    for s in range(36, 39):
        for f in selected_files:
            if not os.path.exists(f"3GPP-clean/Rel-{r}/{s}_series/{f}"):
                continue
            document = SimpleDirectoryReader(input_files=[f"3GPP-clean/Rel-{r}/{s}_series/{f}"]).load_data()
            documents += document
            print(f"Document 3GPP-clean/Rel-{r}/{s}_series/{f}: {len(document) = }")
            node = text_splitter.get_nodes_from_documents(document)
            nodes += node

print(f"Loaded {len(documents)} docs")
print(f"Parsed {len(nodes)} nodes")

# build an index
index = VectorStoreIndex(nodes, embed_model=embed_model, show_progress=True)


# store the index
index.storage_context.persist(persist_dir=f"3GPP-index_{W}")
print("Saved to path:", os.path.abspath(f"3GPP-index_{W}"))