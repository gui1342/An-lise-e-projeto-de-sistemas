import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from perfil_do_usuario import Perfil

from login import TelaLogin
from telaprincipal import TelaBiblioteca
from cadastro import TelaCadastro
from gerenciador_sessao import carregar_id_usuario, fazer_logout, salvar_id_usuario
from repository.filme_repository import FilmeRepository 

class App(ttk.Window):
    def __init__(self):
        super().__init__("Cine Filmes", "superhero", resizable=(True, True))
        self.attributes('-zoomed', True)
        self.protocol("WM_DELETE_WINDOW", self.confirmar_saida)

        self.repository = FilmeRepository()
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=YES)
        
        self._verificar_sessao_e_iniciar()

    def _limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _verificar_sessao_e_iniciar(self):
        """Verifica se há sessão salva e decide qual tela mostrar."""
        user_id = carregar_id_usuario()
        if user_id:
            # Verifica se o perfil está completo
            if self.repository.verificar_perfil_completo(user_id):
                usuario = self.repository.buscar_usuario_por_id(user_id)
                self.mostrar_tela_biblioteca(usuario)
            else:
                # Se não estiver completo, chama a tela de cadastro
                usuario_incompleto = self.repository.buscar_usuario_por_id(user_id)
                self.mostrar_tela_cadastro(usuario_incompleto)
        else:
            self.mostrar_tela_login()

    def on_login_success(self, perfil_google):
        """Callback após o login. Salva o usuário e verifica o cadastro."""
        try:
            user_id_interno = self.repository.salvar_ou_atualizar_usuario(perfil_google)
            salvar_id_usuario(user_id_interno)
            self._verificar_sessao_e_iniciar() # Re-executa a verificação
        except Exception as e:
            messagebox.showerror("Erro no Login", f"Ocorreu um erro ao processar seu login: {e}")

    def on_cadastro_success(self, usuario: Perfil):
        """Callback após o cadastro. Mostra a tela da biblioteca."""
        self.mostrar_tela_biblioteca(usuario)

    def mostrar_tela_login(self):
        self._limpar_container()
        login_view = TelaLogin(self.container, on_login_success=self.on_login_success)
        login_view.pack(fill=BOTH, expand=YES)

    def mostrar_tela_cadastro(self, usuario: Perfil):
        """Constrói e exibe a tela para completar o cadastro."""
        self._limpar_container()
        cadastro_view = TelaCadastro(self.container, usuario, on_cadastro_success=self.on_cadastro_success)
        cadastro_view.pack(fill=BOTH, expand=YES)

    def mostrar_tela_biblioteca(self, usuario: Perfil):
        self._limpar_container()
        biblioteca_view = TelaBiblioteca(self.container, usuario_logado=usuario)
        biblioteca_view.pack(fill=BOTH, expand=YES)

    def confirmar_saida(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do Cine Filmes?"):
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
