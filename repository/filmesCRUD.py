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
            
            return [self._montar_filme_completo(cursor, filme) for filme in filmes]

    def buscar_por_id(self, filme_id: int) -> Optional[Dict[str, Any]]:
        """Busca um filme específico com todos seus relacionamentos."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM filmes WHERE id = ?', (filme_id,))
            filme = cursor.fetchone()
            
            if not filme:
                return None
                
            return self._montar_filme_completo(cursor, filme)

    def criar(self, filme_dados: Dict[str, Any]) -> Optional[int]:
        """
        Cria um novo filme com todos seus relacionamentos.
        Retorna o ID do filme criado ou None se já existir.
        """
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            # Verifica se já existe
            if self._filme_existe(cursor, filme_dados['titulo'], filme_dados['data_de_lancamento']):
                return None

            # Insere o filme
            filme_id = self._inserir_filme_base(cursor, filme_dados)
            
            # Insere relacionamentos
            self._inserir_relacionamentos(cursor, filme_id, filme_dados)
            
            return filme_id

    def atualizar(self, filme_id: int, filme_dados: Dict[str, Any]) -> bool:
        """
        Atualiza um filme e seus relacionamentos.
        Retorna True se a atualização foi bem sucedida.
        """
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            if not self._filme_existe_por_id(cursor, filme_id):
                return False

            # Atualiza dados básicos
            self._atualizar_filme_base(cursor, filme_id, filme_dados)
            
            # Atualiza relacionamentos
            self._remover_relacionamentos(cursor, filme_id)
            self._inserir_relacionamentos(cursor, filme_id, filme_dados)
            
            return True

    def deletar(self, filme_id: int) -> bool:
        """
        Deleta um filme e seus relacionamentos.
        Retorna True se a deleção foi bem sucedida.
        """
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            if not self._filme_existe_por_id(cursor, filme_id):
                return False

            self._remover_relacionamentos(cursor, filme_id)
            cursor.execute('DELETE FROM filmes WHERE id = ?', (filme_id,))
            
            return True

    # Métodos auxiliares privados
    def _montar_filme_completo(self, cursor, filme_tuple: tuple) -> Dict[str, Any]:
        """Monta um dicionário completo do filme com todos seus relacionamentos."""
        filme_id = filme_tuple[0]
        return {
            'id': filme_id,
            'titulo': filme_tuple[1],
            'resumo': filme_tuple[2],
            'classificacao_indicativa': filme_tuple[3],
            'classificacao_IMDB': filme_tuple[4],
            'duracao_minutos': filme_tuple[5],
            'data_de_lancamento': filme_tuple[6],
            'capa': filme_tuple[7],
            'generos': self._buscar_generos(cursor, filme_id),
            'dublagens': self._buscar_dublagens(cursor, filme_id),
            'legendas': self._buscar_legendas(cursor, filme_id),
            'elenco': self._buscar_elenco(cursor, filme_id)
        }

    def _filme_existe(self, cursor, titulo: str, data_lancamento: str) -> bool:
        """Verifica se um filme já existe pelo título e data de lançamento."""
        cursor.execute(
            'SELECT 1 FROM filmes WHERE titulo = ? AND data_de_lancamento = ?',
            (titulo, data_lancamento)
        )
        return cursor.fetchone() is not None

    def _filme_existe_por_id(self, cursor, filme_id: int) -> bool:
        """Verifica se um filme existe pelo ID."""
        cursor.execute('SELECT 1 FROM filmes WHERE id = ?', (filme_id,))
        return cursor.fetchone() is not None

    def _inserir_filme_base(self, cursor, filme_dados: Dict[str, Any]) -> int:
        """Insere os dados básicos do filme e retorna o ID."""
        cursor.execute('''
            INSERT INTO filmes (
                titulo, resumo, classificacao_indicativa, classificacao_IMDB,
                duracao_minutos, data_de_lancamento, capa
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            filme_dados['titulo'],
            filme_dados['resumo'],
            filme_dados['classificacao_indicativa'],
            filme_dados['classificacao_IMDB'],
            filme_dados['duracao_minutos'],
            filme_dados['data_de_lancamento'],
            filme_dados['capa']
        ))
        return cursor.lastrowid

    def _atualizar_filme_base(self, cursor, filme_id: int, filme_dados: Dict[str, Any]):
        """Atualiza os dados básicos do filme."""
        cursor.execute('''
            UPDATE filmes SET
                titulo = ?, resumo = ?, classificacao_indicativa = ?,
                classificacao_IMDB = ?, duracao_minutos = ?,
                data_de_lancamento = ?, capa = ?
            WHERE id = ?
        ''', (
            filme_dados['titulo'],
            filme_dados['resumo'],
            filme_dados['classificacao_indicativa'],
            filme_dados['classificacao_IMDB'],
            filme_dados['duracao_minutos'],
            filme_dados['data_de_lancamento'],
            filme_dados['capa'],
            filme_id
        ))

    def _inserir_relacionamentos(self, cursor, filme_id: int, filme_dados: Dict[str, Any]):
        """Insere todos os relacionamentos de um filme."""
        # Insere gêneros
        for genero in filme_dados['generos']:
            genero_id = self._verificar_ou_criar_id(cursor, 'generos', 'nome', genero)
            cursor.execute(
                'INSERT INTO filmes_generos (filme_id, genero_id) VALUES (?, ?)',
                (filme_id, genero_id)
            )

        # Insere dublagens
        for dublagem in filme_dados['dublagens']:
            dublagem_id = self._verificar_ou_criar_id(cursor, 'dublagens', 'idioma', dublagem)
            cursor.execute(
                'INSERT INTO filmes_dublagens (filme_id, dublagem_id) VALUES (?, ?)',
                (filme_id, dublagem_id)
            )

        # Insere legendas
        for legenda in filme_dados['legendas']:
            legenda_id = self._verificar_ou_criar_id(cursor, 'legendas_disponiveis', 'idioma', legenda)
            cursor.execute(
                'INSERT INTO filmes_legendas_disponiveis (filme_id, legendas_disponiveis_id) VALUES (?, ?)',
                (filme_id, legenda_id)
            )

        # Insere elenco
        for membro in filme_dados['elenco']:
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

    def _verificar_ou_criar_id(self, cursor, tabela: str, coluna: str, valor: str) -> int:
        """Verifica se um registro existe ou cria um novo, retornando o ID."""
        cursor.execute(f'SELECT id FROM {tabela} WHERE {coluna} = ?', (valor,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        cursor.execute(f'INSERT INTO {tabela} ({coluna}) VALUES (?)', (valor,))
        return cursor.lastrowid

    def _buscar_generos(self, cursor, filme_id: int) -> List[str]:
        """Busca os gêneros de um filme."""
        cursor.execute('''
            SELECT g.nome FROM generos g
            JOIN filmes_generos fg ON g.id = fg.genero_id
            WHERE fg.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_dublagens(self, cursor, filme_id: int) -> List[str]:
        """Busca as dublagens de um filme."""
        cursor.execute('''
            SELECT d.idioma FROM dublagens d
            JOIN filmes_dublagens fd ON d.id = fd.dublagem_id
            WHERE fd.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_legendas(self, cursor, filme_id: int) -> List[str]:
        """Busca as legendas de um filme."""
        cursor.execute('''
            SELECT l.idioma FROM legendas_disponiveis l
            JOIN filmes_legendas_disponiveis fl ON l.id = fl.legendas_disponiveis_id
            WHERE fl.filme_id = ?
        ''', (filme_id,))
        return [linha[0] for linha in cursor.fetchall()]

    def _buscar_elenco(self, cursor, filme_id: int) -> List[Dict[str, str]]:
        """Busca o elenco de um filme."""
        cursor.execute('''
            SELECT a.nome, e.papel FROM atores a
            JOIN elenco e ON a.id = e.ator_id
            WHERE e.filme_id = ?
        ''', (filme_id,))
        return [{'ator': nome, 'papel': papel} for nome, papel in cursor.fetchall()] 