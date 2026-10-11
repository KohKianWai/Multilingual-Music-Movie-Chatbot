## Multilingual Music and Movie Chatbot

A multilingual chatbot that provides personalized music and movie recommendations through natural language interactions, helping users discover content based on their preferences in multiple languages.

### Setup Instructions

1. Create virtual environment

   (do this only for the first time) --> *python -m venv rasa-env*  
   (whenever working, write the code to activate the virtual environment) --> *rasa-env\Scripts\activate*  

3. Install dependencies: 
   *pip install -r requirements.txt*  

4. Train the model (models not included in repo): 
   *rasa train*  

5. Run the bot: 
   *rasa shell*  

6. Run the custom action classes (In another separate terminal): 
   *rasa run actions*

7. Run the RASA API (In another separate terminal): 
   *rasa run --enable-api --cors '\*'*

## Backend Setup

1. navigate to the backend folder: 
   *cd backend*

2. Activate venv (virtual environment): 
   *venv\Scripts\activate*

3. Start FastAPI backend with auto-reload: 
   *uvicorn main:app --reload*

## Frontend Setup

1. navigate to the frontend folder: 
   *cd frontend*

2. Run the command: 
   *npm run dev*

## API Setup

### Common Setup for ALL API
1. navigate to the backend folder: 
   *cd backend*

2. Activate venv (virtual environment): 
   *venv\Scripts\activate*

3. Install Dependencies (do it only once):
   1. *pip install python-dotenv*
   2. *python -m pip install requests*
   3. *pip install ytmusicapi*


### Notes
- Python version: 3.10.5
- Rasa Version: 3.6.20  
- Rasa SDK Version: 3.6.2  
- Python Version: 3.10.5  
- Models folder is excluded since the project is still under development
