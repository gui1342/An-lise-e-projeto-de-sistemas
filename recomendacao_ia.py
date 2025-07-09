import google.generativeai as genai
from datetime import date

# --- IMPORTANTE ---
# Coloque sua Chave de API do Google AI Studio aqui.
# É altamente recomendável usar variáveis de ambiente para isso em um projeto real.
GOOGLE_API_KEY = ''

genai.configure(api_key=GOOGLE_API_KEY)

# Configurações do modelo da IA
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  # ... (outras configurações de segurança podem ser adicionadas)
]

model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def calcular_idade(data_nascimento_str: str) -> int:
    """Calcula a idade a partir de uma string de data no formato YYYY-MM-DD."""
    if not data_nascimento_str:
        return 25 # Retorna uma idade padrão se não houver data
    try:
        nascimento = date.fromisoformat(data_nascimento_str)
        hoje = date.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade
    except (ValueError, TypeError):
        return 25 # Retorna idade padrão em caso de erro

def obter_recomendacao_de_filme(idade_usuario: int, filmes_de_interesse: list) -> str:
    """
    Monta o prompt e consulta a IA do Gemini para obter uma recomendação de filme.
    Retorna apenas o título do filme recomendado.
    """
    if not filmes_de_interesse:
        prompt_parts = [
            f"Aja como um especialista em cinema. Recomende um filme popular para uma pessoa de {idade_usuario} anos. ",
            "Responda APENAS com o título do filme, sem nenhuma formatação ou texto adicional (ex: 'O Poderoso Chefão')."
        ]
    else:
        lista_filmes_str = ", ".join(filmes_de_interesse)
        prompt_parts = [
            "Aja como um especialista em cinema.",
            f"Baseado na lista de filmes que um usuário de {idade_usuario} anos gosta ({lista_filmes_str}), recomende UM outro filme que ele provavelmente vai gostar.",
            "O filme recomendado NÃO PODE estar na lista fornecida.",
            "Responda APENAS com o título do filme, sem nenhuma formatação ou texto adicional (ex: 'Clube da Luta')."
        ]

    try:
        response = model.generate_content(prompt_parts)
        # Limpa a resposta para garantir que temos apenas o título
        titulo_limpo = response.text.strip().replace("*", "")
        return titulo_limpo
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return "Não foi possível obter uma recomendação no momento."