from database.conecta_banco import conecta_banco

class Filmes_CRUD:
    def __init__(self):
        self.conecta_banco = conecta_banco()

    def listar_todos(self):
        with self.conecta_banco as con:
            cursor = con.cursor()
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
                    'generos': self._buscar_generos(cursor, filme_id),
                    'dublagens': self._buscar_dublagens(cursor, filme_id),
                    'legendas': self._buscar_legendas(cursor, filme_id),
                    'elenco': self._buscar_elenco(cursor, filme_id)
                }
                lista_filmes.append(dados_filme)
            
            return lista_filmes

    def _buscar_generos(self, cursor, filme_id):
        cursor.execute('''
            SELECT g.nome FROM generos g
            JOIN filmes_generos fg ON g.id = fg.genero_id
            WHERE fg.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_dublagens(self, cursor, filme_id):
        cursor.execute('''
            SELECT d.idioma FROM dublagens d
            JOIN filmes_dublagens fd ON d.id = fd.dublagem_id
            WHERE fd.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_legendas(self, cursor, filme_id):
        cursor.execute('''
            SELECT l.idioma FROM legendas_disponiveis l
            JOIN filmes_legendas_disponiveis fl ON l.id = fl.legendas_disponiveis_id
            WHERE fl.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_elenco(self, cursor, filme_id):
        cursor.execute('''
            SELECT a.nome, e.papel FROM atores a
            JOIN elenco e ON a.id = e.ator_id
            WHERE e.filme_id = ?
        ''', (filme_id,))
        return [{'ator': nome, 'papel': papel} for nome, papel in cursor.fetchall()]

    def verificar_ou_gravar_id(self, cursor, table, column, value):
        cursor.execute(f'SELECT id FROM {table} WHERE {column} = ?', (value,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute(f'INSERT INTO {table} ({column}) VALUES (?)', (value,))
        return cursor.lastrowid

    def incluir_filme(self, cursor, titulo, resumo, classificacao_indicativa,
                     classificacao_IMDB, duracao_minutos, data_de_lancamento,
                     capa, generos, dublagens_disponiveis, legendas_disponiveis,
                     elenco):
        
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