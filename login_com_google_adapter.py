from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import id_token
from google.auth.transport import requests 
from login_interface import login_adapter
from perfil_do_usuario import Perfil

class Login_com_google_adapter(login_adapter):
    def login(self):
        # Cria o fluxo de autenticação baseado no arquivo de credenciais e nas permissões (escopos) necessárias
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_11884206682-9eda8fnqvj1f2ua462ps1vegdk30619r.apps.googleusercontent.com.json',
            scopes=[
                'openid',  # Necessário para obter o ID token
                'https://www.googleapis.com/auth/userinfo.email',  # Permite acesso ao e-mail do usuário
                'https://www.googleapis.com/auth/userinfo.profile'  # Permite acesso ao nome e foto do perfil
            ]
        )

        # Executa o servidor local para o login e espera o usuário autenticar no navegador
        credentials = flow.run_local_server(port=0)

        # Verifica e decodifica o ID Token retornado, validando com o cliente do app
        idinfo = id_token.verify_oauth2_token(
            credentials._id_token,          # Token a ser verificado
            requests.Request(),             # Objeto de requisição seguro
            audience=credentials.client_id  # Confirma que o token é destinado ao app correto
        )

        perfil = Perfil(
            nome=idinfo.get("name"),
            email=idinfo.get("email"),
            foto=idinfo.get("picture"),
            tipo_perfil="padrao",
        )

        return perfil