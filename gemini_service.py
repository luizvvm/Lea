# gemini_service.py
import os
import json
import google.generativeai as genai

# Configuração (sem mudanças)
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível configurar a API do Gemini. Erro: {e}")
    exit()

generation_config = {"response_mime_type": "application/json"}
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config)

# --- NOSSAS NOVAS FUNÇÕES ESPECIALISTAS ---

def analisar_solicitacao_inicial(texto_usuario):
    """
    Analisa a primeira mensagem do usuário para extrair a intenção e os dados.
    Esta é a porta de entrada para qualquer nova conversa.
    """
    prompt = f"""
    Analise a mensagem do usuário para identificar sua intenção principal.
    As intenções podem ser: 'solicitar_plano', 'criar_tarefa', 'listar_tarefas', 'concluir_tarefa', ou 'conversa_geral'.
    Extraia os parâmetros relevantes.

    MENSAGEM: "{texto_usuario}"

    Exemplos:
    1. MENSAGEM: "me ajude a criar um plano para concluir minha matéria de calculo II. Hoje é dia 18 de agosto, minha aula vai até 01 de dezembro, tenho que estudar 17 capítulos"
       SAÍDA: {{"intent": "solicitar_plano", "data": {{"tema": "Cálculo II", "detalhes": "17 capítulos entre 18/08 e 01/12"}}}}
    2. MENSAGEM: "adicione a tarefa de comprar pão"
       SAÍDA: {{"intent": "criar_tarefa", "data": {{"descricao": "comprar pão"}}}}
    3. MENSAGEM: "sim"
       SAÍDA: {{"intent": "confirmacao_positiva", "data": {{}}}}
    4. MENSAGEM: "não"
       SAÍDA: {{"intent": "confirmacao_negativa", "data": {{}}}}
    5. MENSAGEM: "bom dia"
       SAÍDA: {{"intent": "conversa_geral", "data": {{}}}}

    Retorne APENAS o JSON.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"ERRO em analisar_solicitacao_inicial: {e}")
        return {"intent": "conversa_geral", "data": {}}

def gerar_plano_de_acao(tema, detalhes):
    """
    Recebe um tema e detalhes estruturados e gera um plano de ação com tarefas.
    """
    prompt = f"""
    Crie um plano de ação conciso e estruturado para o seguinte objetivo.
    Divida o plano em 3 a 5 etapas principais.
    Para cada etapa, crie uma tarefa acionável.

    TEMA DO PLANO: {tema}
    DETALHES ADICIONAIS: {detalhes}

    Retorne sua resposta no seguinte formato JSON, sem exceção:
    {{
        "resumo_plano": "Uma frase que resume a estratégia do plano.",
        "tarefas_acionaveis": [
            "Primeira tarefa detalhada para o plano.",
            "Segunda tarefa detalhada para o plano.",
            "Terceira tarefa detalhada para o plano."
        ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"ERRO em gerar_plano_de_acao: {e}")
        return None