import customtkinter
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import webbrowser
import math
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from io import BytesIO
import urllib.parse

# Variáveis globais
ultimos_perfis = []
total_paginas = 0
pagina_atual = 1
imagens_perfis = []  # Lista para manter as referências das imagens

# Função para buscar estados usando a API do IBGE
def buscar_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    response = requests.get(url)
    if response.status_code != 200:
        messagebox.showerror("Erro", f"Erro na requisição dos estados: {response.status_code}")
        return []

    estados_data = response.json()
    estados_siglas = [estado["sigla"] for estado in estados_data]
    return estados_siglas

# Funções de busca
def buscar_perfis_github(nome, sobrenome, estado, cidade, pagina=1):
    resultados_por_pagina = 10
    query = f'{nome}+{sobrenome}+location:"{cidade}+{estado}"'
    url = f'https://api.github.com/search/users?q={query}&per_page={resultados_por_pagina}&page={pagina}'

    response = requests.get(url)
    
    if response.status_code != 200:
        messagebox.showerror("Erro", f"Erro na requisição: {response.status_code}")
        return []

    data = response.json()
    total_resultados = data.get('total_count', 0)
    global total_paginas
    total_paginas = math.ceil(total_resultados / resultados_por_pagina)
    
    urls = [user['html_url'] for user in data.get('items', [])]
    
    return urls

def formatar_linguagem(linguagem):
    if linguagem.lower() == 'c#':
        return 'c%23'
    elif linguagem.lower() == 'c++':
        return 'c%2B%2B'
    else:
        return urllib.parse.quote(linguagem)

