import os
import re
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains.summarize import load_summarize_chain

load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")
personal_api_key = os.getenv("API_KEY")  # Add this line


app = Flask(__name__)
llm = ChatOpenAI(model_name ='gpt-3.5-turbo', temperature=0.9, max_tokens=256)

@app.route('/chunk', methods=['POST'])
def chunk_and_summarize():
    text = request.json['text']

    llm = OpenAI(temperature=0)

    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(text)

    docs = [Document(page_content=t) for t in texts[:3]]

    chain = load_summarize_chain(llm, chain_type="map_reduce")
    result = chain.run(docs)

    return jsonify({'summary': result}), 200

if __name__ == '__main__':
    app.run(port=4999, debug=True)