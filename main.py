from funcao import *
from tkinter import filedialog
from tkinter import *
import threading
import os.path
from time import sleep


def botao_preco_venda():
    try:
        acao = lista_oque_tenho.get(lista_oque_tenho.curselection()).split(' -')[0].upper()
        preco, acao = pega_dados(acao)
        ver_preco_venda.config(text=f'{acao}: R${preco:.2f}')
    except TclError:
        mensagem_erro('PAPEL NÃO ESPECIFICADO')
        ver_preco_venda.config(text=f'Qual o preço?')
    except AttributeError:
        mensagem_erro('PAPEL NÃO ENCONTRADO OU NÃO ESPECIFICADO')
        ver_preco_venda.config(text=f'Qual o preço?')


def botao_preco_compra():
    acao = codigo_entry_compra.get().strip()
    try:
        if acao == '':
            raise AttributeError
        preco, acao = pega_dados(acao)
        ver_preco_compra.config(text=f'{acao }: R${preco:.2f}')
    except AttributeError:
        mensagem_erro('PAPEL NÃO ENCONTRADO OU NÃO ESPECIFICADO')
        ver_preco_compra.config(text=f'Qual o preço?')


def abrir_arquivo():
    global carteira_inicial
    carteira_inicial = Carteira(filedialog.askdirectory(initialdir='dados'))
    atualizar_listbox()
    dinheiro_carteira()
    atualizar_diretorio_de_pasta()


def criar_arquivo():
    global carteira_inicial
    diretorio = filedialog.askdirectory(title='Criar banco de dados em qual pasta?', initialdir='dados')

    if os.path.isfile(diretorio + '\\dados.db') or os.path.isfile(diretorio + '\\dados.db'):
        resposta = messagebox.askyesno(title='Já tem arquivos aqui', message='Quer substituir os arquivos?')
        if not resposta:
            carteira_inicial = Carteira(diretorio)
            atualizar_diretorio_de_pasta()
            return

    with open(diretorio + '\\dinheiro.txt', 'w') as escrever:
        escrever.write('1000')
    with open(diretorio + '\\dados.db', 'w'):
        banco_criar = sqlite3.connect(diretorio + '\\dados.db')
        cursor_criar = banco_criar.cursor()
        cursor_criar.execute('''CREATE TABLE papeis (
                                    nome text,
                                    preco real,
                                    quantidade integer,
                                    total real
                                    )''')
        banco_criar.commit()
        banco_criar.close()

    carteira_inicial = Carteira(diretorio)
    atualizar_listbox()
    dinheiro_carteira()
    atualizar_diretorio_de_pasta()


def mudar_tempo():
    def mudar_tempo2(tempo):
        global tempo_de_atualizacao
        try:
            if float(tempo) < 0:
                raise ValueError
            tempo_de_atualizacao = float(tempo)
        except ValueError:
            mensagem_erro('APENAS NÚMEROS NATURAIS')
        else:
            janela_pergunta.destroy()

    janela_pergunta = Toplevel()
    janela_pergunta.resizable(0, 0)
    janela_pergunta.title('MUDAR TEMPO')
    janela_pergunta.geometry('250x70')
    frame = Frame(janela_pergunta)
    frame.pack()
    Label(frame, text='Novo tempo', font=('ARIAL', 13), ).grid(row=0, column=0)
    entry = Entry(frame, font=('ARIAL', 15), width=10)
    entry.grid(row=0, column=1)
    Button(frame, text='MUDAR', font=('Arial', 12), fg='BLACK', bg='green',
           command=lambda: mudar_tempo2(entry.get())).grid(row=1, column=1, columnspan=2)
    entry.insert(1, str(tempo_de_atualizacao))
    janela_pergunta.mainloop()


def atualizar_diretorio_de_pasta():
    diretorio_mostrar.config(text=carteira_inicial.pasta_origem)


def atualizar_listbox():
    lista_oque_tenho.delete(0, END)
    papeis_atualizados = carteira_inicial.enviar_carteira_alfabetica()
    for chave, acao in enumerate(papeis_atualizados):
        lista_oque_tenho.insert(chave, f'{acao[0]} - {acao[2]}')


