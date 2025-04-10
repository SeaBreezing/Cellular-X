import os
import json
import openai
openai.api_key = "your_api_key"
openai.base_url="your_url"
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
parser.add_argument('-k', type=int, help='top_k', required=True)
parser.add_argument('-w', type=int, help='chunk size', required=True)
parser.add_argument('-m', '--model', type=str, help='model for query', required=True)
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
    prompt = "Select the correct option for the question in JSON format below:\n"
    prompt += question_prompt+'\n'
    rag_results = query_index(prompt, K)
    # prompt += "You are provided with related document information as follows:\n"
    # for i, result in enumerate(rag_results):
    #     prompt += f"Information {i+1}: "+result.text+"\n"
    prompt += "Only answer the 'option_?' in plaintext without single quotation marks, where ? is the index of the option you choose. Do not add any additional explanation."
    response = client.chat.completions.create(
        model = model,
        messages = [{'role': 'user', 'content': prompt}]
    )
    if not os.path.exists("experiments"):
        os.mkdir("experiments")
    response = response.choices[0].message.content.strip()
    with open(f"experiments/answers_W{W}_K{K}_{model}.txt", "a+") as f:
        f.write(f"question_{question_idx} answer: {response}\n")
    return response

def evaluate_questions(model):
    # clear former answers and stats
    if os.path.exists(f"experiments/answers_W{W}_K{K}_{model}.txt"):
        os.system(f"rm experiments/answers_W{W}_K{K}_{model}.txt")
    if os.path.exists(f"experiments/stats_W{W}_K{K}_{model}.txt"):
        os.system(f"rm experiments/stats_W{W}_K{K}_{model}.txt")

    # Load the JSON file
    with open("Q-small/Sampled_3GPP_TR_Questions.json", 'r') as file:
        questions_data = json.load(file)
    
    # Initialize counters
    correct_counts = {"Easy": 0, "Intermediate": 0, "Hard": 0}
    total_counts = {"Easy": 0, "Intermediate": 0, "Hard": 0}
    
    qna_keys = ['question', 'option_1', 'option_2', 'option_3', 'option_4']
    # Iterate through each question
    for question_idx, (question_id, question_info) in tqdm.tqdm(enumerate(questions_data.items())):
        question_and_options = { k: v for k, v in question_info.items() if k in qna_keys}
        question_and_options = str(question_and_options)
        correct_answer = question_info['answer'].split(':')[0]  # Extract the answer text
        difficulty = question_info['difficulty']
        
        returned_answer = query(question_idx, question_and_options, model=model)
        is_correct = returned_answer.lower() == correct_answer.lower()
        
        total_counts[difficulty] += 1
        if is_correct:
            correct_counts[difficulty] += 1
    
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