# app.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
import os
from twilio.rest import Client

from gemini_service import gerar_resposta_inteligente
# --- IMPORTAÇÃO ATUALIZADA ---
# Importamos todas as funções que o app vai usar diretamente.
import sheets_service

app = Flask(__name__)

# Credenciais da Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '')

    print(f"INFO: Recebi a mensagem de {from_number}: '{message_body}'")

    gemini_response = gerar_resposta_inteligente(message_body)
    
    intent = gemini_response.get('intent', 'conversa_geral')
    response_to_user = gemini_response.get('response_to_user', "Houve uma falha no meu processamento. Por favor, tente novamente.")

    if intent == 'criar_tarefa':
        descricao = gemini_response.get('parameters', {}).get('descricao_tarefa')
        if descricao:
            sheets_service.add_task_to_sheet(from_number, descricao)
        else:
            # --- AJUSTE DE TOM ---
            response_to_user = "Não identifiquei a tarefa a ser criada. Poderia reformular, por favor?"
    
    elif intent == 'listar_tarefas':
        tasks = sheets_service.get_tasks_from_sheet(from_number, status_filter="Pendente")
        if not tasks:
            # --- AJUSTE DE TOM ---
            response_to_user = "Seu registro de tarefas pendentes está limpo. Excelente."
        else:
            task_list_str = "\n".join([f"▫️ {task['Descricao']} (ID: {task['TaskID']})" for task in tasks])
            # --- AJUSTE DE TOM ---
            response_to_user = f"Estas são suas diretivas pendentes:\n\n{task_list_str}"

    elif intent == 'concluir_tarefa':
        task_id_to_complete = gemini_response.get('parameters', {}).get('task_id')
        if task_id_to_complete:
            success = sheets_service.update_task_status(from_number, task_id_to_complete.upper())
            if not success:
                # --- AJUSTE DE TOM ---
                response_to_user = f"O identificador de tarefa '{task_id_to_complete}' não foi localizado em seus registros. Verifique e tente novamente."
        else:
            # --- AJUSTE DE TOM ---
            response_to_user = "Não foi especificado qual tarefa deve ser marcada como concluída. Por favor, informe o ID."

    # --- BLOCO NOVO PARA METAS ---
    elif intent == 'definir_meta_plano':
        descricao_meta = gemini_response.get('parameters', {}).get('descricao_meta')
        if descricao_meta:
            sheets_service.add_goal_to_sheet(from_number, descricao_meta)
            # A resposta para o usuário já foi criada pela Gemini, então apenas a utilizamos.
        else:
            response_to_user = "O objetivo não foi claramente definido. Por favor, especifique a meta que deseja estabelecer."
    
    print(f"INFO: Enviando resposta para {from_number}: '{response_to_user}'")

    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=from_number,
            body=response_to_user
        )
        return 'OK', 200
    except Exception as e:
        print(f"ERRO: Erro ao enviar mensagem via Twilio: {e}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))