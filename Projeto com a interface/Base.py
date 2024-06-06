# Codigo base do Rafael

import customtkinter
from PIL import Image

janela = customtkinter.CTk()
janela.title("interface")
janela.geometry("1400x700")

top_bar = customtkinter.CTkFrame(master=janela, fg_color="#0D1E40", width=1400, height=140, corner_radius=0)
top_bar.pack_propagate(0)
top_bar.pack(fill="x", anchor="n")

frame_principal = customtkinter.CTkFrame(master=janela, fg_color="#D9D9D9", width=1400, height=700, corner_radius=0)
frame_principal.pack_propagate(0)
frame_principal.pack(anchor="n")

instrucao = customtkinter.CTkLabel(master=frame_principal, text="Digite todas as informações necessárias para localizar o perfil do candidato(a).",  font=("Arial Black", 25), text_color="#0D1E40")
instrucao.pack(anchor="n", padx= 20, pady= 50)

grid_entradas = customtkinter.CTkFrame(master=frame_principal, fg_color="transparent")
grid_entradas.pack(fill="x" , padx=250, pady=(50,0), anchor="n")

nome = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Nome completo",placeholder_text_color="#0D1E40", fg_color="transparent", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
nome.grid(row=0, column=0, ipady=10, sticky="n",  pady=(24,0))

linguagem = customtkinter.CTkEntry(master= grid_entradas,  placeholder_text="Linguagem de programação", placeholder_text_color="#0D1E40", fg_color="transparent", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
linguagem.grid(row=1, column=0, ipady=10, sticky="n", pady=(24,0))

localidade = customtkinter.CTkEntry(master=grid_entradas, placeholder_text="Localidade", placeholder_text_color="#0D1E40", fg_color="transparent", border_color="#0D1E40", border_width=2, width=400, corner_radius=10)
localidade.grid(row=0, column=1, ipady=10, sticky="n", pady=(24,0), padx=(24,0))

consulta = customtkinter.CTkButton(master=grid_entradas, text="consultar", text_color="#D9D9D9", width=400, fg_color="#0D1E40",  font=("Arial Bold", 17), hover_color="#144673", border_width=2, corner_radius=10)
consulta.grid(row=1, column=1,  ipady=10, sticky="n", pady=(24,0), padx=(24,0))




janela.mainloop()