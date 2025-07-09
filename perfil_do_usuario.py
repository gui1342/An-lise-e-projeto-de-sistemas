class Perfil:
    def __init__(self, google_id: str, nome: str, email: str, foto_url: str, id_banco: int = None, tipo_perfil: str = "Padrão", data_nascimento: str = None):
        self.id = id_banco             
        self.google_id = google_id       
        self.nome_completo = nome
        self.email = email
        self.foto = foto_url             
        self.tipo_perfil = tipo_perfil
        self.data_nascimento = data_nascimento
