import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, StringVar, INSERT
from datetime import datetime


class TelaCadastro(ttk.Frame):
    def __init__(self, master, dados_usuario):
        super().__init__(master, padding=(20, 10))
        self.pack(fill=BOTH, expand=YES)

        ttk.Label(
            self, text="Complete seu cadastro:", font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(10, 10))

        # Exibe dados obtidos
        ttk.Label(self, text=f"Nome: {dados_usuario.get('nome', 'Não disponível')}").pack(pady=5, fill=X)
        ttk.Label(self, text=f"Email: {dados_usuario.get('email', 'Não disponível')}").pack(pady=5, fill=X)

        # Campo para confirmar a data de nascimento
        self.aniversario_var = StringVar()
        self.criar_aniversario(self)

        # Botão para finalizar cadastro
        ttk.Button(
            self,
            text="Finalizar Cadastro",
            bootstyle=SUCCESS,
            command=self.finalizar_cadastro
        ).pack(pady=15, fill=X)


    def formatar_aniversario(self, entrada_var):
        entrada = self.aniversario_entry
        texto = entrada_var.get()
        novo_texto = ''
        numeros = ''.join(filter(str.isdigit, texto))
        cursor_pos = entrada.index(INSERT) # Obtém a posição atual do cursor

        if len(numeros) > 0:
            if len(numeros) <= 2:
                novo_texto = numeros
            elif len(numeros) <= 4:
                novo_texto = f"{numeros[:2]}/{numeros[2:]}"
            elif len(numeros) <= 6:
                novo_texto = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
            elif len(numeros) <= 8:
                novo_texto = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:8]}"
            else:
                novo_texto = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:8]}"

        entrada_var.set(novo_texto)

        # Ajusta a posição do cursor
        if len(novo_texto) < len(texto):
            # Se uma barra foi inserida, move o cursor para depois dela
            if len(numeros) == 2 or len(numeros) == 4:
                entrada.icursor(cursor_pos + 1)
            else:
                entrada.icursor(cursor_pos)
        elif len(novo_texto) > len(texto):
            # Se um dígito foi adicionado após uma barra, mantém a posição
            entrada.icursor(cursor_pos + 1)
        else:
            entrada.icursor(cursor_pos)

    def criar_aniversario(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill=X, expand=YES, pady=5)
        ttk.Label(container, text="Confirme seu nascimento:", width=20).pack(side=LEFT)
        # Campo de entrada para digitar o aniversário
        self.aniversario_entry = ttk.Entry(container, textvariable=self.aniversario_var)
        self.aniversario_entry.pack(side=LEFT, fill=X, expand=YES)
        # Ativa a formatação automática
        self.aniversario_entry.bind("<KeyRelease>", lambda event: self.formatar_aniversario(self.aniversario_var))

    def finalizar_cadastro(self):
        aniversario = self.aniversario_var.get()

        if not aniversario:
            messagebox.showwarning("Aviso", "Por favor, insira sua data de nascimento!")
            return

        try:
            datetime.strptime(aniversario, '%d/%m/%Y')
            messagebox.showinfo("Sucesso", f"Cadastro finalizado com sucesso!")
            self.destroy()  # Fecha a tela de cadastro
        except ValueError:
            messagebox.showwarning("Aviso", "Formato de data inválido. Use DD/MM/AAAA.")
