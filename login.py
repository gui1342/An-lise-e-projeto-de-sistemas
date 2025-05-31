import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys


# Caminho para acessar o login_com_google
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from telas.cadastro import TelaCadastro
from login_com_google_adapter import *

class TelaLogin(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master, padding=(20, 10))
        self.master = master
        self.on_login_success = on_login_success
        self.pack(fill=BOTH, expand=YES)

        master.protocol("WM_DELETE_WINDOW", self.confirmar_saida)

        # Header
        ttk.Label(
            master=self,
            text="Para entrar no Cine Filmes é necessário fazer login:",
            font="-size 12",
            anchor="center"
        ).pack(pady=(10, 5), fill=X)

        ttk.Label(
            master=self,
            text="Você será redirecionado para o navegador",
            font="-size 10",
            anchor="center"
        ).pack(pady=(0, 20), fill=X)

        # Botão de login com imagem
        self.botao_login_google()

    def botao_login_google(self):
        container = ttk.Frame(self)
        container.pack()

        # Caminho da imagem
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(script_dir, "google_logo.png")

        # Carrega imagem
        try:
            imagem = Image.open(img_path).resize((20, 20))
            logo = ImageTk.PhotoImage(imagem)
        except FileNotFoundError:
            print("Imagem 'google_logo.png' não encontrada!")
            logo = None

        # Cria botão com a logo
        botao = ttk.Button(
            master=container,
            text=" Entrar com Google",
            image=logo,
            compound=LEFT,
            bootstyle=INFO,
            command=self.realizar_login,
            width=30
        )
        botao.image = logo  # mantém referência
        botao.pack(pady=10)

    def realizar_login(self):
        adaptador = Login_com_google_adapter()       # cria a instância da classe adaptadora
        perfil = adaptador.login()           # chama o método de login

        if perfil:
            self.destroy()
            self.on_login_success(perfil)    # envia o objeto Perfil
        else:
            messagebox.showerror("Erro", "O login falhou ou foi cancelado.")

    def confirmar_saida(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.master.destroy()



if __name__ == "__main__":
    app = ttk.Window("Login - Cine Filmes", "superhero", resizable=(False, False))

    def mostrar_tela_cadastro(dados):
        TelaCadastro(app, dados)

    TelaLogin(app, on_login_success=mostrar_tela_cadastro)
    app.mainloop()