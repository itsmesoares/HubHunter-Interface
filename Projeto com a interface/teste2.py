# A interface integrada e adicionei mais algumas coisas visuais

import customtkinter
from PIL import Image
import requests
from bs4 import BeautifulSoup
import webbrowser
from tkinter import messagebox

# Variáveis globais
ultimos_perfis = []

# Funções de busca
def buscar_perfis_github(nome, sobrenome, localizacao):
    query = f'{nome}+{sobrenome}+location:"{localizacao}"'
    url = f'https://api.github.com/search/users?q={query}'

    response = requests.get(url)
    
    if response.status_code != 200:
        messagebox.showerror("Erro", f"Erro na requisição: {response.status_code}")
        return []

    data = response.json()
    
    urls = [user['html_url'] for user in data.get('items', [])]
    
    return urls

def buscar_projetos_por_usuario(nome_usuario, linguagem):
    url = f"https://github.com/{nome_usuario}?tab=repositories&q=&type=&language={linguagem}&sort="
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

# Função de consulta
def consultar():
    global ultimos_perfis
    nome_completo = nome.get().split()
    if len(nome_completo) < 2:
        messagebox.showerror("Erro", "Por favor, insira o nome e sobrenome.")
        return

    nome_pessoa = nome_completo[0]
    sobrenome_pessoa = ' '.join(nome_completo[1:])
    localizacao_pessoa = localidade.get()

    perfis = buscar_perfis_github(nome_pessoa, sobrenome_pessoa, localizacao_pessoa)
    ultimos_perfis = perfis

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    if not perfis:
        resultado_label = customtkinter.CTkLabel(master=resultados_frame, text="Nenhum perfil encontrado.", text_color="black", fg_color="transparent")
        resultado_label.pack(anchor="w")
        return

    for perfil in perfis:
        perfil_frame = customtkinter.CTkFrame(master=resultados_frame, fg_color="white")
        perfil_frame.pack(fill="x", pady=10, padx=10)

        perfil_icon = customtkinter.CTkLabel(master=perfil_frame, text="●", text_color="blue", fg_color="transparent", font=("Arial", 14))
        perfil_icon.pack(side="left", padx=5, pady=5)

        perfil_label = customtkinter.CTkLabel(master=perfil_frame, text=perfil, text_color="blue", fg_color="transparent", cursor="hand2")
        perfil_label.pack(side="left", padx=5, pady=5)
        perfil_label.bind("<Button-1>", lambda e, url=perfil: mostrar_projetos(url))

def mostrar_projetos(perfil_url):
    global ultimos_perfis
    nome_usuario = perfil_url.split('/')[-1]
    projetos = buscar_projetos_por_usuario(nome_usuario, linguagem.get())

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    if not projetos:
        projeto_label = customtkinter.CTkLabel(master=resultados_frame, text=f"{nome_usuario} não possui projetos em {linguagem.get()}.", text_color="black", fg_color="transparent", padx=20)
        projeto_label.pack(anchor="w", padx=20, pady=2)
        botao_voltar = customtkinter.CTkButton(master=resultados_frame, text="Voltar", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: restaurar_links(ultimos_perfis))
        botao_voltar.pack(anchor="e", padx=20, pady=10)
        return

    for projeto in projetos:
        projeto_label = customtkinter.CTkLabel(master=resultados_frame, text=projeto, text_color="blue", fg_color="transparent", cursor="hand2")
        projeto_label.pack(anchor="w", padx=20, pady=2)
        projeto_label.bind("<Button-1>", lambda e, url=projeto: abrir_link(url))

    botao_voltar = customtkinter.CTkButton(master=resultados_frame, text="Voltar", text_color="white", fg_color="#0D1E40", font=("Arial", 12), hover_color="#144673", border_width=2, corner_radius=5, command=lambda: restaurar_links(ultimos_perfis))
    botao_voltar.pack(anchor="e", padx=20, pady=10)

def restaurar_links(perfis):
    for widget in resultados_frame.winfo_children():
        widget.destroy()

    for perfil in perfis:
        perfil_frame = customtkinter.CTkFrame(master=resultados_frame, fg_color="white")
        perfil_frame.pack(fill="x", pady=10, padx=10)

        perfil_icon = customtkinter.CTkLabel(master=perfil_frame, text="●", text_color="blue", fg_color="transparent", font=("Arial", 14))
        perfil_icon.pack(side="left", padx=5, pady=5)

        perfil_label = customtkinter.CTkLabel(master=perfil_frame, text=perfil, text_color="blue", fg_color="transparent", cursor="hand2")
        perfil_label.pack(side="left", padx=5, pady=5)
        perfil_label.bind("<Button-1>", lambda e, url=perfil: mostrar_projetos(url))

# Interface gráfica
janela = customtkinter.CTk()
janela.title("Interface")
janela.geometry("1400x700")

top_bar = customtkinter.CTkFrame(master=janela, fg_color="#0D1E40", width=1400, height=140, corner_radius=0)
top_bar.pack_propagate(0)
top_bar.pack(fill="x", anchor="n")

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

localidade = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Localidade", placeholder_text_color="#0D1E40", fg_color="white", text_color="black", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
localidade.grid(row=0, column=1, ipady=10, sticky="n", pady=(24,0), padx=(24,0))

consulta = customtkinter.CTkButton(master=grid_entradas, text="Consultar", text_color="#D9D9D9", width=400, fg_color="#0D1E40", font=("Arial Bold", 17), hover_color="#144673", border_width=2, corner_radius=10, command=consultar)
consulta.grid(row=1, column=1, ipady=10, sticky="n", pady=(24,0), padx=(24,0))

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
