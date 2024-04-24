# from flask import Flask, request, jsonify, abort, session
# from flask_cors import CORS
# import os
# import google.generativeai as genai
# import PyPDF2

# app = Flask(__name__)
# # Utilize uma chave secreta fixa para garantir que as sessões sejam persistentes entre reinícios da aplicação
# app.config['SECRET_KEY'] = 'gdçkmdf~çpgndiaÕBNLKFJHDBLS56461651dfgsd3g4'
# CORS(app)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita o tamanho máximo de upload de arquivos a 16MB

# os.environ['GOOGLE_API_KEY'] = "AIzaSyBcYei2m_mC8QSBQh72DQ1SbbwOL_pNHfo"
# genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# model = genai.GenerativeModel('gemini-pro')


# @app.route('/api/chat', methods=['POST'])
# def chat():
#     # Inicializa o contexto da sessão se não existir
#     session_context = session.get('context', '')
#     user_message = request.form.get('message', '')
#     file = request.files.get('file')

#     if file and allowed_file(file.filename):
#         pdf_text = extract_text_from_pdf(file)
#         session_context += f"\nPDF Text: {pdf_text}"

#     full_message = f"{session_context}\n{user_message}".strip()
#     if not full_message:
#         abort(400, 'No text found in the message or PDF.')

#     response = model.generate_content(full_message)

#     # Atualiza o contexto na sessão para uso futuro
#     session['context'] = full_message

#     return jsonify({'message': response.text})

# def extract_text_from_pdf(file):
#     try:
#         pdf_reader = PyPDF2.PdfReader(file.stream)
#         text = ''.join(page.extract_text() or "" for page in pdf_reader.pages)  # Usa 'or ""' para evitar None
#         return text
#     except Exception as e:
#         print(f"Failed to extract PDF text: {e}")
#         abort(400, 'Failed to extract text from PDF.')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

# if __name__ == "__main__":
#     app.run(port=8501)


from flask import Flask, request, jsonify, abort, session
from flask_session import Session  # Importar Session de flask_session
from flask_cors import CORS
import os
import google.generativeai as genai
import PyPDF2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gdçkmdf~çpgndiaÕBNLKFJHDBLS56461651dfgsd3g4'
app.config['SESSION_TYPE'] = 'filesystem'  # Configurando o tipo de sessão para armazenamento no sistema de arquivos
Session(app)  # Inicializando o objeto Session com a configuração do app
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita o tamanho máximo de upload de arquivos a 16MB

os.environ['GOOGLE_API_KEY'] = "AIzaSyBcYei2m_mC8QSBQh72DQ1SbbwOL_pNHfo"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

model = genai.GenerativeModel('gemini-pro')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Inicializa ou recupera o histórico da sessão
    if 'history' not in session:
        session['history'] = []

    user_message = request.form.get('message', '')
    file = request.files.get('file')

    if file and allowed_file(file.filename):
        pdf_text = extract_text_from_pdf(file)
        user_message += f"\nPDF Text: {pdf_text}"

    # Armazena a mensagem do usuário no histórico
    if user_message.strip():
        session['history'].append(f"User: {user_message}")

    # Prepara o texto completo para o modelo
    full_context = "\n".join(entry.split(": ", 1)[1] for entry in session['history'])  # Remove prefixos para limpar a entrada

    response = model.generate_content(full_context)

    # Adiciona a resposta do modelo ao histórico
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