# Função para buscar projetos por usuário com a linguagem formatada
def buscar_projetos_por_usuario(nome_usuario, linguagem):
    linguagem_formatada = formatar_linguagem(linguagem)  # Formata a linguagem antes de adicioná-la à URL
    url = f"https://github.com/{nome_usuario}?tab=repositories&q=&type=&language={linguagem_formatada}&sort="
    response = requests.get(url)
    if response.status_code != 200:
        messagebox.showerror("Erro", f"Erro ao acessar a página de repositórios: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = soup.find_all('a', itemprop='name codeRepository')
    
    project_links = []
    for repo in repos:
        project_link = repo['href']
        project_links.append(f"https://github.com{project_link}")

    return project_links

# Função para abrir links no navegador
def abrir_link(url):
    webbrowser.open(url, new=2)

# Função de consulta com paginação
def consultar():
    global ultimos_perfis, pagina_atual, imagens_perfis
    imagens_perfis = []  # Limpa a lista de imagens antes de nova consulta
    nome_completo = nome.get().split()
    if len(nome_completo) < 1:
        messagebox.showerror("Erro", "Por favor, insira pelo menos o primeiro nome.")
        return

    nome_pessoa = nome_completo[0]
    sobrenome_pessoa = ' '.join(nome_completo[1:])
    estado_pessoa = estado.get()
    cidade_pessoa = cidade.get()

    perfis = buscar_perfis_github(nome_pessoa, sobrenome_pessoa, estado_pessoa, cidade_pessoa, pagina=pagina_atual)
    ultimos_perfis = perfis

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    if not perfis:
        resultado_label = customtkinter.CTkLabel(master=resultados_frame, text="Nenhum perfil encontrado.", text_color="black", fg_color="transparent")
        resultado_label.pack(anchor="w")
        return

    for perfil in perfis:
        perfil_frame = customtkinter.CTkFrame(master=resultados_frame, fg_color="white", corner_radius=15)
        perfil_frame.pack(fill="x", pady=10, padx=10)
        perfil_frame.configure(border_width=2, border_color="#0D1E40")

        # Define a URL do avatar do usuário
        avatar_url = f'https://github.com/{perfil.split("/")[-1]}.png'

        avatar_response = requests.get(avatar_url)
        if avatar_response.status_code == 200:
            avatar_data = avatar_response.content
            avatar_image = Image.open(BytesIO(avatar_data))
            avatar_image = avatar_image.resize((50, 50), Image.Resampling.LANCZOS)
            avatar_photo = ImageTk.PhotoImage(avatar_image)
            avatar_label = tk.Label(perfil_frame, image=avatar_photo)
            avatar_label.image = avatar_photo  # Manter uma referência da imagem
            avatar_label.pack(side="left", padx=5, pady=5)
            imagens_perfis.append(avatar_photo)  # Adiciona a imagem à lista de referências

        perfil_icon = customtkinter.CTkLabel(master=perfil_frame, text="●", text_color="blue", fg_color="transparent", font=("Arial", 14))
        perfil_icon.pack(side="left", padx=5, pady=5)

        perfil_label = customtkinter.CTkLabel(master=perfil_frame, text=perfil, text_color="blue", fg_color="transparent", cursor="hand2")
        perfil_label.pack(side="left", padx=5, pady=5)
        perfil_label.bind("<Button-1>", lambda e, url=perfil: abrir_link(url))

        # Adiciona o botão "Projetos"
        botao_projetos = customtkinter.CTkButton(master=perfil_frame, text="Projetos", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda url=perfil: carregar_projetos(url))
        botao_projetos.pack(side="left", padx=20, pady=10)

    # Adicionar controles de paginação
    pagina_label = customtkinter.CTkLabel(master=resultados_frame, text=f"Página {pagina_atual} de {total_paginas}", text_color="black", fg_color="transparent")
    pagina_label.pack(anchor="w", pady=(10, 0))

    if pagina_atual > 1:
        botao_anterior = customtkinter.CTkButton(master=resultados_frame, text="Anterior", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: atualizar_pagina(pagina_atual - 1))
        botao_anterior.pack(side="left", padx=20, pady=10)

    if pagina_atual < total_paginas:
        botao_proximo = customtkinter.CTkButton(master=resultados_frame, text="Próximo", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: atualizar_pagina(pagina_atual + 1))
        botao_proximo.pack(side="right", padx=20, pady=10)

def carregar_projetos(perfil_url):
    nome_usuario = perfil_url.split('/')[-1]
    exibir_projetos(nome_usuario)

def exibir_projetos(nome_usuario):
    projetos = buscar_projetos_por_usuario(nome_usuario, linguagem.get())

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    if not projetos:
        projeto_label = customtkinter.CTkLabel(master=resultados_frame, text=f"{nome_usuario} não possui projetos em {linguagem.get()}.", text_color="black", fg_color="transparent", padx=20)
        projeto_label.pack(anchor="w", padx=20, pady=2)
        botao_voltar = customtkinter.CTkButton(master=resultados_frame, text="Voltar", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: restaurar_links(ultimos_perfis))
        botao_voltar.pack(anchor="e", padx=20, pady=10)
        return

    for idx, projeto in enumerate(projetos, start=1):
        projeto_label = customtkinter.CTkLabel(master=resultados_frame, text=f"{idx}. {projeto}", text_color="blue", fg_color="transparent", cursor="hand2")
        projeto_label.pack(anchor="w", padx=20, pady=2)
        projeto_label.bind("<Button-1>", lambda e, url=projeto: abrir_link(url))

    botao_voltar = customtkinter.CTkButton(master=resultados_frame, text="Voltar", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: restaurar_links(ultimos_perfis))
    botao_voltar.pack(anchor="e", padx=20, pady=10)

def atualizar_pagina(nova_pagina):
    global pagina_atual
    pagina_atual = nova_pagina
    consultar()

def restaurar_links(links):
    global imagens_perfis
    imagens_perfis = []  # Limpa a lista de imagens antes de restaurar links
    for widget in resultados_frame.winfo_children():
        widget.destroy()

    for perfil in links:
        perfil_frame = customtkinter.CTkFrame(master=resultados_frame, fg_color="white", corner_radius=15)
        perfil_frame.pack(fill="x", pady=10, padx=10)
        perfil_frame.configure(border_width=2, border_color="#0D1E40")

        avatar_url = f'https://github.com/{perfil.split("/")[-1]}.png'
        avatar_response = requests.get(avatar_url)
        if avatar_response.status_code == 200:
            avatar_data = avatar_response.content
            avatar_image = Image.open(BytesIO(avatar_data))
            avatar_image = avatar_image.resize((50, 50), Image.Resampling.LANCZOS)
            avatar_photo = ImageTk.PhotoImage(avatar_image)
            avatar_label = tk.Label(perfil_frame, image=avatar_photo)
            avatar_label.image = avatar_photo  # Manter uma referência da imagem
            avatar_label.pack(side="left", padx=5, pady=5)
            imagens_perfis.append(avatar_photo)  # Adiciona a imagem à lista de referências

        perfil_icon = customtkinter.CTkLabel(master=perfil_frame, text="●", text_color="blue", fg_color="transparent", font=("Arial", 14))
        perfil_icon.pack(side="left", padx=5, pady=5)

        perfil_label = customtkinter.CTkLabel(master=perfil_frame, text=perfil, text_color="blue", fg_color="transparent", cursor="hand2")
        perfil_label.pack(side="left", padx=5, pady=5)
        perfil_label.bind("<Button-1>", lambda e, url=perfil: abrir_link(url))

        botao_projetos = customtkinter.CTkButton(master=perfil_frame, text="Projetos", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda url=perfil: carregar_projetos(url))
        botao_projetos.pack(side="left", padx=20, pady=10)

# Configuração da interface gráfica
janela = customtkinter.CTk()
janela.title("GitHub")
janela.geometry("1400x700")

top_bar = customtkinter.CTkFrame(master=janela, fg_color="#0D1E40", width=1400, height=140, corner_radius=0)
top_bar.pack_propagate(0)
top_bar.pack(fill="x", anchor="n")

# Adicionar o rótulo com o nome do projeto "GitHub" na barra superior
titulo_projeto = customtkinter.CTkLabel(master=top_bar, text="GitHub", font=("Arial Black", 35), text_color="white")
titulo_projeto.pack(anchor="center", pady=20)

frame_principal = customtkinter.CTkFrame(master=janela, fg_color="#D9D9D9", width=1400, height=700, corner_radius=0)
frame_principal.pack_propagate(0)
frame_principal.pack(anchor="n")

instrucao = customtkinter.CTkLabel(master=frame_principal, text="Digite todas as informações necessárias para localizar o perfil do candidato(a).", font=("Arial Black", 25), text_color="#0D1E40")
instrucao.pack(anchor="n", padx=20, pady=50)

grid_entradas = customtkinter.CTkFrame(master=frame_principal, fg_color="transparent")
grid_entradas.pack(fill="x", padx=250, pady=(50,0), anchor="n")

nome = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Nome completo", placeholder_text_color="#0D1E40", fg_color="white", text_color="black", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
nome.grid(row=0, column=0, ipady=10, sticky="n", pady=(24,0))

linguagem = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Linguagem de programação", placeholder_text_color="#0D1E40", fg_color="white", text_color="black", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
linguagem.grid(row=1, column=0, ipady=10, sticky="n", pady=(24,0))

# Obtém a lista de estados da API do IBGE
estados = buscar_estados()

# Função para estilizar o Combobox
def estilizar_combobox(combobox):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TCombobox",
                    fieldbackground="white",
                    background="white",
                    foreground="black",
                    bordercolor="#0D1E40",
                    borderwidth=2,
                    relief="flat",
                    padding=5)
    combobox.configure(style="TCombobox")
    combobox.option_add("*TCombobox*Listbox.foreground", "black")
    combobox.option_add("*TCombobox*Listbox.background", "white")
    combobox.option_add("*TCombobox*Listbox.bordercolor", "#0D1E40")
    combobox.option_add("*TCombobox*Listbox.borderwidth", 2)
    combobox.option_add("*TCombobox*Listbox.font", ("Arial", 12))