def atualizador_carteira(tempo=3, inicial=1000):
    segunda_janela = Toplevel()
    segunda_janela.resizable(0, 0)
    segunda_janela.title('CARTEIRA')
    total = Label(segunda_janela, text='TOTAL', font=('Arial', 15), width=25, heigh=3, bg='BLACK', fg='green')
    total.pack()
    rendimento = Label(segunda_janela, text='RENDIMENTO', font=('Arial', 15), fg='BLACK', bg='green', width=25, heigh=3)
    rendimento.pack()
    try:
        while segunda_janela:
            dados = carteira_inicial.enviar_carteira_alfabetica()
            bolso = carteira_inicial.dinheiro_restante()
            soma = 0
            for dado in dados:
                valor_atualizado = pega_dados(dado[0])[0]
                soma += valor_atualizado * dado[2]
            final = soma + bolso
            total.config(text=f'R${final:.2f}')
            rendimento.config(text=f'R${final - inicial:.2f}, {((final - inicial) / inicial) * 100:.2f}%')
            sleep(tempo)
    except RuntimeError:
        segunda_janela.destroy()

    segunda_janela.mainloop()


def dinheiro_carteira():
    dinheiro_total.config(text=f'R${carteira_inicial.dinheiro_restante():.2f}')
    atualizar_listbox()


def enviar_venda():
    if not mercado_ta_aberto():
        mensagem_erro('MERCADO FECHADO')
        return
    try:
        x = lista_oque_tenho.get(lista_oque_tenho.curselection()).split(' -')[0].upper()
        if x == '':
            mensagem_erro('VOCÊ DEVE ESCOLHER UMA AÇÃO PARA VENDER')
            return
        n = int(quantidade_entry_venda.get())
        if n <= 0:
            raise ValueError
        k = carteira_inicial.venda(x, n)

    except ValueError:
        mensagem_erro('VOCÊ DEVE COLOCAR UM NÚMERO NATURAL POSITIVO EM "VENDER QUANTOS"')
        return
    if not k:
        mensagem_erro('VOCÊ NÃO PODE VENDER O QUE NÃO TEM')
    else:
        dinheiro_carteira()
        mensagem_sucesso(f'{x} VENDIDO POR {k[1]}, TOTALIZANDO +{k[1] * k[2]}')
        quantidade_entry_venda.delete(0, END)
        atualizar_listbox()


def enviar_compra():
    if not mercado_ta_aberto():
        mensagem_erro('MERCADO FECHADO')
        return
    try:
        n = int(quantidade_entry_compra.get())
        if n <= 0:
            raise ValueError
        x = carteira_inicial.compra(codigo_entry_compra.get().upper(), n)

    except ValueError:
        mensagem_erro('VOCÊ DEVE COLOCAR UM NÚMERO NATURAL POSITIVO EM "QUANTIDADE"')
        return
    if not x:
        if x is None:
            return
        mensagem_erro(f'MERCADO FECHADO OU DINHEIRO INSUFICIENTE PARA REALIZAR COMPRA DE '
                      f'{codigo_entry_compra.get().upper()}')
    else:
        dinheiro_carteira()
        mensagem_sucesso(f'{x[0]} COMPRADO POR {x[1]}, TOTALIZANDO {(float(x[1]) * float(x[2])):.2f}')
        atualizar_listbox()
        codigo_entry_compra.delete(0, END)
        quantidade_entry_compra.delete(0, END)


# verifica se o banco de dados existe, senao cria
if not os.path.isfile('dados\\dados\\dados.db'):
    banco = sqlite3.connect('dados\\dados\\dados.db')
    cursor = banco.cursor()
    cursor.execute('''CREATE TABLE papeis (
                                nome text,
                                preco real,
                                quantidade integer,
                                total real
                                )''')
    banco.commit()
    banco.close()
if not os.path.isfile('dados\\dados\\dinheiro.txt'):
    with open('dados\\dados\\dinheiro.txt', 'w') as escrita:
        escrita.write('1000')


carteira_inicial = Carteira('dados\\dados')
tempo_de_atualizacao = 900
janela = Tk()
janela.geometry('800x640')
foto_tela = PhotoImage(file='imagens\\tela.png')
janela.iconphoto(True, foto_tela)
janela.title('SIMULADOR DE AÇÕES')
janela.resizable(0, 0)

parte_superior = Frame(janela)
parte_superior.pack()


# mostrar diretório
diretorio_mostrar = Label(text='Nenhuma pasta aberta', font=('Arial', 7, 'italic'))
diretorio_mostrar.place(x=0, y=0)
atualizar_diretorio_de_pasta()

