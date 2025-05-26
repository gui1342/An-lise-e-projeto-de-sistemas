import pandas as pd
import sqlite3
from tkinter import filedialog, messagebox, filedialog, Tk

def conect():
    return sqlite3.connect('cine_filmes.db')


def listar_filmes():
    con = conect()
    cursor = con.cursor()

    # Busca todos os filmes
    cursor.execute('SELECT * FROM filmes')
    filmes = cursor.fetchall()

    lista_filmes = []

    for filme in filmes:
        filme_id = filme[0]
        dados_filme = {
            'id': filme_id,
            'titulo': filme[1],
            'resumo': filme[2],
            'classificacao_indicativa': filme[3],
            'classificacao_IMDB': filme[4],
            'duracao_minutos': filme[5],
            'data_de_lancamento': filme[6],
            'capa': filme[7],
            'generos': [],
            'dublagens': [],
            'legendas': [],
            'elenco': []
        }

        # Busca gêneros
        cursor.execute('''
            SELECT g.nome FROM generos g
            JOIN filmes_generos fg ON g.id = fg.genero_id
            WHERE fg.filme_id = ?
        ''', (filme_id,))
        dados_filme['generos'] = [linha[0] for linha in cursor.fetchall()]

        # Busca dublagens
        cursor.execute('''
            SELECT d.idioma FROM dublagens d
            JOIN filmes_dublagens fd ON d.id = fd.dublagem_id
            WHERE fd.filme_id = ?
        ''', (filme_id,))
        dados_filme['dublagens'] = [linha[0] for linha in cursor.fetchall()]

        # Busca legendas
        cursor.execute('''
            SELECT l.idioma FROM legendas_disponiveis l
            JOIN filmes_legendas_disponiveis fl ON l.id = fl.legendas_disponiveis_id
            WHERE fl.filme_id = ?
        ''', (filme_id,))
        dados_filme['legendas'] = [linha[0] for linha in cursor.fetchall()]

        # Busca elenco
        cursor.execute('''
            SELECT a.nome, e.papel FROM atores a
            JOIN elenco e ON a.id = e.ator_id
            WHERE e.filme_id = ?
        ''', (filme_id,))
        dados_filme['elenco'] = [{'ator': nome, 'papel': papel} for nome, papel in cursor.fetchall()]

        lista_filmes.append(dados_filme)

    con.close()
    return lista_filmes


def verificar_ou_gravar_id(cursor, table, column, value):
    cursor.execute(f'SELECT id FROM {table} WHERE {column} = ?', (value,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f'INSERT INTO {table} ({column}) VALUES (?)', (value,))
    return cursor.lastrowid

def incluir_filme(cursor, titulo, resumo, classificacao_indicativa,
                  classificacao_IMDB, duracao_minutos, data_de_lancamento,
                  capa, generos, dublagens_disponiveis, legendas_disponiveis,
                  elenco):

    # Verifica se o filme já existe pelo título e data de lançamento (exemplo)
    cursor.execute('SELECT id FROM filmes WHERE titulo = ? AND data_de_lancamento = ?', 
                   (titulo, data_de_lancamento))
    if cursor.fetchone():
        print(f'Filme "{titulo}" já cadastrado. Pulando...')
        return

    cursor.execute('''
        INSERT INTO filmes (titulo, resumo, classificacao_indicativa, classificacao_IMDB,
                            duracao_minutos, data_de_lancamento, capa)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, resumo, classificacao_indicativa, classificacao_IMDB, duracao_minutos,
          data_de_lancamento, capa))

    filme_id = cursor.lastrowid

    for genero_id in generos:
        cursor.execute('INSERT INTO filmes_generos (filme_id, genero_id) VALUES (?, ?)', 
                       (filme_id, genero_id))

    for dublagem_id in dublagens_disponiveis:
        cursor.execute('INSERT INTO filmes_dublagens (filme_id, dublagem_id) VALUES (?, ?)', 
                       (filme_id, dublagem_id))

    for legenda_id in legendas_disponiveis:
        cursor.execute('INSERT INTO filmes_legendas_disponiveis (filme_id, legendas_disponiveis_id) VALUES (?, ?)', 
                       (filme_id, legenda_id))

    for ator_id, papel in elenco:
        cursor.execute('INSERT INTO elenco (filme_id, ator_id, papel) VALUES (?, ?, ?)', 
                       (filme_id, ator_id, papel))

def importar_filmes_excel():
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
        con = conect()
        cursor = con.cursor()

        for _, row in df.iterrows():
            titulo = row['titulo']
            resumo = row['resumo']
            classificacao_indicativa = row['classificacao_indicativa']
            classificacao_IMDB = row['classificacao_IMDB']
            duracao_minutos = row['duracao_minutos']
            data_de_lancamento = pd.to_datetime(row['data_de_lancamento']).date()
            capa = row['capa']  # Pode ser BLOB ou caminho, ajuste conforme necessidade

            # Gêneros
            generos = []
            for nome in str(row['generos']).split(','):
                nome = nome.strip()
                if nome:
                    genero_id = verificar_ou_gravar_id(cursor, 'generos', 'nome', nome)
                    generos.append(genero_id)

            # Dublagens
            dublagens_disponiveis = []
            for idioma in str(row['dublagens_disponiveis']).split(','):
                idioma = idioma.strip()
                if idioma:
                    dublagem_id = verificar_ou_gravar_id(cursor, 'dublagens', 'idioma', idioma)
                    dublagens_disponiveis.append(dublagem_id)

            # Legendas
            legendas_disponiveis = []
            for idioma in str(row['legendas_disponiveis']).split(','):
                idioma = idioma.strip()
                if idioma:
                    legenda_id = verificar_ou_gravar_id(cursor, 'legendas_disponiveis', 'idioma', idioma)
                    legendas_disponiveis.append(legenda_id)

            # Elenco
            elenco = []
            for ator_papel in str(row['elenco']).split(';'):
                if '-' in ator_papel:
                    nome, papel = ator_papel.split('-', 1)
                    nome = nome.strip()
                    papel = papel.strip()
                    ator_id = verificar_ou_gravar_id(cursor, 'atores', 'nome', nome)
                    elenco.append((ator_id, papel))

            incluir_filme(cursor, titulo, resumo, classificacao_indicativa,
                          classificacao_IMDB, duracao_minutos, data_de_lancamento,
                          capa, generos, dublagens_disponiveis,
                          legendas_disponiveis, elenco)

        con.commit()
        con.close()
        print("Importação concluída com sucesso!")

    except Exception as e:
        print("Erro ao importar filmes:", e)

#importar_filmes_excel()
lista = listar_filmes()
for itens in lista:
    print(itens)