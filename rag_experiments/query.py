import os, json
import voice2text
import openai
openai.api_key = "your_api_key"
openai.base_url = "your_url"
client = openai.OpenAI(
    api_key = "your_api_key",
    base_url = "your_url",
)

from llama_index.llms.openai import OpenAI
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core.retrievers import VectorIndexRetriever

import tqdm
import argparse

parser = argparse.ArgumentParser(description='Parameters for query setup: K (top_k) and W (chunk size)')
parser.add_argument('-k', type=int, help='top_k', default=4)
parser.add_argument('-w', type=int, help='chunk size', default=1024)
parser.add_argument('-m', '--model', type=str, help='model for query', default="gpt-4")
args = parser.parse_args()

W = args.w
K = args.k

# load embed model and index
embed_model = OpenAIEmbedding(mode="similarity", model="text-embedding-ada-002")
index = load_index_from_storage(StorageContext.from_defaults(persist_dir=f"./3GPP-index_{W}"))

def query_index(prompt: str, top_k: int = K):
    query_embedding = embed_model.get_text_embedding(prompt)
    retriever = VectorIndexRetriever(index, similarity_top_k=top_k)
    results = retriever.retrieve(prompt)
    return results

def query(question_idx: int, question_prompt: str, model) -> str:
    # prompt = "Select the correct option for the question in JSON format below:\n"
    # prompt += question_prompt+'\n'
    prompt = "Answer the question for the question below:\n"
    prompt += question_prompt+'\n'
    rag_results = query_index(prompt, K)
    # RAG 
    prompt += "You are provided with related document information as follows:\n"
    for i, result in enumerate(rag_results):
        prompt += f"Information {i+1}: "+result.text+"\n"
    prompt += "Specify the parameters I need to configurate. Do not add any additional and abstract explanation. The response should not be longer than 50 tokens."
    prompt += "let me know the article section which you use to generate questions from."
    prompt += "Below is an example"
    prompt += "question: What is the BS Tx power for UMa at 6GHz in large scale calibration?"
    prompt += "answer: 49 dBm"
    prompt += "explanation: As per Table 7.8-1 in the section provided, the BS Tx power for UMa at 6GHz is specified as 49 dBm."
    prompt += "category: 7.8.1 Large scale calibration"
    response = client.chat.completions.create(
        model = model,
        messages = [{'role': 'user', 'content': prompt}]
    )
    if not os.path.exists("experiments"):
        os.mkdir("experiments")
    response = response.choices[0].message.content.strip()
    with open(f"experiments/answers_W{W}_K{K}_{model}.txt", "a+") as f:
        f.write(f"【question_{question_idx}】{question_prompt}\n【answer】: {response}\n")
    return response

def evaluate_questions(model):
    # clear former answers and stats
    if os.path.exists(f"experiments/answers_W{W}_K{K}_{model}.txt"):
        os.system(f"rm experiments/answers_W{W}_K{K}_{model}.txt")
    if os.path.exists(f"experiments/stats_W{W}_K{K}_{model}.txt"):
        os.system(f"rm experiments/stats_W{W}_K{K}_{model}.txt")

    question_text = [voice2text.v2text("record.mp3")]
    print(f"question_text:{question_text}")
    # Initialize counters
    correct_counts = {"Easy": 0, "Intermediate": 0, "Hard": 0}
    total_counts = {"Easy": 0, "Intermediate": 0, "Hard": 0}
    
    qna_keys = ['question', 'option_1', 'option_2', 'option_3', 'option_4']
    # Iterate through each question
    for question_idx, question_info in tqdm.tqdm(enumerate(question_text)):
        
        returned_answer = query(question_idx, question_info, model=model)
        print(returned_answer)
        voice2text.t2voice(returned_answer, question_idx)
    
    # Print results
    print("Results:")
    for difficulty in ["Easy", "Intermediate", "Hard"]:
        correct = correct_counts[difficulty]
        total = total_counts[difficulty]
        percentage = (correct / total) * 100 if total > 0 else 0
        print(f"{difficulty}: {correct}/{total} ({percentage:.2f}%)")
    
    # Calculate overall accuracy
    total_correct = sum(correct_counts.values())
    total_questions = sum(total_counts.values())
    overall_accuracy = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    print(f"Overall Accuracy: {total_correct}/{total_questions} ({overall_accuracy:.2f}%)")
    with open(f"experiments/stats_W{W}_K{K}_{model}.txt", "a+") as f:
        for difficulty in ["Easy", "Intermediate", "Hard"]:
            correct = correct_counts[difficulty]
            total = total_counts[difficulty]
            percentage = (correct / total) * 100 if total > 0 else 0
            f.write(f"{difficulty}: {correct}/{total} ({percentage:.2f}%)\n")
        f.write(f"Overall Accuracy: {total_correct}/{total_questions} ({overall_accuracy:.2f}%)\n")

# query_prompt = "What is the process for determining the offset angle for ZOD in LOS conditions for RMa-AV?"
# top_k_results = query_index(query_prompt, top_k=3)

# Display results
# for result in top_k_results:
#     print("Document:", result.text)
#     print("Similarity Score:", result.score)

evaluate_questions(args.model)
