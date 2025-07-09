from typing import List, Dict, Any, Optional
from cinefilmesdb import conecta
import sqlite3
from perfil_do_usuario import Perfil

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

    def criar(self, cursor: sqlite3.Cursor, filme_dict: Dict[str, Any]) -> int:
        """
        Cria um novo filme com seus relacionamentos usando um cursor existente.
        Este método NÃO gerencia a transação; ele apenas executa os comandos.
        """
        # Verifica se o filme já existe
        cursor.execute(
            'SELECT id FROM filmes WHERE titulo = ? AND data_de_lancamento = ?',
            (filme_dict['titulo'], filme_dict['data_de_lancamento'].isoformat())
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
            filme_dict['data_de_lancamento'].isoformat(), # Salva a data como texto
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
        
    def atualizar_capa(self, filme_id: int, novo_caminho_capa: str) -> bool:
        """Atualiza APENAS o caminho da capa de um filme específico."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute(
                "UPDATE filmes SET capa = ? WHERE id = ?",
                (novo_caminho_capa, filme_id)
            )
            con.commit()
            # Retorna True se alguma linha foi alterada, False caso contrário
            return cursor.rowcount > 0

    # Adicione este método à sua classe Filmes_CRUD ou FilmeRepository

    def listar_todos_generos(self):
        """
        Busca e retorna uma lista com o nome de todos os gêneros
        disponíveis, ordenados alfabeticamente.
        """
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute('SELECT nome FROM generos ORDER BY nome')
            return [linha[0] for linha in cursor.fetchall()]

    def buscar_filmes_por_genero(self, nome_genero):
        """Busca e retorna uma lista de dicionários de filmes para um dado gênero."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT f.id, f.titulo, f.capa FROM filmes f
                JOIN filmes_generos fg ON f.id = fg.filme_id
                JOIN generos g ON g.id = fg.genero_id
                WHERE g.nome = ?
                ORDER BY f.titulo
            ''', (nome_genero,))
            
            filmes_do_genero = []
            for filme in cursor.fetchall():
                filmes_do_genero.append({
                    'id': filme[0],
                    'titulo': filme[1],
                    'capa': filme[2]
                })
            return filmes_do_genero

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

    #gerencia o login no banco de dados
    def salvar_ou_atualizar_usuario(self, perfil:Perfil) -> int:
        """
        Verifica se um usuário existe pelo google_id.
        Se não existir, cria. Se existir, atualiza.
        Retorna o ID interno do usuário no banco de dados.
        """
        with self.conecta_banco as con:
            cursor = con.cursor()
            
            # Primeiro, verifica se o usuário já existe
            cursor.execute("SELECT id FROM usuarios WHERE google_id = ?", (perfil.google_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                # O usuário existe, então atualiza
                user_id = resultado[0]
                cursor.execute("""
                    UPDATE usuarios 
                    SET nome = ?, email = ?, foto_url = ?, ultimo_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (perfil.nome_completo, perfil.email, perfil.foto, user_id))
            else:
                # O usuário não existe, então insere
                cursor.execute("""
                    INSERT INTO usuarios (google_id, email, nome, foto_url, ultimo_login)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (perfil.google_id, perfil.email, perfil.nome_completo, perfil.foto))
                user_id = cursor.lastrowid
                
            con.commit()
            return user_id

    def buscar_usuario_por_id(self, user_id: int) -> Perfil | None:
        """Busca os dados de um usuário pelo seu ID interno e retorna um objeto Perfil"""
        with self.conecta_banco as con:
            con.row_factory = sqlite3.Row # Permite acessar colunas por nome
            cursor = con.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            
            if not user_row:
                return None
            
        # Cria e retorna uma instância da classe Perfil
        return Perfil(
            id_banco=user_row['id'],
            google_id=user_row['google_id'],
            nome=user_row['nome'],
            email=user_row['email'],
            foto_url=user_row['foto_url'],
            data_nascimento=user_row['data_nascimento']
        )
    
    def verificar_perfil_completo(self, usuario_id: int) -> bool:
        """Verifica se o usuário já tem uma data de nascimento cadastrada."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute("SELECT data_nascimento FROM usuarios WHERE id = ?", (usuario_id,))
            resultado = cursor.fetchone()
            return resultado is not None and resultado[0] is not None

    def atualizar_data_nascimento(self, usuario_id: int, data_nascimento: str):
        """Atualiza a data de nascimento de um usuário específico."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute(
                "UPDATE usuarios SET data_nascimento = ? WHERE id = ?",
                (data_nascimento, usuario_id)
            )
            con.commit()

    def verificar_interesse(self, usuario_id, filme_id):
        """Verifica se um filme já está na lista de interesses do usuário."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            cursor.execute("SELECT 1 FROM interesses_usuario WHERE usuario_id = ? AND filme_id = ?", (usuario_id, filme_id))
            resultado = cursor.fetchone()
            return resultado is not None

    def alternar_interesse(self, usuario_id, filme_id):
        """Adiciona o filme aos interesses se não estiver, ou remove se já estiver.
        Retorna o novo estado (True se agora tem interesse, False se não tem)."""
        tem_interesse = self.verificar_interesse(usuario_id, filme_id)
        with self.conecta_banco as con:
            cursor = con.cursor()
            if tem_interesse:
                cursor.execute("DELETE FROM interesses_usuario WHERE usuario_id = ? AND filme_id = ?", (usuario_id, filme_id))
                novo_estado = False
            else:
                cursor.execute("INSERT INTO interesses_usuario (usuario_id, filme_id) VALUES (?, ?)", (usuario_id, filme_id))
                novo_estado = True
            con.commit()
            return novo_estado

    def listar_interesses_por_usuario(self, usuario_id):
        """Retorna uma lista com os títulos dos filmes de interesse de um usuário."""
        with self.conecta_banco as con:
            cursor = con.cursor()
            # Junta as tabelas para pegar o título do filme diretamente
            cursor.execute("""
                SELECT f.titulo FROM filmes f
                JOIN interesses_usuario iu ON f.id = iu.filme_id
                WHERE iu.usuario_id = ?
            """, (usuario_id,))
            filmes = [row[0] for row in cursor.fetchall()]
            return filmes