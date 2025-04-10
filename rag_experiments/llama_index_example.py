import openai
openai.api_key = "sk-CRIeTtB7ily8Tyrq577d9a2dC628484bB1C8C0B566A69200"
openai.base_url="https://oneapi.xty.app/v1"

# Load data and build an index
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

Settings.llm = OpenAI(model="gpt-4o", temperature=0)

documents = SimpleDirectoryReader("example_data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Query data
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)

# Viewing Queries and Events Using Logging
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# store the index
index.storage_context.persist(persist_dir="example")