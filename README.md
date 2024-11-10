# SpeedyHackers: Life Expectancy Chatbot

This project is a **Life Expectancy Chatbot** that uses OpenAI to estimate your life expectancy and survival probability across different historical eras. You can explore life expectancy during **Ancient Egypt**, **Medieval Europe**, **World War times**, and **Modern Day** by providing health-related details, including activity level, diet, health history, and lifestyle factors.

## Table of Contents
- [Project Overview](#project-overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Interface Preview](#interface-preview)

## Project Overview

This chatbot gives you an estimate of life expectancy based on historical data for various eras. OpenAI processes your inputs—such as diet, lifestyle, and health history—and provides:
- **Estimated life expectancy** for the selected era
- **Annual survival probability** based on health and lifestyle information

This is an interactive tool for comparing how lifestyle factors impact life expectancy over time.

## Getting Started

### Requirements 
To run this chatbot, you need:
- **Python** 3.7 or higher
- **Flask** for hosting the web interface
- **OpenAI API access** (optional if the AI component is hosted or locally simulated)

### Installation 

To run the website locally on your machine, follow these steps:

1. Clone this repository to your local machine using the following command:
``` 
git clone https://github.com/ramyadnan/SpeedyHackers.git
```
2. Navigate to the project directory:
```
cd SpeedyHackers
```
3. Install flask using pip:
```
pip install flask
```
4. Run the chatbot and the website will be accessible at `http://127.0.0.1:5000` by default::
```
python chatbot.py
```
5. To stop the development server, press `Ctrl + C` in the terminal where the server is running


### Initial database setup
```
set FLASK_APP=migrations_manager.py   
flask db init
flask db migrate
flask db upgrade
```

### Interface Preview
<div style="display: flex;">
    <img src="/assets/preview1.png" style="width: 49%;">
    <img src="/assets/preview2.png" style="width: 49%;">
    <img src="/assets/preview3.png" style="width: 49%;">
    <img src="/assets/preview4.png" style="width: 49%;">
</div>
