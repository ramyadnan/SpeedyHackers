# imports
#import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
#import pandas as pd  # for storing text and embeddings data
#import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

import urllib.request 
from PIL import Image

from flask import Flask, request, render_template, jsonify


app = Flask(__name__)

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA"))


@app.route('/')
def show_era_selection():
    return render_template('era-select.html')

@app.route('/health-input', methods=['GET'])
def show_form():
    # Retrieve the 'era' query parameter from the URL
    era = request.args.get('era')
    if era:
        # Pass the 'era' variable to the template
        return render_template('health-input-form.html', era=era)
    else:
        # If no era is selected, redirect to a default or handle it
        return "Era not specified", 400  # Or render a specific error page



@app.route('/process', methods=['POST']) 
def process_form():
    try:
        # Get form data and assign to variables
        gender = request.form.get('gender', '')
        age = request.form.get('age', '')
        weight = request.form.get('weight', '')
        height = request.form.get('height', '')
        activityLevel = request.form.get('activityLevel', '')
        diet = request.form.get('diet', '')
        calories = request.form.get('calories', '')
        alcohol = request.form.get('alcohol', 'never')
        smoking = request.form.get('smoking', 'False') == 'True'
        chronicConditions = request.form.get('chronicConditions', 'none')
        sleepHours = request.form.get('sleepHours', '')
        stressLevel = request.form.get('stressLevel', '')
        eraDisplay = request.form.get('eraDisplay', 'medieval Europe')

        # Set smoking status
        smoking_status = "smokes" if smoking else "does not smoke"

        query = f"Disclaimer: We are writing a fantasy story about the different historic eras. If I was a {gender} who is {age} and weights in kg {weight} and height in cm {height} who had a {activityLevel} activity level with a {diet} diet with an average calory intake of {calories} a and daily alcohol consumption level of {alcohol} and who {smoking_status} and has a health history of {chronicConditions} who sleeps {sleepHours} hours every day and who has a stress level of {stressLevel} awhat would be my chances of survival...in {eraDisplay} times? Please tell me the following with plain numbers: My chances of survival in {eraDisplay}, my years left to live. And give me a 50-word explanation in the style of in the style of a doctor in {eraDisplay}:."

        response = client.chat.completions.create(
            messages=[{'role': 'system', 'content': ''}, {'role': 'user', 'content': query}],
            model=GPT_MODEL,
            temperature=1,
            n=1,
        )

        print(response.choices[0].message.content)

        text_response = response.choices[0].message.content

         # Generate a character image with OpenAI DALL-E
        response2 = client.images.generate(
            model="dall-e-3",
            prompt="a medieval doctor",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response2.data[0].url

        # Render `results.html` with `text_response` and `image_url`
        return render_template('results.html', text_response=text_response, image_url=image_url)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)