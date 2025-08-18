# app.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
import os
from twilio.rest import Client

from gemini_service import gerar_resposta_inteligente
import sheets_service

app = Flask(__name__)

# Credenciais da Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- NOSSA NOVA MEMÓRIA DE CURTO PRAZO ---
# Em um ambiente de produção real, usaríamos um banco de dados como Redis,
# mas para o nosso MVP, um dicionário Python é suficiente.
conversation_contexts = {}

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    print(f"INFO: Recebi a mensagem de {from_number}: '{message_body}'")

    # --- LÓGICA DE MEMÓRIA (LEITURA) ---
    # 1. Verificamos se há um contexto salvo para este usuário
    user_context = conversation_contexts.get(from_number, {})

    # 2. Enviamos a mensagem do usuário E o contexto para a Gemini
    gemini_response = gerar_resposta_inteligente(message_body, user_context)
    
    intent = gemini_response.get('intent', 'conversa_geral')
    response_to_user = gemini_response.get('response_to_user', "Houve uma falha no meu processamento. Por favor, tente novamente.")
    
    # Extrai a nova tag de contexto, se houver
    new_context_tag = gemini_response.get('set_context_tag')

    # Lógica de Ações (if/elif)
    if intent == 'criar_tarefa':
        descricao = gemini_response.get('parameters', {}).get('descricao_tarefa')
        if descricao:
            sheets_service.add_task_to_sheet(from_number, descricao)
    
    elif intent == 'listar_tarefas':
        # (a lógica de listar tarefas permanece a mesma, com os ajustes de tom)
        pass

    elif intent == 'concluir_tarefa':
        # (a lógica de concluir tarefa permanece a mesma, com os ajustes de tom)
        pass

    elif intent == 'definir_meta_plano':
        # Agora, a descrição da meta pode vir da mensagem atual ou do contexto salvo
        descricao_meta = gemini_response.get('parameters', {}).get('descricao_meta')
        plano_gerado = gemini_response.get('parameters', {}).get('plano_detalhado')

        # Se a Gemini gerou um plano detalhado, usamos isso como descrição
        meta_a_salvar = plano_gerado if plano_gerado else descricao_meta
        if meta_a_salvar:
            sheets_service.add_goal_to_sheet(from_number, meta_a_salvar)

    # --- LÓGICA DE MEMÓRIA (ESCRITA) ---
    # 3. Atualizamos ou limpamos a memória após processar a ação
    if new_context_tag:
        # Se a Gemini pediu para aguardar uma resposta, salvamos o contexto
        # Também salvamos os dados atuais para uso futuro
        current_data = gemini_response.get('parameters', {})
        conversation_contexts[from_number] = {"last_tag": new_context_tag, "data": current_data}
        print(f"INFO: Contexto salvo para {from_number}: {new_context_tag}")
    else:
        # Se não há nova tag, a conversa foi concluída, então limpamos a memória
        if from_number in conversation_contexts:
            del conversation_contexts[from_number]
            print(f"INFO: Contexto limpo para {from_number}")
    
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