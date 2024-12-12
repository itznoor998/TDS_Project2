#/// script
# requires-python = ">=3.11"
# dependencies = [
#   "python-dotenv",
#   "pandas",
#   "numpy",
#   "matplotlib",
#   "seaborn",
#   "os",
#   "sys",
#   "warnings",
#   "datetime",
#   "requests",
#   "json",
# ]
# ///

from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import warnings
from datetime import datetime
import requests
import json




def load_data(file_path):

    """Load the dataset from 'file_path'."""


    try:
        # read the dataset using pandas
        data = pd.read_csv(file_path,encoding='latin1',encoding_errors='ignore')
        print(f"Dataset loaded successfully with {data.shape[0]} rows and {data.shape[1]} columns.")
        return data
    except Exception as e:
        # handle exceptions if any
        print(f"Error loading dataset: {e}")
        sys.exit(1)

def data_cleaning(data):

    """Perform data cleaning operations."""

    

def general_statistics(data):

    """Generate general statistics and return as a string."""

    numerical_cols = data.select_dtypes(include='number').columns
    categorical_cols = data.select_dtypes(exclude='number').columns

    numerical_data = data.loc[:,numerical_cols]
    categorical_data = data.loc[:,categorical_cols]

    stats = f"Dataset Summary:\n"
    stats += f"Shape: {data.shape[0]} rows, {data.shape[1]} columns\n"
    stats += f"Columns: {', '.join(data.columns)}\n"
    stats += f"Total no of NaN values in the dataset:{data.isna().sum().sum()}\n"
    stats += f"Unique values in categorical columns:\n{categorical_data.nunique()}\n"


    for col in categorical_cols:
        top_values = data[col].value_counts().head(5).to_dict()
        stats += f"Top five values in {col}:\n{top_values}\n"

    stats += f"\nSummary Statistics:\n{data.describe()}\n"

    outliers = {}
    
    for col in numerical_cols:
        z_scores = (data[col] - data[col].mean()) / data[col].std()
        threshold = 3
        outliers[col] = len(data[z_scores.abs() > threshold][col].tolist())
    stats += f"Number of outliers in each column:\n{outliers}\n"

    for num_col in numerical_cols:
        for Num_col in numerical_cols:
            if num_col != Num_col:
                stats += f"- Correlation between {num_col} and {Num_col}: {numerical_data[num_col].corr(numerical_data[Num_col])}\n"
    
    
    return stats

def plot_visualizations(data):

    """Generate and save visualizations."""

    images = []

    numerical_cols = data.select_dtypes(include='number').columns
    categorical_cols = data.select_dtypes(exclude='number').columns

    numerical_data = data.loc[:,numerical_cols]
    categorical_data = data.loc[:,categorical_cols]

    if len(numerical_cols) > 1:
        corr_mat = numerical_data.corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_mat, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title('Heatmap')
        heatmap = "heatmap.png"
        plt.tight_layout()
        plt.savefig(heatmap)
        plt.close()
        images.append(heatmap)

        plt.figure(figsize=(8, 6))
        numerical_data.hist(bins=20, color='skyblue', edgecolor='black')
        plt.title('Histogram')
        hist = "histogram.png"
        plt.tight_layout()
        plt.savefig(hist)
        plt.close()
        images.append(hist)

    print("Please wait, pairplot is generating...")
    warnings.filterwarnings("ignore", category=UserWarning)
    plt.figure(figsize=(10, 8))
    sns.pairplot(data,diag_kind='kde', palette='virdis')
    plt.tight_layout()
    pairplot = "pairplot.png"
    plt.savefig(pairplot)
    plt.close()
    images.append(pairplot)
    

    return images

def write_report(stats):

    """Write the analysis results to README.md."""

    with open('README.md', 'w') as file:
        file.write("# Data Analysis Report\n")
        file.write(f"Analysis performed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("## General Statistics\n")
        file.write(stats)
    file.close()

def analyze_data(data):

    """Main function to load data, analyze it."""

    # Generate general statistics
    stats = general_statistics(data)

    # Write the analysis results to README.md
    write_report(stats)

    analysis = ""

    #Read the analysis results
    with open('README.md', 'r') as file:
        analysis = file.read()
        file.close()
    return analysis


def generate_story(data_analysis,df):

    """ Generating story with the help of LLM"""

    load_dotenv() # Loading the .env 

    AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN') #fetching the token
    if AIPROXY_TOKEN is None:
        print("AIPROXY_TOKEN not found in .env file")
        sys.exit(1)

    # url to send requests to LLM to generate story
    url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    headers={
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
            "Content-Type": "application/json"
        }
    function_descriptions=[
            {
                "name": "generate_story",
                "description": "Generate  an engaging and interesting story from the provided data analysis and return as json format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_analysis": {
                            "type": "string",
                            "description": "The analysis of the dataset."
                        }   
                    }
                }
            }
        ]
            

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant who helps to generate interesting stories from data analysis."
            },
            {
                "role": "user",
                "content": """Based on the following data analysis findings, generate a professional, engaging narrative with clear,
                    insightful subheadings highlighting the key trends and insights. Structure the story well."""
            }
        ],
        "max_tokens": 500,
        "functions": function_descriptions,
        "function_call":{"name": "generate_story", "arguments": {"data_analysis": data_analysis}}
    }

    response = requests.post(url=url, headers=headers, json=data)

    print(response.text)
    raw_story =  response.json()['choices'][0]['message']['function_call']['arguments']

    story = json.loads(raw_story)['data_analysis']

    # Saving figures
    images = plot_visualizations(df)

    # Overwrite analysis results in README.md with story and visualizations
    with open('README.md', 'w') as file:
        file.write("# Report\n")
        file.write(f"\nReport created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        # Embed images in markdown format
        file.write("\n## Visualizations\n")
        for image in images:
            file.write(f"![{image}]({image})\n")
        file.write(f"\n\n## Story\n\n{story}")
        file.close()
    print("Story and visualizations generated. Check README.md")
    return story

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <csv_file>")
        sys.exit(1)

    # Get the file path from the command line
    dataset_path = sys.argv[1]
    print(dataset_path)
    # Load the dataset
    data = load_data(dataset_path)
    # Analyze the data
    data_analysis = analyze_data(data)
    
    #  Generate the story
    story = generate_story(data_analysis,data)

