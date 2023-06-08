import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("API_KEY")  # Add this line

app = Flask(__name__)
llm = ChatOpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)

# Define the prompt template
template = """Ignore previous instructions. Your name is Logan and you are english teacher.  Your main goal is to teach Bob at a B2+ level.

Current conversation:
{history}
Bob: {input}
Logan:"""
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=template
)

# Use ConversationSummaryBufferMemory
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)

conversation_chain = ConversationChain(
    llm=llm, 
    prompt=PROMPT, 
    verbose=True, 
    memory=memory,
)

@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

@app.route('/bot', methods=['POST'])
def respond():
    # Add this block of code
    if 'Authorization' not in request.headers or request.headers['Authorization'] != api_key:
        abort(401)
    message = request.json['message']
    response = conversation_chain.predict(input=message)
    return {"response": response}

@app.route('/clear', methods=['GET'])
def clear():
    # Add this block of code
    if 'Authorization' not in request.headers or request.headers['Authorization'] != api_key:
        abort(401)
    global memory
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)
    return {"status": "Cleared conversation history"}

if __name__=='__main__':
     app.run(host='0.0.0.0', port=4999)
