import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage, HORIZONTAL
from repository.filme_repository import FilmeRepository
from PIL import Image, ImageTk

class TelaBiblioteca(ttk.Window):
    def __init__(self):
        super().__init__(title="Cine Filmes", themename="darkly")
        self.attributes('-zoomed', True)
        self.crud = FilmeRepository()
        self.photo_images = []

        self.sidebar = ttk.Frame(self, width=200, bootstyle="secondary")
        self.sidebar.pack(side=LEFT, fill=Y)
        
        self.main_container = ttk.Frame(self)
        self.main_container.pack(side=LEFT, fill=BOTH, expand=True)

        self.library_frame = ttk.Frame(self.main_container)
        self.details_frame = ttk.Frame(self.main_container)

        self._build_sidebar()
        self._build_library_view()

        self._show_frame(self.library_frame)

    def _show_frame(self, frame_to_show):
        for frame in [self.library_frame, self.details_frame]:
            frame.pack_forget()
        frame_to_show.pack(fill=BOTH, expand=True)

    def _build_sidebar(self):
        perfil = ttk.Frame(self.sidebar, padding=10)
        perfil.pack(fill=X)
        avatar = PhotoImage(width=50, height=50)
        ttk.Label(perfil, image=avatar, bootstyle="secondary").pack(side=LEFT)
        ttk.Label(perfil, text="Olá, Usuário", font=("TkDefaultFont", 12, "bold")).pack(padx=5)
        for i in range(1, 6):
            ttk.Button(self.sidebar, text=f"Opção {i}", bootstyle="light").pack(fill=X, pady=5, padx=10)

    def _build_library_view(self):
        canvas = ttk.Canvas(self.library_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(self.library_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        scrollable_frame = ttk.Frame(canvas)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))

        # Busca os dados para a tela principal
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
                
                # O clique passa o ID do filme
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
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Busca os detalhes completos no momento do clique
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
            img_pil = Image.open(filme['capa'])
            img_pil.thumbnail((240, 360))
            img = ImageTk.PhotoImage(img_pil)
            self.photo_images.append(img)
            ttk.Label(frame_esquerda, image=img).pack()
        except Exception:
            ttk.Label(frame_esquerda, text="Capa Indisponível", bootstyle="secondary", width=30, height=20).pack()

        frame_direita = ttk.Frame(content_frame)
        frame_direita.grid(row=0, column=1, sticky="nsew")

        ttk.Label(frame_direita, text=filme.get('titulo', 'N/A'), font=("TkDefaultFont", 22, "bold"), wraplength=600).pack(anchor="nw")

        info_rapida_str = f"{str(filme.get('data_de_lancamento', 'N/A'))[:4]} | {filme.get('duracao_minutos', 'N/A')} min | IMDB: {filme.get('classificacao_IMDB', 'N/A')}"
        ttk.Label(frame_direita, text=info_rapida_str, font=("TkDefaultFont", 10, "italic")).pack(anchor="nw", pady=(5, 15))

        ttk.Label(frame_direita, text=filme.get('resumo', 'N/A'), wraplength=700, justify="left").pack(anchor="nw", pady=(0, 20), fill=X)
        
        generos_str = "Gêneros: " + ", ".join(filme.get('generos', []))
        ttk.Label(frame_direita, text=generos_str, wraplength=700).pack(anchor="nw", pady=5)
        
        elenco_str = "Elenco: " + ", ".join([ator['ator'] for ator in filme.get('elenco', [])])
        ttk.Label(frame_direita, text=elenco_str, wraplength=700).pack(anchor="nw", pady=5)
        
        self._show_frame(self.details_frame)

if __name__ == "__main__":
    app = TelaBiblioteca()
    app.mainloop()