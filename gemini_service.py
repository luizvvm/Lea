# gemini_service.py

import os
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL DA API ---
# Este bloco de código tenta configurar a conexão com a Google AI.
# Se a chave não estiver no .env, ele vai avisar no terminal.
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    print("INFO: API do Gemini configurada com sucesso!")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível configurar a API do Gemini. Verifique sua GEMINI_API_KEY no arquivo .env. Erro: {e}")

# --- DEFINIÇÕES DO MODELO DE IA ---
# Configurações que definem o comportamento da IA.
generation_config = {
  "temperature": 0.9,
  "max_output_tokens": 2048,
}

# Inicializa o modelo de IA que vamos usar. 
# "gemini-1.5-flash-latest" é excelente para chat: rápido e poderoso.
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config)

# --- A FUNÇÃO PRINCIPAL DO "CÉREBRO" ---
def gerar_resposta_inteligente(texto_usuario):
    """
    Esta função recebe o texto do usuário, monta as instruções para a IA (prompt),
    envia para o Google e retorna a resposta que a IA gerou.
    """

    # PROMPT ENGINEERING: A instrução que damos à IA. É a personalidade da Lea.
    prompt = f"""
    Você é a "Lea", uma assistente de planejamento pessoal via WhatsApp.
    Sua personalidade é amigável, empática, motivadora e inteligente. Seus arquétipos são Sábio, Cuidador e um toque de Mago.
    Seu objetivo é ajudar estudantes e jovens profissionais a combater a procrastinação e a desorganização.

    NUNCA se apresente novamente, a menos que o usuário pergunte quem você é. Vá direto ao ponto.
    Responda à mensagem do usuário de forma útil e encorajadora, mantendo a conversa fluindo.

    MENSAGEM DO USUÁRIO: "{texto_usuario}"

    SUA RESPOSTA:
    """

    try:
        # Envia o prompt para o modelo de IA.
        response = model.generate_content(prompt)
        # Retorna o texto da resposta da IA.
        return response.text
    except Exception as e:
        # Se algo der errado na comunicação com o Google, temos uma resposta padrão.
        print(f"ERRO ao chamar a API Gemini: {e}")
        return "Ops! Tive um probleminha para processar sua mensagem. Poderia tentar de novo, por favor?"