# gerenciador_sessao.py
import json
import os

ARQUIVO_SESSAO = 'sessao.json'

def salvar_id_usuario(user_id: int):
    """Salva o ID do usuário logado no arquivo de sessão."""
    with open(ARQUIVO_SESSAO, 'w') as f:
        json.dump({'user_id': user_id}, f)
    print(f"Sessão salva para o usuário ID: {user_id}")

def carregar_id_usuario() -> int | None:
    """Carrega o ID do usuário do arquivo de sessão, se existir."""
    if not os.path.exists(ARQUIVO_SESSAO):
        return None
    try:
        with open(ARQUIVO_SESSAO, 'r') as f:
            dados = json.load(f)
            return dados.get('user_id')
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def fazer_logout():
    """Apaga o arquivo de sessão."""
    if os.path.exists(ARQUIVO_SESSAO):
        os.remove(ARQUIVO_SESSAO)
        print("Sessão encerrada (logout).")