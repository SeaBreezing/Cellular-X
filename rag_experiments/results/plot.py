import re
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the file names based on the given directory layout
file_names = [
    f"stats_W{w}_K{k}_{model}.txt" for w in ['1024', '2048'] for k in range(2, 5) for model in ['gpt-3.5-turbo', 'gpt-4']
] + [
    f"stats_trivial_{model}.txt" for model in ['gpt-3.5-turbo', 'gpt-4']
] + ["stats_reported model.txt"]
xlabel_names = [file_name[6:][:-4].replace('_', ', ') for file_name in file_names]

# Initialize dictionaries to store the accuracies
overall_accuracies = {}
detailed_accuracies = {}

# Regular expression to extract accuracy percentages
accuracy_pattern = re.compile(r"(\d+\.\d+)%")

# Read each file and extract accuracies
for file_name in file_names:
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            content = file.read()
            key_name = file_name[6:][:-4].replace('_', ', ')
            
            # Extract overall accuracy
            overall_accuracy = accuracy_pattern.findall(content.split("Overall Accuracy:")[1])[0]
            overall_accuracies[key_name] = float(overall_accuracy)
            
            # Extract detailed accuracies
            easy_accuracy = accuracy_pattern.findall(content.split("Easy:")[1])[0]
            intermediate_accuracy = accuracy_pattern.findall(content.split("Intermediate:")[1])[0]
            hard_accuracy = accuracy_pattern.findall(content.split("Hard:")[1])[0]
            detailed_accuracies[key_name] = {
                'Easy': float(easy_accuracy),
                'Intermediate': float(intermediate_accuracy),
                'Hard': float(hard_accuracy)
            }

# Plot overall accuracies
plt.figure(figsize=(12, 6))
bars = plt.bar(overall_accuracies.keys(), overall_accuracies.values(), color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Overall Accuracy (%)')
plt.title('Overall Accuracy for Each Model')

# Add value labels on top of each bar
reported_model_height = None
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%',
             ha='center', va='bottom', rotation=0)
    if bar.get_x() <= xlabel_names.index('reported model') < bar.get_x() + bar.get_width():
        reported_model_height = height
        reported_model_color = bar.get_facecolor()

# Draw a dotted line at the height of the reported model's bar
if reported_model_height is not None:
    plt.axhline(y=reported_model_height, color=reported_model_color, linestyle='--')

plt.tight_layout()
plt.savefig('overall_accuracy.png')
plt.close()

# Plot detailed accuracies
categories = ['Easy', 'Intermediate', 'Hard']
plt.figure(figsize=(20, 6))
width = 0.25
x = np.arange(len(file_names))
col = ["lightblue", "green", "orange"]

for i, category in enumerate(categories):
    values = [detailed_accuracies[file_name][category] for file_name in xlabel_names]
    bars = plt.bar(x + i * width, values, width, color=col[i], label=category)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}%',
                 ha='center', va='bottom', rotation=0, fontsize=8)

    plt.axhline(y=detailed_accuracies["reported model"][category], color=col[i], linestyle='--')

plt.xticks(x + width, xlabel_names, rotation=45, ha='right')
plt.ylabel('Accuracy (%)')
plt.title('Detailed Accuracies for Each Model')
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig('detailed_accuracies.png')
plt.close()