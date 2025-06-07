import pandas as pd
from tkinter import Tk, filedialog
from repository.filme_repository import FilmeRepository

class Importar_filmes:
    def __init__(self):
        self.repository = FilmeRepository()

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
            for i in range(len(df)):
                # Processa gêneros
                generos = [
                    nome.strip()
                    for nome in str(df['generos'][i]).split(',')
                    if nome.strip()
                ]

                # Processa dublagens
                dublagens = [
                    idioma.strip()
                    for idioma in str(df['dublagens_disponiveis'][i]).split(',')
                    if idioma.strip()
                ]

                # Processa legendas
                legendas = [
                    idioma.strip()
                    for idioma in str(df['legendas_disponiveis'][i]).split(',')
                    if idioma.strip()
                ]

                # Processa elenco
                elenco = []
                for ator_papel in str(df['elenco'][i]).split(';'):
                    if '-' in ator_papel:
                        nome, papel = ator_papel.split('-', 1)
                        elenco.append({
                            'ator': nome.strip(),
                            'papel': papel.strip()
                        })

                filme_dados = {
                    'titulo': df['titulo'][i],
                    'resumo': df['resumo'][i],
                    'classificacao_indicativa': df['classificacao_indicativa'][i],
                    'classificacao_IMDB': df['classificacao_IMDB'][i],
                    'duracao_minutos': df['duracao_minutos'][i],
                    'data_de_lancamento': pd.to_datetime(df['data_de_lancamento'][i]).date(),
                    'capa': df['capa'][i],
                    'generos': generos,
                    'dublagens': dublagens,
                    'legendas': legendas,
                    'elenco': elenco
                }

                try:
                    self.repository.criar(filme_dados)
                    print(f"Filme '{filme_dados['titulo']}' importado com sucesso!")
                except ValueError as e:
                    print(f"Aviso: {str(e)}")

            print("Importação concluída!")

        except Exception as e:
            print("Erro ao importar filmes:", e) 