# dinheiro total e carteira
dinheiro_total = Button(parte_superior, text='  SEM DADOS  ', bg='YELLOW', font=('arial', 15),
                        command=dinheiro_carteira)
dinheiro_total.grid(row=1)
dinheiro_total.config(text=f'R${carteira_inicial.dinheiro_restante():.2f}')


botao_carteira = Button(parte_superior, text='CARTEIRA', bg='BLUE',
                        font=('arial', 10), command=lambda: threading.Thread(target=atualizador_carteira,
                                                                             args=[tempo_de_atualizacao]).start())
botao_carteira.grid()

# título e linha separatória
titulo = Label(parte_superior, text='SIMULADOR DE COMPRA E VENDA DE AÇÕES', font=('Arial', 25, 'bold'),
               pady=22, fg='ORANGE').grid(row=0)

separador = Label(janela, pady=300, padx=-3, bg='black', compound=CENTER)
separador.pack()

# Menu
menuBar = Menu(janela)
janela.config(menu=menuBar)
menu_arquivo = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label='Arquivo', menu=menu_arquivo)
menu_arquivo.add_command(label='Abrir', command=abrir_arquivo)
menu_arquivo.add_command(label='Criar db', command=criar_arquivo)
menu_arquivo.add_separator()
menu_arquivo.add_command(label='Sair', command=lambda: exit())
menu_config = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label='Configurações', menu=menu_config)
menu_config.add_command(label='Tempo att', command=mudar_tempo)

# compra
titulo_compra = Label(janela, text='COMPRA', font=('ARIAL', 20), fg='GREEN')
titulo_compra.place(x=130, y=80)

dados_compra = Frame(janela)
dados_compra.place(x=20, y=200)

codigo_label_compra = Label(dados_compra, text='CÓDIGO DA AÇÃO', font=('ARIAL', 13), fg='blue').grid(row=0, column=0)
codigo_entry_compra = Entry(dados_compra, font=('ARIAL', 13), )
codigo_entry_compra.grid(row=0, column=1)

quantidade_label_compra = Label(dados_compra, text='QUANTIDADE', font=('ARIAL', 13), fg='blue').grid(row=1, column=0)
quantidade_entry_compra = Entry(dados_compra, font=('ARIAL', 13), )
quantidade_entry_compra.grid(row=1, column=1)

ver_preco_compra = Button(dados_compra, text='Qual o preço?', font=('ARIAL', 13), fg='blue',
                          bg='#71dd13', command=lambda: threading.Thread(target=botao_preco_compra).start())
ver_preco_compra.grid(row=2, column=0, columnspan=2)

botao_compra = Button(janela, text='COMPRAR', font=('ARIAL', 15), bg='LIGHT GREEN',
                      command=lambda: threading.Thread(target=enviar_compra).start(),
                      padx=15, pady=3)
botao_compra.place(x=210, y=560)

# venda
titulo_venda = Label(janela, text='VENDA', font=('ARIAL', 20), fg='RED')
titulo_venda.place(x=540, y=80)

dados_venda = Frame(janela)
dados_venda.place(x=420, y=200)

lista_oque_tenho = Listbox(dados_venda, font=('arial', 15), bg='#f8c471', width=12, height=7)
lista_oque_tenho.grid(row=0, column=0, rowspan=15)
papeis_que_tenho = carteira_inicial.enviar_carteira_alfabetica()

quantidade_label_venda = Label(dados_venda, text='VENDER QUANTOS', font=('ARIAL', 13), fg='blue')
quantidade_label_venda.grid(row=1, column=2)
quantidade_entry_venda = Entry(dados_venda, font=('arial', 15), width=8)
quantidade_entry_venda.grid(row=2, column=2)


for key, papel in enumerate(papeis_que_tenho):
    lista_oque_tenho.insert(key, f'{papel[0]} - {papel[2]}')


ver_preco_venda = Button(dados_venda, text='Qual o preço?', font=('ARIAL', 13), fg='blue',
                         bg='#71dd13', command=lambda: threading.Thread(target=botao_preco_venda).start())
ver_preco_venda.grid(row=3, column=2)


botao_venda = Button(janela, text='VENDER', font=('ARIAL', 15), bg='RED',
                     command=lambda: threading.Thread(target=enviar_venda).start(),
                     padx=15, pady=3)
botao_venda.place(x=630, y=560)


janela.mainloop()
