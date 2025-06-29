import pandas as pd
import logging
from datetime import datetime
from tkinter import Tk, filedialog, messagebox
from repository.filme_repository import FilmeRepository
from typing import Dict, List, Any, Optional
import sqlite3

class ValidacaoError(Exception):
    """Exceção personalizada para erros de validação"""
    pass

class TransacaoError(Exception):
    """Exceção personalizada para erros de transação"""
    pass

class Importar_filmes:
    def __init__(self):
        self.repository = FilmeRepository()
        self._configurar_logging()

    def _configurar_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            filename=f'importacao_filmes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _validar_campos_obrigatorios(self, dados: pd.Series) -> None:
        """Valida se todos os campos obrigatórios estão preenchidos"""
        campos_obrigatorios = ['titulo', 'classificacao_indicativa', 'duracao_minutos', 'data_de_lancamento']
        for campo in campos_obrigatorios:
            if pd.isna(dados[campo]) or str(dados[campo]).strip() == '':
                raise ValidacaoError(f"Campo obrigatório '{campo}' não preenchido")

    def _validar_classificacao_indicativa(self, classificacao: Any) -> int:
        """Valida e converte a classificação indicativa"""
        try:
            classificacao = int(classificacao)
            if classificacao not in [0, 10, 12, 14, 16, 18]:
                raise ValidacaoError(f"Classificação indicativa inválida: {classificacao}")
            return classificacao
        except (ValueError, TypeError):
            raise ValidacaoError(f"Classificação indicativa deve ser um número: {classificacao}")

    def _validar_classificacao_imdb(self, classificacao: Any) -> float:
        """Valida e converte a classificação IMDB"""
        try:
            classificacao = float(classificacao)
            if not (0 <= classificacao <= 10):
                raise ValidacaoError(f"Classificação IMDB deve estar entre 0 e 10: {classificacao}")
            return classificacao
        except (ValueError, TypeError):
            raise ValidacaoError(f"Classificação IMDB deve ser um número: {classificacao}")

    def _validar_duracao(self, duracao: Any) -> int:
        """Valida e converte a duração do filme"""
        try:
            duracao = int(duracao)
            if duracao <= 0:
                raise ValidacaoError(f"Duração deve ser maior que zero: {duracao}")
            return duracao
        except (ValueError, TypeError):
            raise ValidacaoError(f"Duração deve ser um número inteiro: {duracao}")

    def _validar_data_lancamento(self, data: Any) -> datetime.date:
        """Valida e converte a data de lançamento"""
        try:
            if isinstance(data, str):
                data = pd.to_datetime(data)
            return pd.to_datetime(data).date()
        except Exception:
            raise ValidacaoError(f"Data de lançamento inválida: {data}")

    def _processar_lista_strings(self, valor: str, separador: str = ',') -> List[str]:
        """Processa uma string em uma lista de valores, removendo espaços e valores vazios"""
        if pd.isna(valor):
            return []
        return [item.strip() for item in str(valor).split(separador) if item.strip()]

    def _processar_elenco(self, elenco_str: str) -> List[Dict[str, str]]:
        """Processa a string de elenco em uma lista de dicionários"""
        if pd.isna(elenco_str):
            return []
        
        elenco = []
        for ator_papel in str(elenco_str).split(';'):
            if '-' not in ator_papel:
                logging.warning(f"Formato inválido de elenco ignorado: {ator_papel}")
                continue
                
            nome, papel = ator_papel.split('-', 1)
            nome = nome.strip()
            papel = papel.strip()
            
            if nome and papel:
                elenco.append({'ator': nome, 'papel': papel})
            else:
                logging.warning(f"Entrada de elenco ignorada - nome ou papel vazio: {ator_papel}")
                
        return elenco

    def _preparar_dados_filme(self, dados: pd.Series) -> Dict[str, Any]:
        """Prepara e valida os dados do filme"""
        try:
            self._validar_campos_obrigatorios(dados)
            
            return {
                'titulo': str(dados['titulo']).strip(),
                'resumo': str(dados['resumo']).strip() if not pd.isna(dados['resumo']) else '',
                'classificacao_indicativa': self._validar_classificacao_indicativa(dados['classificacao_indicativa']),
                'classificacao_IMDB': self._validar_classificacao_imdb(dados['classificacao_IMDB']),
                'duracao_minutos': self._validar_duracao(dados['duracao_minutos']),
                'data_de_lancamento': self._validar_data_lancamento(dados['data_de_lancamento']),
                'capa': str(dados['capa']).strip() if not pd.isna(dados['capa']) else '',
                'generos': self._processar_lista_strings(dados['generos']),
                'dublagens': self._processar_lista_strings(dados['dublagens_disponiveis']),
                'legendas': self._processar_lista_strings(dados['legendas_disponiveis']),
                'elenco': self._processar_elenco(dados['elenco'])
            }
        except ValidacaoError as e:
            raise ValidacaoError(f"Erro nos dados do filme '{dados['titulo']}': {str(e)}")
        except Exception as e:
            raise ValidacaoError(f"Erro inesperado ao processar filme '{dados['titulo']}': {str(e)}")

    def _executar_transacao(self, filme_dados: Dict[str, Any], conexao: sqlite3.Connection) -> bool:
        """
        Executa uma transação para inserir um filme e seus relacionamentos.
        Retorna True se a transação foi bem sucedida, False caso contrário.
        """
        try:
            # Inicia a transação
            conexao.execute("BEGIN TRANSACTION")
            cursor = conexao.cursor()
            
            # Tenta criar o filme
            self.repository.criar(cursor, filme_dados)
            
            # Se chegou até aqui, confirma a transação
            #conexao.execute("COMMIT")
            conexao.commit()
            logging.info(f"Transação concluída com sucesso para o filme: {filme_dados['titulo']}")
            return True
            
        except Exception as e:
            # Em caso de erro, desfaz a transação
            conexao.execute("ROLLBACK")
            logging.error(f"Erro na transação do filme {filme_dados['titulo']}: {str(e)}")
            raise TransacaoError(f"Erro ao processar filme {filme_dados['titulo']}: {str(e)}")

    def importar_excel(self):
        """Importa filmes de um arquivo Excel com controle de transação"""
        Tk().withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("Planilhas Excel", "*.xlsx")],
            title="Selecione a planilha de filmes"
        )
        
        if not file_path:
            logging.info("Importação cancelada: Nenhum arquivo selecionado")
            print("Nenhum arquivo selecionado.")
            return

        logging.info(f"Iniciando importação do arquivo: {file_path}")
        sucessos = 0
        falhas = 0

        try:
            df = pd.read_excel(file_path)
            total_registros = len(df)
            logging.info(f"Total de registros encontrados: {total_registros}")

            # Obtém uma conexão com o banco de dados
            with self.repository.conecta_banco as conexao:
                for i in range(total_registros):
                    try:
                        filme_dados = self._preparar_dados_filme(df.iloc[i])
                        
                        # Executa a transação para este filme
                        self._executar_transacao(filme_dados, conexao)
                        
                        sucessos += 1
                        logging.info(f"Filme importado com sucesso: {filme_dados['titulo']}")
                        print(f"Filme '{filme_dados['titulo']}' importado com sucesso!")
                        
                    except ValidacaoError as e:
                        falhas += 1
                        logging.error(str(e))
                        print(f"Erro de validação: {str(e)}")
                        continue
                        
                    except TransacaoError as e:
                        falhas += 1
                        logging.error(str(e))
                        print(f"Erro na transação: {str(e)}")
                        continue
                        
                    except Exception as e:
                        falhas += 1
                        logging.error(f"Erro inesperado: {str(e)}")
                        print(f"Erro inesperado: {str(e)}")
                        continue

            mensagem_final = (
                f"Importação concluída!\n"
                f"Sucessos: {sucessos}\n"
                f"Falhas: {falhas}\n"
                f"Total: {total_registros}"
            )
            
            logging.info(mensagem_final.replace('\n', ' - '))
            messagebox.showinfo("Resultado da Importação", mensagem_final)

        except Exception as e:
            erro = f"Erro ao ler arquivo Excel: {str(e)}"
            logging.error(erro)
            messagebox.showerror("Erro", erro) 
if __name__ == "__main__":
    importar = Importar_filmes()
    importar.importar_excel()