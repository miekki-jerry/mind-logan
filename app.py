import os
from flask import Flask, request
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = "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"
app = Flask(__name__)
llm = OpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)

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

@app.route('/bot', methods=['POST'])
def respond():
    message = request.json['message']
    response = conversation_chain.predict(input=message)
    return {"response": response}

@app.route('/clear', methods=['GET'])
def clear():
    global memory
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)
    return {"status": "Cleared conversation history"}

if __name__=='__main__':
    app.run(port=5000)