estado = ttk.Combobox(master=grid_entradas, values=estados, state="readonly", width=47)
estado.set("Selecione o estado")
estado.grid(row=0, column=1, ipady=10, sticky="n", pady=(24,0), padx=(24,0))
estilizar_combobox(estado)

cidade = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Cidade", placeholder_text_color="#0D1E40", fg_color="white", text_color="black", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
cidade.grid(row=1, column=1, ipady=10, sticky="n", pady=(24,0), padx=(24,0))

consulta = customtkinter.CTkButton(master=grid_entradas, text="Consultar", text_color="#D9D9D9", width=400, fg_color="#0D1E40", font=("Arial Bold", 17), hover_color="#144673", border_width=2, corner_radius=10, command=consultar)
consulta.grid(row=2, column=0, columnspan=2, ipady=10, sticky="n", pady=(24,0))

resultados_container = customtkinter.CTkFrame(master=frame_principal, fg_color="transparent", width=1300, height=300)
resultados_container.pack(pady=20)

canvas = customtkinter.CTkCanvas(master=resultados_container, width=1300, height=300)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = customtkinter.CTkScrollbar(master=resultados_container, orientation="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

resultados_frame = customtkinter.CTkFrame(master=canvas, fg_color="white")
canvas.create_window((0, 0), window=resultados_frame, anchor="nw")

resultados_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.configure(yscrollcommand=scrollbar.set)

janela.mainloop()
