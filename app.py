# app.py

from flask import Flask, request
import os
from dotenv import load_dotenv
from twilio.rest import Client

# IMPORTANTE: Importando a função inteligente que criamos no outro arquivo!
from gemini_service import gerar_resposta_inteligente

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Credenciais da Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Inicializa o cliente Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '')

    print(f"Recebi a mensagem de {from_number}: '{message_body}'")

    # <<< --- A GRANDE MUDANÇA ESTÁ AQUI --- >>>
    # Em vez de só responder "Você disse...", agora chamamos a função que fala com a Gemini.
    response_text = gerar_resposta_inteligente(message_body)

    print(f"Enviando resposta da Gemini para {from_number}: '{response_text}'")

    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=from_number,
            body=response_text
        )
        return 'OK', 200
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))