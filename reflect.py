import os
import globalvars
from dotenv import load_dotenv
from airtable_con import get_answer, airtable
from flask import Flask, request
# from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")
appReflect = Flask(__name__)
llm = ChatOpenAI(model_name ='gpt-4', temperature=0.4, max_tokens=4000)

# Define the prompt template
template = """You are Logan, a witty and insightful English language tutor, tasked with summarizing a recent lesson with Bob, your student. 
Bob is aiming to elevate his English skills to a B2+ level, with a particular emphasis on vocabulary, grammar, and idioms. 
In a brief way, write about what the lesson was about.
As you wrap up the lesson, reflect on his progress, identifying and correcting any lingering mistakes in his speech or writing. 
You and Bob have developed a friendship that transcends the traditional teacher-student dynamic. 
In your summary, evaluate the effectiveness of today's session and identify the areas where Bob had difficulties but try to keep it as short as you can. 
Additionally, consider what teaching methods or strategies you could adopt to better facilitate Bob's learning in future sessions.
Additionally evaluate if Bob has learned the words from the lesson. Write the word yes/no. 
Example:
word1 = yes/no
word2 = yes/no
Conversation from previous lesson:
"
{human_input}
"
###
your reflexion:
"""
prompt = PromptTemplate(
    input_variables=["human_input"], 
    template=template
)


llm_chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    verbose=True
)

def save_to_airtable(response):
    record_id = globalvars.record_id  # Get the record id
    record = {'reflexion': response}
    return airtable.update(record_id, record)  # Update the record

def create_reflection():
    response = llm_chain.predict(human_input=globalvars.reflect_conversation_history)
    #save_to_airtable(response)  # make sure this saves to the 'question' column
    return response

def reflect():
    reflection = create_reflection()
    save_to_airtable(reflection)
    try:
        status_message = {"status": "Successfully reflected the conversation history"}
    except Exception as e:
        status_message = {"status": "Failed to reflect conversation history", "error": str(e)}
    return status_message


if __name__=='__main__':
    appReflect.run(port=5000)
