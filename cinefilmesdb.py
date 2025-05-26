import sqlite3

#cria o banco cine_filmes
def conecta():
    return sqlite3.connect('cine_filmes.db')

#Cria as tabelas do banco cine_filmes.db
def criar_tabelas():
    #cria conexao
    con = conecta()
    #cria cursor
    cursor = con.cursor()

    #cria a tabela de filmes
    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        resumo TEXT NOT NULL,
                        classificacao_indicativa INTEGER,
                        classificacao_IMDB REAL,
                        duracao_minutos INTEGER,
                        data_de_lancamento NUMERIC,
                        capa BLOB )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS generos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL UNIQUE )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes_generos (
                        filme_id INTEGER,
                        genero_id INTEGER,
                        FOREIGN KEY(filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
                        FOREIGN KEY(genero_id) REFERENCES generos(id) ON DELETE CASCADE,
                        PRIMARY KEY (filme_id, genero_id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS diretores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL UNIQUE )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes_diretores (
                        filme_id INTEGER,
                        diretor_id INTEGER,
                        FOREIGN KEY(filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
                        FOREIGN KEY(diretor_id) REFERENCES diretores(id) ON DELETE CASCADE,
                        PRIMARY KEY (filme_id, diretor_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS dublagens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        idioma TEXT NOT NULL UNIQUE )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes_dublagens (
                        filme_id INTEGER,
                        dublagem_id INTEGER,
                        FOREIGN KEY(filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
                        FOREIGN KEY(dublagem_id) REFERENCES dublagens(id) ON DELETE CASCADE,
                        PRIMARY KEY (filme_id, dublagem_id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS legendas_disponiveis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        idioma TEXT NOT NULL UNIQUE )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes_legendas_disponiveis (
                        filme_id INTEGER,
                        legendas_disponiveis_id INTEGER,
                        FOREIGN KEY(filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
                        FOREIGN KEY(legendas_disponiveis_id) REFERENCES legendas_disponiveis(id) ON DELETE CASCADE,
                        PRIMARY KEY (filme_id, legendas_disponiveis_id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS atores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL UNIQUE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS elenco (
                        filme_id INTEGER,
                        ator_id INTEGER,
                        papel TEXT,
                        FOREIGN KEY(filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
                        FOREIGN KEY(ator_id) REFERENCES atores(id) ON DELETE CASCADE,
                        PRIMARY KEY (filme_id, ator_id))''')
    
    #salva as alterações
    con.commit()
    #fecha a conexão
    con.close()

criar_tabelas()
