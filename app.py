# app.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
import os
from twilio.rest import Client

# Nossas novas funções especialistas
from gemini_service import analisar_solicitacao_inicial, gerar_plano_de_acao
import sheets_service

app = Flask(__name__)

# Configuração Twilio (sem mudanças)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Memória de Curto Prazo
conversation_contexts = {}

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    response_to_user = "Não compreendi sua solicitação. Poderia reformular?" # Resposta padrão

    # 1. VERIFICAR SE HÁ UMA CONVERSA EM ANDAMENTO
    user_context = conversation_contexts.get(from_number)

    if user_context:
        # --- FLUXO DE CONVERSA EXISTENTE ---
        analise = analisar_solicitacao_inicial(message_body) # Usamos para detectar 'sim'/'não'
        
        if user_context['tag'] == 'awaiting_plan_confirmation' and analise['intent'] == 'confirmacao_positiva':
            # O usuário disse 'sim' para a criação do plano.
            
            # Chamamos o especialista em gerar planos
            dados_plano = user_context['data']
            plano_gerado = gerar_plano_de_acao(dados_plano['tema'], dados_plano.get('detalhes', ''))

            if plano_gerado:
                sheets_service.add_goal_to_sheet(from_number, f"Plano para: {dados_plano['tema']}")
                sheets_service.add_tasks_from_plan(from_number, plano_gerado['tarefas_acionaveis'])
                
                tarefas_formatadas = "\n".join([f"▫️ {tarefa}" for tarefa in plano_gerado['tarefas_acionaveis']])
                response_to_user = f"{plano_gerado['resumo_plano']}\n\nAdicionei as seguintes tarefas iniciais à sua lista:\n{tarefas_formatadas}"
            else:
                response_to_user = "Enfrentei uma dificuldade ao detalhar o plano. Poderíamos tentar novamente?"

            # Limpa o contexto, pois a conversa terminou
            del conversation_contexts[from_number]

        else:
            # O usuário respondeu algo inesperado, então limpamos o contexto para recomeçar
            response_to_user = "Entendido. Deixaremos o plano para depois. Como posso auxiliar agora?"
            del conversation_contexts[from_number]

    else:
        # --- FLUXO DE UMA NOVA CONVERSA ---
        analise = analisar_solicitacao_inicial(message_body)
        intent = analise.get('intent')
        data = analise.get('data', {})

        if intent == 'solicitar_plano':
            # A IA detectou um pedido de plano. O código agora faz a pergunta.
            response_to_user = f"Compreendi que você deseja um plano para '{data.get('tema', 'seu objetivo')}'. Tenho os detalhes necessários. Deseja que eu gere o plano de ação agora?"
            
            # Salvamos o contexto para aguardar a confirmação
            conversation_contexts[from_number] = {"tag": "awaiting_plan_confirmation", "data": data}

        elif intent == 'listar_tarefas':
            tasks = sheets_service.get_tasks_from_sheet(from_number)
            if not tasks:
                response_to_user = "Seu registro de tarefas pendentes está limpo."
            else:
                task_list_str = "\n".join([f"▫️ {task['Descricao']} (ID: {task['TaskID']})" for task in tasks])
                response_to_user = f"Estas são suas diretivas pendentes:\n\n{task_list_str}"
        
        # ... (aqui entrariam outros intents como criar_tarefa, concluir_tarefa) ...

        else: # conversa_geral
             response_to_user = "Entendido. Como posso ser útil?"


    # Envia a resposta final para o usuário
    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=from_number,
            body=response_to_user
        )
        return 'OK', 200
    except Exception as e:
        print(f"ERRO ao enviar mensagem via Twilio: {e}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))