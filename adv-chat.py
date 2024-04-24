from flask import Flask, request, jsonify, abort, session
from flask_session import Session
from flask_cors import CORS
import os
import google.generativeai as genai
import PyPDF2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gdçkmdf~çpgndiaÕBNLKFJHDBLS56461651dfgsd3g4'
app.config['SESSION_TYPE'] = 'filesystem' 
Session(app)  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app, supports_credentials=True)

os.environ['GOOGLE_API_KEY'] = "AIzaSyBcYei2m_mC8QSBQh72DQ1SbbwOL_pNHfo"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

model = genai.GenerativeModel('gemini-pro')

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'history' not in session:
        session['history'] = []

    user_message = request.form.get('message', '')
    file = request.files.get('file')

    if file and allowed_file(file.filename):
        pdf_text = extract_text_from_pdf(file)
        user_message += f"\nPDF Text: {pdf_text}"

    if user_message.strip():
        session['history'].append(f"User: {user_message}")

    full_context = "\n".join(entry.split(": ", 1)[1] for entry in session['history'])

    response = model.generate_content(full_context)

    session['history'].append(f"Bot: {response.text}")

    return jsonify({'message': response.text})

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file.stream)
        return ''.join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as e:
        print(f"Failed to extract PDF text: {e}")
        abort(400, 'Failed to extract text from PDF.')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

if __name__ == "__main__":
    app.run(port=8501)
