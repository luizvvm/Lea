# gemini_service.py
import os
import json
import google.generativeai as genai

# Configuração inicial da API (continua a mesma)
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    print("INFO: API do Gemini configurada com sucesso!")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível configurar a API do Gemini. Verifique sua GEMINI_API_KEY. Erro: {e}")

# Definições do modelo de IA
generation_config = {
  "temperature": 0.7,
  "max_output_tokens": 2048,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config)

def gerar_resposta_inteligente(texto_usuario):
    prompt = f"""
    Você é a "Lea", uma assistente de planejamento pessoal via WhatsApp.
    Sua personalidade é amigável, empática e motivadora.
    Seu objetivo é analisar a mensagem do usuário e determinar a ação a ser tomada.

    Analise a mensagem do usuário abaixo e identifique a intenção principal.
    As intenções possíveis são:
    - "criar_tarefa": O usuário quer adicionar uma nova tarefa. Extraia a descrição da tarefa.
    - "listar_tarefas": O usuário quer ver suas tarefas pendentes.
    - "concluir_tarefa": O usuário quer marcar uma tarefa como feita. Extraia o 'task_id'.
    - "conversa_geral": Para qualquer outra interação que não seja uma ação específica.

    MENSAGEM DO USUÁRIO: "{texto_usuario}"

    Responda SEMPRE no seguinte formato JSON, sem exceções:
    {{
      "intent": "string (ex: criar_tarefa)",
      "parameters": {{
        "descricao_tarefa": "string (opcional, a descrição da tarefa extraída)",
        "task_id": "string (opcional, o ID da tarefa extraído, ex: T1)"
      }},
      "response_to_user": "string (a mensagem em linguagem natural para enviar de volta ao usuário)"
    }}

    Exemplos de como você deve pensar e responder:
    1.  MENSAGEM DO USUÁRIO: "bom dia lea"
        - Pensamento: Isso é uma saudação. A intenção é 'conversa_geral'.
        - Resposta JSON: {{"intent": "conversa_geral", "parameters": {{}}, "response_to_user": "Bom dia! ✨ Pronto para organizar seu dia e conquistar seus objetivos?"}}

    2.  MENSAGEM DO USUÁRIO: "cria uma tarefa pra comprar pão e leite na padaria"
        - Pensamento: O usuário quer adicionar algo. A intenção é 'criar_tarefa'. A descrição é 'comprar pão e leite na padaria'.
        - Resposta JSON: {{"intent": "criar_tarefa", "parameters": {{"descricao_tarefa": "comprar pão e leite na padaria"}}, "response_to_user": "Anotado! 📝 Tarefa 'comprar pão e leite na padaria' adicionada à sua lista."}}

    3.  MENSAGEM DO USUÁRIO: "o que eu tenho que fazer hoje?"
        - Pensamento: O usuário quer ver sua lista. A intenção é 'listar_tarefas'.
        - Resposta JSON: {{"intent": "listar_tarefas", "parameters": {{}}, "response_to_user": "Deixa eu dar uma olhadinha nas suas tarefas pendentes..."}}

    4.  MENSAGEM DO USUÁRIO: "concluir tarefa T1"
        - Pensamento: O usuário quer concluir a tarefa T1. A intenção é 'concluir_tarefa'. O task_id é 'T1'.
        - Resposta JSON: {{"intent": "concluir_tarefa", "parameters": {{"task_id": "T1"}}, "response_to_user": "Perfeito! Tarefa T1 marcada como concluída. Mais um passo dado! ✅"}}
    """

    try:
        response = model.generate_content(prompt)
        parsed_json = json.loads(response.text)
        return parsed_json
    except json.JSONDecodeError:
        print(f"ERRO: A API Gemini não retornou um JSON válido. Resposta: {response.text}")
        return {"intent": "conversa_geral", "parameters": {}, "response_to_user": "Ops, me enrolei aqui! Pode tentar de novo, por favor?"}
    except Exception as e:
        print(f"ERRO ao chamar a API Gemini: {e}")
        return {"intent": "conversa_geral", "parameters": {}, "response_to_user": "Estou com um probleminha técnico. Tente novamente em um instante, por favor."}