from flask import Flask, request, jsonify, abort, session
from flask_cors import CORS
import os
import google.generativeai as genai
import PyPDF2


secret_key = os.urandom(16)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gdçkmdf~çpgndiaÕBNLKFJHDBLS56461651dfgsd3g4'
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.environ['GOOGLE_API_KEY'] = "AIzaSyBcYei2m_mC8QSBQh72DQ1SbbwOL_pNHfo"
genai.configure(api_key = os.environ['GOOGLE_API_KEY'])

# Select the model
model = genai.GenerativeModel('gemini-pro')

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     response = model.generate_content(user_message)
#     return jsonify({'message': response.text})

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     if 'file' in request.files:
#         file = request.files['file']
#         if file and file.filename.endswith('.pdf'):
#             print('chegou aqui para extrai pdf')
#             pdf_text = extract_text_from_pdf(file)
#         else:
#             abort(400, 'Only PDF files are accepted.')
#     else:
#         pdf_text = ""

#     user_message = request.form.get('message', '')
#     combined_text = f"{user_message}\nPDF Text: {pdf_text}" if pdf_text else user_message
    
#     if not combined_text.strip():
#         abort(400, 'No text found in the message or PDF.')

#     response = model.generate_content(combined_text)
#     return jsonify({'message': response.text})

# def extract_text_from_pdf(file):
#     try:
#         # Assegure-se de ler o arquivo como um stream binário
#         pdf_reader = PyPDF2.PdfReader(file.stream)
#         text = ''
#         # Usa len(reader.pages) ao invés de reader.numPages
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text
#     except Exception as e:
#         print(f"Failed to extract PDF text: {e}")
#         return ""

@app.route('/api/chat', methods=['POST'])
def chat():
    session_context = session.get('context', '')
    user_message = request.form.get('message', '')
    file = request.files.get('file')

    if file and allowed_file(file.filename):
        pdf_text = extract_text_from_pdf(file)
        session_context += f"\nPDF Text: {pdf_text}"

    full_message = f"{session_context}\n{user_message}"
    response = model.generate_content(full_message)

    # Update session context
    session['context'] = full_message  # Or manage the size of context if needed

    return jsonify({'message': response.text})

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file.stream)
    text = ''.join(page.extract_text() for page in pdf_reader.pages)
    return text

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


if __name__ == "__main__":
    app.run(port=8501)