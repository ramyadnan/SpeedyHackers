# imports
#import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
#import pandas as pd  # for storing text and embeddings data
#import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

import urllib.request 
from PIL import Image

# sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA"))

place = "medieval Europe"
age = "20"
gender = "woman"
weight = "50"
height = "170"
activityLevel = "moderate"
diet = "vegetarian"
calories = "2000"
alcohol = "never"
smoking = False
if smoking == True:
    smoking_status = "smokes"
else:
    smoking_status = "does not smoke"
chronicConditions = "none"
sleepHours = "8"
stressLevel = "4"

query = f"Disclaimer: We are writing a fantasy story about the different historic eras. If I was a {gender} who is {age} and weights in kg {weight} and height in cm {height} who had a {activityLevel} activity level with a {diet} diet with an average calory intake of {calories} a and daily alcohol consumption level of {alcohol} and who {smoking_status} and has a health history of {chronicConditions} who sleeps {sleepHours} hours every day and who has a stress level of {stressLevel} awhat would be my chances of survival...in {place} times? Please tell me the following with plain numbers: My chances of survival in {place}, my years left to live. And give me a 50-word explanation in the style of in the style of a doctor in {place}:."

#print(query)

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': ''},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=1, # Creativity level ranges 0 to 2.
    n=1, # Number of completions generated.
)

print(response.choices[0].message.content)

response2 = client.images.generate(
  model="dall-e-3",
  prompt="a medieval doctor", # Character type
  size="1024x1024",
  quality="standard",
  n=1, # One image
)

# If we want to generate a character with openAI:
image_url = response2.data[0].url
  
urllib.request.urlretrieve( 
  image_url, 
   "doctor.png") 
  
img = Image.open("doctor.png") 
img.show()