import os
from flask import Flask, request
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = "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"
app = Flask(__name__)
llm = OpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)

# Define the prompt template
template = """Ignore previous instructions. Your name is Logan and you are english teacher.  Your main goal is to teach Bob at a B2+ level.

{chat_history}
Bob: {human_input}
Logan:"""
prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], 
    template=template
)

# Use ConversationBufferMemory
memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    verbose=True, 
    memory=memory,
)

@app.route('/bot', methods=['POST'])
def respond():
    message = request.json['message']
    response = llm_chain.predict(human_input=message)
    return {"response": response}

@app.route('/clear', methods=['GET'])
def clear():
    global memory
    memory = ConversationBufferMemory(memory_key="chat_history")
    return {"status": "Cleared conversation history"}

if __name__=='__main__':
    app.run(port=5000)
