import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

app = Flask(__name__)

# Provide the folder path for PDF files
PDF_FOLDER_PATH = "pdf/uae.pdf"
conversation_chain = None

def get_pdf_text(pdf_file_path):
    text = ""
    try:
        pdf_reader = PdfReader(pdf_file_path)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except PdfReadError:
        print("Error: Could not read the PDF file due to PdfReadError: EOF marker not found.")
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    global conversation_chain
    raw_text = get_pdf_text(PDF_FOLDER_PATH)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    conversation_chain = get_conversation_chain(vectorstore)
    return jsonify({"message": "PDF processed successfully."})

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get('question')
    answer = ""
    if conversation_chain:
        response = conversation_chain({'question': user_question})
        chat_history = response['chat_history']
        answer = chat_history[-1].content
    return jsonify({"answer": answer})

if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
