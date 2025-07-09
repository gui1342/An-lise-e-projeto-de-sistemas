import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage, HORIZONTAL, messagebox
from repository.filme_repository import FilmeRepository
from PIL import Image, ImageTk
from perfil_do_usuario import Perfil
from recomendacao_ia import obter_recomendacao_de_filme, calcular_idade

class TelaBiblioteca(ttk.Frame):
    def __init__(self, master, usuario_logado: Perfil):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)

        self.crud = FilmeRepository()
        self.photo_images = []
        self.usuario_logado = usuario_logado

        # Variável para controlar o estado do botão de interesse (marcado/desmarcado)
        self.interesse_var = ttk.BooleanVar()

        # --- ESTRUTURA DA TELA ---
        # Frame da Sidebar
        self.sidebar = ttk.Frame(self, width=200, bootstyle="secondary")
        self.sidebar.pack(side=LEFT, fill=Y)
        
        # Frame do Conteúdo Principal (que será rolável)
        # Este frame conterá o canvas e a scrollbar
        self.main_content_frame = ttk.Frame(self)
        self.main_content_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # --- FRAMES PARA NAVEGAÇÃO (dentro do conteúdo principal) ---
        # Estes são os "palcos" que vamos alternar
        self.library_frame = ttk.Frame(self.main_content_frame)
        self.details_frame = ttk.Frame(self.main_content_frame)

        # Constrói a interface inicial
        self._build_sidebar()
        self._build_library_view()

        # Mostra a tela da biblioteca por padrão
        self._show_frame(self.library_frame)


    def _show_frame(self, frame_to_show):
        """Esconde todos os frames no container principal e mostra apenas o desejado."""
        for frame in [self.library_frame, self.details_frame]:
            frame.pack_forget()
        frame_to_show.pack(fill=BOTH, expand=True)

    def _build_sidebar(self):
        """Constrói o conteúdo da barra lateral."""
        perfil = ttk.Frame(self.sidebar, padding=10)
        perfil.pack(fill=X)
        avatar = PhotoImage(width=50, height=50) # Placeholder
        ttk.Label(perfil, image=avatar, bootstyle="secondary").pack(side=LEFT)
        ttk.Label(perfil, text=f"Olá, {self.usuario_logado.nome_completo.split()[0]}", font=("TkDefaultFont", 12, "bold")).pack(padx=5)
        #BOTÃO DE RECOMENDAÇÃO
        btn_recomendar = ttk.Button(
            self.sidebar, 
            text=" Me Recomende um Filme!", 
            bootstyle="primary-outline",
            command=self._iniciar_recomendacao
        )
        btn_recomendar.pack(fill=X, padx=10, pady=10)

    def _build_library_view(self):
        """Constrói a tela principal com a lista de filmes por gênero."""
        # --- Estrutura de Rolagem Vertical ---
        canvas = ttk.Canvas(self.library_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(self.library_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollable_frame = ttk.Frame(canvas)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))

        # --- Preenchimento do Conteúdo ---
        lista_de_generos = self.crud.listar_todos_generos()
        for genero in lista_de_generos:
            filmes = self.crud.buscar_filmes_por_genero(genero)
            if not filmes: continue

            container_genero = ttk.Frame(scrollable_frame)
            container_genero.pack(fill='x', expand=True, padx=20, pady=10)
            ttk.Label(container_genero, text=genero, font=("TkDefaultFont", 11, "bold")).pack(anchor=NW, pady=(10, 0))
            
            canvas_filmes = ttk.Canvas(container_genero, height=200)
            h_scroll = ttk.Scrollbar(container_genero, orient=HORIZONTAL, command=canvas_filmes.xview)
            canvas_filmes.configure(xscrollcommand=h_scroll.set)
            canvas_filmes.pack(fill='x', pady=5)
            h_scroll.pack(fill='x')

            frame_interno_filmes = ttk.Frame(canvas_filmes)
            canvas_filmes.create_window((0, 0), window=frame_interno_filmes, anchor=NW)

            for filme_info in filmes:
                card = ttk.Frame(frame_interno_filmes, width=120, height=180, padding=5)
                card.pack(side=LEFT, padx=5, pady=10)
                card.pack_propagate(False)
                
                callback_detalhes = lambda event, f_id=filme_info['id']: self._exibir_detalhes_filme(f_id)
                
                try:
                    img_pil = Image.open(filme_info['capa'])
                    img_pil.thumbnail((120, 180))
                    img = ImageTk.PhotoImage(img_pil)
                    self.photo_images.append(img)
                    label_widget = ttk.Label(card, image=img, cursor="hand2")
                    label_widget.bind("<Button-1>", callback_detalhes)
                except Exception:
                    label_widget = ttk.Label(card, text=filme_info.get('titulo', 'Erro'), anchor=CENTER, wraplength=110, cursor="hand2")
                    label_widget.bind("<Button-1>", callback_detalhes)
                
                label_widget.pack(fill=BOTH, expand=True)
            
            frame_interno_filmes.update_idletasks()
            canvas_filmes.configure(scrollregion=canvas_filmes.bbox("all"))

    def _exibir_detalhes_filme(self, filme_id: int):
        """Busca os detalhes do filme e constrói a tela de detalhes."""
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Busca os detalhes completos no momento do clique.
        # O método buscar_por_id retorna um dicionário.
        filme = self.crud.buscar_por_id(filme_id)
        
        if not filme:
            ttk.Label(self.details_frame, text=f"Filme com ID {filme_id} não encontrado.").pack(pady=20)
            self._show_frame(self.details_frame)
            return

        btn_voltar = ttk.Button(self.details_frame, text="< Voltar", command=lambda: self._show_frame(self.library_frame), bootstyle="light-outline")
        btn_voltar.pack(anchor="nw", padx=20, pady=20)

        content_frame = ttk.Frame(self.details_frame)
        content_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        content_frame.columnconfigure(1, weight=1)

        frame_esquerda = ttk.Frame(content_frame)
        frame_esquerda.grid(row=0, column=0, sticky="n", padx=(0, 20))

        try:
            caminho_capa = filme.get('capa')
            if caminho_capa:
                img_pil = Image.open(caminho_capa)
                img_pil.thumbnail((240, 360))
                img = ImageTk.PhotoImage(img_pil)
                self.photo_images.append(img)
                ttk.Label(frame_esquerda, image=img).pack()
            else:
                raise ValueError("Caminho da capa está vazio")
        except Exception as e:
            print(f"Erro ao carregar capa do detalhe: {e}")
            ttk.Label(frame_esquerda, text="Capa Indisponível", bootstyle="secondary", padding=(10, 80)).pack()

        frame_direita = ttk.Frame(content_frame)
        frame_direita.grid(row=0, column=1, sticky="nsew")

         # --- FRAME PARA TÍTULO E BOTÃO DE INTERESSE ---
        header_frame = ttk.Frame(frame_direita)
        header_frame.pack(fill=X, anchor="nw")

        ttk.Label(header_frame, text=filme.get('titulo', 'N/A'), font=("TkDefaultFont", 22, "bold"), wraplength=550).pack(side=LEFT, anchor="nw")

        # Verifica no banco se o usuário já tem interesse neste filme
        tem_interesse = self.crud.verificar_interesse(self.usuario_logado.id, filme_id)
        
        # Define o estado inicial da nossa variável de controle
        self.interesse_var.set(tem_interesse)

        # Cria o Checkbutton estilizado como um botão de ferramenta
        btn_interesse = ttk.Checkbutton(
            master=header_frame,
            bootstyle="outline-toolbutton", # Estilo chave!
            variable=self.interesse_var,
            onvalue=True,
            offvalue=False
        )
        
        # Define o texto do botão (a estrela) e o comando a ser executado no clique
        # O texto não vai mudar, o estado visual do botão é que muda.
        btn_interesse.config(
            text="★", 
            command=lambda f_id=filme_id: self._alternar_interesse(f_id)
        )

        btn_interesse.pack(side=LEFT, padx=10, anchor="n")


        info_rapida_str = f"{str(filme.get('data_de_lancamento', 'N/A'))[:4]} | {filme.get('duracao_minutos', 'N/A')} min | IMDB: {filme.get('classificacao_IMDB', 'N/A')}"
        ttk.Label(frame_direita, text=info_rapida_str, font=("TkDefaultFont", 10, "italic")).pack(anchor="nw", pady=(5, 15))

        ttk.Label(frame_direita, text=filme.get('resumo', 'N/A'), wraplength=700, justify="left").pack(anchor="nw", pady=(0, 20), fill=X)
        
        generos_str = "Gêneros: " + ", ".join(filme.get('generos', []))
        ttk.Label(frame_direita, text=generos_str, wraplength=700).pack(anchor="nw", pady=5)
        
        elenco_str = "Elenco: " + ", ".join([ator['ator'] for ator in filme.get('elenco', [])])
        ttk.Label(frame_direita, text=elenco_str, wraplength=700).pack(anchor="nw", pady=5)
        
        self._show_frame(self.details_frame)


    def _alternar_interesse(self, filme_id: int): # <--- Remova o argumento 'botao'
        """
        Apenas executa a lógica do banco de dados.
        O estado visual do botão é atualizado automaticamente pelo Checkbutton.
        """
        self.crud.alternar_interesse(self.usuario_logado.id, filme_id)

    def _iniciar_recomendacao(self):
        """Coleta os dados necessários e chama a IA para uma recomendação."""
        # Obter a idade do usuário
        usuario_completo = self.crud.buscar_usuario_por_id(self.usuario_logado.id)
        idade = calcular_idade(usuario_completo.data_nascimento)

        # Obter a lista de filmes de interesse
        filmes_interesse = self.crud.listar_interesses_por_usuario(self.usuario_logado.id)

        # Mostrar uma mensagem de "carregando"
        self.update_idletasks() # Garante que a UI esteja atualizada
        dialogo_carregando = messagebox.showinfo("Aguarde", "Buscando uma recomendação para você...", icon='info')
        self.update() # Força a atualização da tela para mostrar o dialogo

        # Chama a IA
        recomendacao = obter_recomendacao_de_filme(idade, filmes_interesse)
        
        # Fechar o diálogo de "carregando" (isso acontece automaticamente ao mostrar o próximo)
        messagebox.showinfo("Recomendação para Você!", f"Baseado no seu gosto, talvez você curta:\n\n{recomendacao}")