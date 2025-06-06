import pandas as pd
from tkinter import Tk, filedialog
from repository.filmesCRUD import Filmes_CRUD

class Importar_filmes:
    def __init__(self):
        self.repository = Filmes_CRUD()

    def importar_excel(self):
        Tk().withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("Planilhas Excel", "*.xlsx")],
            title="Selecione a planilha de filmes"
        )
        if not file_path:
            print("Nenhum arquivo selecionado.")
            return

        try:
            df = pd.read_excel(file_path)
            with self.repository.conecta_banco as con:
                cursor = con.cursor()

                for i in range(len(df)):
                    # Processa gêneros
                    generos = []
                    for nome in str(df['generos'][i]).split(','):
                        nome = nome.strip()
                        if nome:
                            genero_id = self.repository.verificar_ou_gravar_id(cursor, 'generos', 'nome', nome)
                            generos.append(genero_id)

                    # Processa dublagens
                    dublagens = []
                    for idioma in str(df['dublagens_disponiveis'][i]).split(','):
                        idioma = idioma.strip()
                        if idioma:
                            dublagem_id = self.repository.verificar_ou_gravar_id(cursor, 'dublagens', 'idioma', idioma)
                            dublagens.append(dublagem_id)

                    # Processa legendas
                    legendas = []
                    for idioma in str(df['legendas_disponiveis'][i]).split(','):
                        idioma = idioma.strip()
                        if idioma:
                            legenda_id = self.repository.verificar_ou_gravar_id(cursor, 'legendas_disponiveis', 'idioma', idioma)
                            legendas.append(legenda_id)

                    # Processa elenco
                    elenco = []
                    for ator_papel in str(df['elenco'][i]).split(';'):
                        if '-' in ator_papel:
                            nome, papel = ator_papel.split('-', 1)
                            nome = nome.strip()
                            papel = papel.strip()
                            ator_id = self.repository.verificar_ou_gravar_id(cursor, 'atores', 'nome', nome)
                            elenco.append((ator_id, papel))

                    self.repository.incluir_filme(
                        cursor,
                        df['titulo'][i],
                        df['resumo'][i],
                        df['classificacao_indicativa'][i],
                        df['classificacao_IMDB'][i],
                        df['duracao_minutos'][i],
                        pd.to_datetime(df['data_de_lancamento'][i]).date(),
                        df['capa'][i],
                        generos,
                        dublagens,
                        legendas,
                        elenco
                    )

                con.commit()
                print("Importação concluída com sucesso!")

        except Exception as e:
            print("Erro ao importar filmes:", e) 