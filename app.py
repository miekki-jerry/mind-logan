import os
import re
from flask_cors import CORS
from dotenv import load_dotenv
from airtable_con import get_answer, airtable
from datetime import datetime
from flask import Flask, request, abort, jsonify
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate

load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")
personal_api_key = os.getenv("API_KEY")  # Add this line


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

llm = ChatOpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)

name = "bob"
# Define the prompt template
template = """Ignore previous instructions. Your name is Logan and you are english teacher.  Your main goal is to teach Bob at a B2+ level.
Current conversation: 
{history}
Bob: {input}
Logan:
[end]
""" 
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=template
)

# Use ConversationSummaryBufferMemory
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)

conversation_history = []

conversation_chain = ConversationChain(
    llm=llm, 
    prompt=PROMPT, 
    verbose=True, 
    memory=memory,
)

def save_to_airtable():
    # Access the global conversation_history variable
    global conversation_history
    # Format the conversation history as a single string
    conversation = "\n".join(f"Bob: {conv['bob']}\nLogan: {conv['logan']}" for conv in conversation_history)
    # Create a new record with the conversation
    record = {'answer': conversation}
    return airtable.create(record)


@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

@app.route('/test')
def fetch_and_display_answer():
    try: 
        answer = get_answer()
        return answer  # return the answer
    except Exception as e:
        print(e)  # Print the error message
        return str(e)  # Return the error message if any error occurs

@app.route('/bot', methods=['POST'])
def respond():
    # Add this block of code
    if 'Authorization' not in request.headers or request.headers['Authorization'] != personal_api_key:
        abort(401)
    message = request.json['message']
    response = conversation_chain.predict(input=message)

    # Remove 'Logan: ' from the response using regex and string manipulation
    cleaned_response = re.sub(r'^Logan: ', '', response)

    # Update the conversation history
    global conversation_history
    conversation_history.append({"bob": message, "logan": cleaned_response})

    return {"response": cleaned_response}


@app.route('/clear', methods=['GET'])
def clear():
    # Add this block of code
    if 'Authorization' not in request.headers or request.headers['Authorization'] != personal_api_key:
        abort(401)
    global memory
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)

    # Clear the conversation history
    global conversation_history
    conversation_history = []

    return {"status": "Cleared conversation history"}


@app.route('/save', methods=['GET'])
def save():
    # Add this block of code
    if 'Authorization' not in request.headers or request.headers['Authorization'] != personal_api_key:
        abort(401)

    # try:
    #     # Access the global conversation_history variable
    #     global conversation_history
        # Save the conversation history to a file
    #     filename = datetime.now().strftime("%d-%m-%Y--%H:%M") + ".txt"
    #     with open(filename, "w") as f:
    #         for conversation in conversation_history:
    #             f.write(f"Bob: {conversation['bob']}\nLogan: {conversation['logan']}\n")
    #     return {"status": "Conversation history saved successfully"}
    # except Exception as e:
    #     return {"status": "Failed to save conversation history", "error": str(e)}
    try:
        # Save the conversation to Airtable and get the created record
        record = save_to_airtable()
        # Return a success status message
        return {"status": "Conversation history saved successfully"}
    except Exception as e:
        # Return an error status message if any exception occurs
        return {"status": "Failed to save conversation history", "error": str(e)}
    


if __name__=='__main__':
     app.run(host='0.0.0.0', port=4999)