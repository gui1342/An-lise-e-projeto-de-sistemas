from typing import List, Dict, Any, Optional
from cinefilmesdb import conecta

class FilmeRepository:
    """
    Repositório para gerenciar operações de filmes no banco de dados.
    Implementa o padrão Repository para isolar a camada de dados.
    """
    
    def __init__(self):
        self.conecta_banco = conecta()

    def listar_todos(self) -> List[Dict[str, Any]]:
        """Lista todos os filmes com seus relacionamentos."""
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

    def buscar_por_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Busca um filme específico com seus relacionamentos."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM filmes WHERE id = ?', (id,))
            filme = cursor.fetchone()
            
            if not filme:
                return None
            
            return {
                'id': filme[0],
                'titulo': filme[1],
                'resumo': filme[2],
                'classificacao_indicativa': filme[3],
                'classificacao_IMDB': filme[4],
                'duracao_minutos': filme[5],
                'data_de_lancamento': filme[6],
                'capa': filme[7],
                'generos': self._buscar_generos(cursor, filme[0]),
                'dublagens': self._buscar_dublagens(cursor, filme[0]),
                'legendas': self._buscar_legendas(cursor, filme[0]),
                'elenco': self._buscar_elenco(cursor, filme[0])
            }

    def criar(self, filme_dict: Dict[str, Any]) -> int:
        """Cria um novo filme com seus relacionamentos."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            # Verifica se o filme já existe
            cursor.execute(
                'SELECT id FROM filmes WHERE titulo = ? AND data_de_lancamento = ?',
                (filme_dict['titulo'], filme_dict['data_de_lancamento'])
            )
            if cursor.fetchone():
                raise ValueError(f'Filme "{filme_dict["titulo"]}" já cadastrado.')

            # Insere o filme
            cursor.execute('''
                INSERT INTO filmes (titulo, resumo, classificacao_indicativa,
                                  classificacao_IMDB, duracao_minutos,
                                  data_de_lancamento, capa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                filme_dict['titulo'],
                filme_dict['resumo'],
                filme_dict['classificacao_indicativa'],
                filme_dict['classificacao_IMDB'],
                filme_dict['duracao_minutos'],
                filme_dict['data_de_lancamento'],
                filme_dict['capa']
            ))
            filme_id = cursor.lastrowid

            # Insere os relacionamentos
            self._inserir_generos(cursor, filme_id, filme_dict['generos'])
            self._inserir_dublagens(cursor, filme_id, filme_dict['dublagens'])
            self._inserir_legendas(cursor, filme_id, filme_dict['legendas'])
            self._inserir_elenco(cursor, filme_id, filme_dict['elenco'])

            return filme_id

    def atualizar(self, id: int, filme_dict: Dict[str, Any]) -> bool:
        """Atualiza um filme e seus relacionamentos."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            # Atualiza os dados básicos do filme
            cursor.execute('''
                UPDATE filmes
                SET titulo = ?, resumo = ?, classificacao_indicativa = ?,
                    classificacao_IMDB = ?, duracao_minutos = ?,
                    data_de_lancamento = ?, capa = ?
                WHERE id = ?
            ''', (
                filme_dict['titulo'],
                filme_dict['resumo'],
                filme_dict['classificacao_indicativa'],
                filme_dict['classificacao_IMDB'],
                filme_dict['duracao_minutos'],
                filme_dict['data_de_lancamento'],
                filme_dict['capa'],
                id
            ))
            
            if cursor.rowcount == 0:
                return False

            # Remove relacionamentos antigos
            self._remover_relacionamentos(cursor, id)

            # Insere novos relacionamentos
            self._inserir_generos(cursor, id, filme_dict['generos'])
            self._inserir_dublagens(cursor, id, filme_dict['dublagens'])
            self._inserir_legendas(cursor, id, filme_dict['legendas'])
            self._inserir_elenco(cursor, id, filme_dict['elenco'])

            return True

    def deletar(self, id: int) -> bool:
        """Deleta um filme e seus relacionamentos."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            # Remove relacionamentos
            self._remover_relacionamentos(cursor, id)
            
            # Remove o filme
            cursor.execute('DELETE FROM filmes WHERE id = ?', (id,))
            return cursor.rowcount > 0

    # Métodos auxiliares para buscar relacionamentos
    def _buscar_generos(self, cursor, filme_id: int) -> List[str]:
        cursor.execute('''
            SELECT g.nome FROM generos g
            JOIN filmes_generos fg ON g.id = fg.genero_id
            WHERE fg.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_dublagens(self, cursor, filme_id: int) -> List[str]:
        cursor.execute('''
            SELECT d.idioma FROM dublagens d
            JOIN filmes_dublagens fd ON d.id = fd.dublagem_id
            WHERE fd.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_legendas(self, cursor, filme_id: int) -> List[str]:
        cursor.execute('''
            SELECT l.idioma FROM legendas_disponiveis l
            JOIN filmes_legendas_disponiveis fl ON l.id = fl.legendas_disponiveis_id
            WHERE fl.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_elenco(self, cursor, filme_id: int) -> List[Dict[str, str]]:
        cursor.execute('''
            SELECT a.nome, e.papel FROM atores a
            JOIN elenco e ON a.id = e.ator_id
            WHERE e.filme_id = ?
        ''', (filme_id,))
        return [{'ator': nome, 'papel': papel} for nome, papel in cursor.fetchall()]

    # Métodos auxiliares para manipular relacionamentos
    def _verificar_ou_criar_id(self, cursor, tabela: str, coluna: str, valor: str) -> int:
        cursor.execute(f'SELECT id FROM {tabela} WHERE {coluna} = ?', (valor,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        cursor.execute(f'INSERT INTO {tabela} ({coluna}) VALUES (?)', (valor,))
        return cursor.lastrowid

    def _inserir_generos(self, cursor, filme_id: int, generos: List[str]):
        for genero in generos:
            genero_id = self._verificar_ou_criar_id(cursor, 'generos', 'nome', genero)
            cursor.execute(
                'INSERT INTO filmes_generos (filme_id, genero_id) VALUES (?, ?)',
                (filme_id, genero_id)
            )

    def _inserir_dublagens(self, cursor, filme_id: int, dublagens: List[str]):
        for dublagem in dublagens:
            dublagem_id = self._verificar_ou_criar_id(cursor, 'dublagens', 'idioma', dublagem)
            cursor.execute(
                'INSERT INTO filmes_dublagens (filme_id, dublagem_id) VALUES (?, ?)',
                (filme_id, dublagem_id)
            )

    def _inserir_legendas(self, cursor, filme_id: int, legendas: List[str]):
        for legenda in legendas:
            legenda_id = self._verificar_ou_criar_id(cursor, 'legendas_disponiveis', 'idioma', legenda)
            cursor.execute(
                'INSERT INTO filmes_legendas_disponiveis (filme_id, legendas_disponiveis_id) VALUES (?, ?)',
                (filme_id, legenda_id)
            )

    def _inserir_elenco(self, cursor, filme_id: int, elenco: List[Dict[str, str]]):
        for membro in elenco:
            ator_id = self._verificar_ou_criar_id(cursor, 'atores', 'nome', membro['ator'])
            cursor.execute(
                'INSERT INTO elenco (filme_id, ator_id, papel) VALUES (?, ?, ?)',
                (filme_id, ator_id, membro['papel'])
            )

    def _remover_relacionamentos(self, cursor, filme_id: int):
        """Remove todos os relacionamentos de um filme."""
        cursor.execute('DELETE FROM filmes_generos WHERE filme_id = ?', (filme_id,))
        cursor.execute('DELETE FROM filmes_dublagens WHERE filme_id = ?', (filme_id,))
        cursor.execute('DELETE FROM filmes_legendas_disponiveis WHERE filme_id = ?', (filme_id,))
        cursor.execute('DELETE FROM elenco WHERE filme_id = ?', (filme_id,)) 