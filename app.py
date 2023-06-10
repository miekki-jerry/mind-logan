import os
import re
import globalvars
from flask_cors import CORS
from dotenv import load_dotenv
from airtable_con import get_answer, airtable
from reflect import reflect
from datetime import datetime
from flask import Flask, request, abort, jsonify
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate

load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")
personal_api_key = os.getenv("API_KEY")  # Add this line

conversation_history = []

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

llm = ChatOpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)


name = "bob"
# Define the prompt template
template = """You are Logan, a witty and insightful english language tutor. Help me, Bob, elevate my English to a B2+ level, with a focus on vocabulary, grammar, and idioms. Feel free to correct my mistakes and guide me through fun quizzes, real-life situations, and games. Our dynamic is more than just a tutor and student; we're friends, too. So, a dash of sarcasm and genuine interest is appreciated. You answers should be concist.

###
A quick glimpse into my world: I'm an AI enthusiast on a journey to become a product manager, the founder of a humor-based app MemeMatch, a fitness buff, and enjoy strolling with my girlfriend, Angelina.

###
I've prepared a few English words that I'm struggling with at the moment. Could you please use them in sentences? 
words: incentive,Swiftly,in terms of,Robust,estranged

###
idiom for todays lesson: The ball is in your court
###
your notes from previous lesson:
 'Today's lesson with Bob focused on advanced AI vocabulary, grammar, and idioms. We discussed the meaning and usage of several vocabulary words, including grief, lightheartedness, juvenile, stifle, and anoint. Bob had some difficulties initially, but after providing additional examples and mnemonics, he seemed to grasp the concepts better.

We also covered the idiom "let the cat out of the bag" and explored its similarity to "spill the beans." Furthermore, we discussed advanced AI concepts such as Large Language Models (LLMs) and their potential impact on the future. Bob demonstrated a good understanding of these concepts and was able to use the advanced AI vocabulary in sentences.

Towards the end, we briefly discussed potential updates for Bob's MemeMatch app and wrapped up with a quick quiz on the AI vocabulary we learned. Overall, Bob made progress in today's session, but there is still room for improvement, especially in using new vocabulary in context.

In future sessions, we could consider incorporating more interactive activities, such as role-plays or debates, to help Bob practice using new vocabulary and idioms in real-life situations. Additionally, offering more examples and mnemonics could help him better understand and remember challenging words.'
Here is plan for today's lesson written in json without brackets: 
###
"day": "Tuesday",
"lesson_name": "Product management and startup culture",
"objective": "Discuss startup culture and product management in the target language",
"content": "Vocabulary related to startups and product management, common expressions and idioms related to entrepreneurship",
"activities": "Reading and discussing an article on startup culture, role-playing a conversation with a founder",
"practise": "Write a paragraph describing your experience with entrepreneurship or your interest in startups",
"assessment": "A short quiz on startup culture and product management vocabulary"
###
but for now let's warm-up. Try engage me in a quick ice-breaker related to the day's topic.
Bobs first message today was: hello
you:
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



conversation_chain = ConversationChain(
    llm=llm, 
    prompt=PROMPT, 
    verbose=True, 
    memory=memory,
)

def check_authorization():
    if 'Authorization' not in request.headers or request.headers['Authorization'] != personal_api_key:
        abort(401)


def save_to_airtable():
    # Access the global conversation_history variable
    global conversation_history
    # Format the conversation history as a single string
    conversation = "\n".join(f"Bob: {conv['bob']}\nLogan: {conv['logan']}" for conv in conversation_history)
    # Create a new record with the conversation
    record = {'conversationHistory': conversation}
    globalvars.reflect_conversation_history = conversation
    created_record = airtable.create(record)  # Save the returned record
    globalvars.record_id = created_record['id']  # Save the record id to a global variable
    return created_record

def perform_save_to_airtable():
    # Perform saving to Airtable here and return the result
    # Replace with actual implementation
    try:
        # Save the conversation to Airtable and get the created record
        record = save_to_airtable() # replace this with actual implementation
        # Return a success status message
        return {"status": "Conversation history saved successfully"}
    except Exception as e:
        # Return an error status message if any exception occurs
        return {"status": "Failed to save conversation history", "error": str(e)}


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
    check_authorization()  

    message = request.json['message']
    response = conversation_chain.predict(input=message)

    # Remove 'Logan: ' from the response using regex and string manipulation
    cleaned_response = re.sub(r'^(System|Logan): ', '', response)

    # Update the conversation history
    global conversation_history
    conversation_history.append({"bob": message, "logan": cleaned_response})

    return {"response": cleaned_response}


@app.route('/clear', methods=['GET'])
def clear():
    check_authorization()

    global memory
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)

    # Clear the conversation history
    global conversation_history
    conversation_history = []

    return {"status": "Cleared conversation history"}


@app.route('/save', methods=['GET'])
def save():
    check_authorization()

    return perform_save_to_airtable()   
    
    

@app.route('/reflect', methods=['GET'])
def reflect_conversation():
    check_authorization()
    save_to_airtable()
    reflection = reflect()  # Get the reflection
    return reflection 

        


if __name__=='__main__':
     app.run(host='0.0.0.0', port=4999)