# imports
#import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
#import pandas as pd  # for storing text and embeddings data
#import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

# sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA"))

query = 'You answer questions in the style of a doctor in medieval europe: How would I be treated if I had a fever in medieval times times'

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': ''},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=0,
)

print(response.choices[0].message.content)