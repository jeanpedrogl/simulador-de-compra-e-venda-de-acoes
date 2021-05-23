import requests
from bs4 import BeautifulSoup
from tkinter import messagebox
import sqlite3


def pega_dados(codigo_da_acao):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                            ' Chrome/90.0.4430.212 Safari/537.36'}
    conteudo = requests.get(f'https://www.google.com/search?q={codigo_da_acao.lower()}', headers=header).content
    site = BeautifulSoup(conteudo, 'html.parser')
    info = site.find('span', attrs={'class': "IsqQVc NprOob XcVN5d wT3VGc", 'jsname': "vWLAgc"})
    nome = site.find('span', {'class': "WuDkNe"})
    try:
        info = float(info.text.replace(',', '.')), nome.text
    except ValueError:
        info = float(info.text.replace(',', '.').replace('.', '')), nome.text

    return info


def compra(codigo_da_acao, quantidade):
    banco = sqlite3.connect('dados\\dados.db')
    cursor = banco.cursor()
    preco_novo, codigo_da_acao = pega_dados(codigo_da_acao)
    total = preco_novo * quantidade

    try:
        cursor.execute(f'SELECT * FROM papeis WHERE "nome" = "{codigo_da_acao}"')
        dados = cursor.fetchall()
        preco_inicial = dados[0][1]
        quantidade_inicial = dados[0][2]
        quantidade_total = quantidade_inicial + quantidade
        valor_final = (preco_inicial * quantidade_inicial + preco_novo * quantidade) / quantidade_total
        cursor.execute(f'''UPDATE papeis SET "preco" = "{valor_final}",
                       "quantidade" = "{quantidade_total}",
                       "total" = "{quantidade_total * valor_final}"
                       WHERE "nome" = "{codigo_da_acao}"''')
    except IndexError:
        cursor.execute(f'INSERT INTO papeis VALUES (?, ?, ?, ?)', (codigo_da_acao, preco_novo, quantidade,
                                                                   total))

    dinheiro_que_tenho = dinheiro_restante()
    if dinheiro_que_tenho - total < 0:
        banco.close()
        return False
    with open('dados\\dinheiro.txt', 'w') as escrita:
        escrita.write(str(dinheiro_que_tenho - total))

    banco.commit()
    banco.close()
    print(f'COMPRADO: {codigo_da_acao}, {preco_novo}, {quantidade}, {preco_novo * quantidade}')
    return [codigo_da_acao, preco_novo, quantidade]


def venda(codigo_da_acao, venderquantos):
    banco = sqlite3.connect('dados\\dados.db')
    cursor = banco.cursor()
    preco_novo, codigo_da_acao = pega_dados(codigo_da_acao)

    cursor.execute(f'SELECT * FROM papeis WHERE "nome" = "{codigo_da_acao}"')
    dados = cursor.fetchall()
    if len(dados) == 0 or dados[0][2] - venderquantos < 0:
        return False
    elif dados[0][2] - venderquantos > 0:
        valor_inicial = dados[0][1]
        quantidade_inicial = dados[0][2]
        quantidade_final = quantidade_inicial - venderquantos
        valor_final = (valor_inicial * quantidade_inicial - preco_novo * venderquantos) / quantidade_final
        cursor.execute(f'''UPDATE papeis SET "preco" = "{valor_final}",
                               "quantidade" = "{quantidade_final}",
                               "total" = "{quantidade_final * valor_final}"
                               WHERE "nome" = "{codigo_da_acao}"''')
    elif dados[0][2] - venderquantos == 0:
        cursor.execute(f'DELETE FROM papeis WHERE "nome" = "{codigo_da_acao}"')

    dinheiro_sobra = dinheiro_restante()
    with open('dados\\dinheiro.txt', 'w') as escrita:
        escrita.write(str(dinheiro_sobra + preco_novo * venderquantos))

    banco.commit()
    banco.close()

    print(f'VENDIDO: {codigo_da_acao}, {preco_novo}, {venderquantos}, {preco_novo * venderquantos}')
    return [codigo_da_acao, preco_novo, venderquantos]


# carteira 1
def enviar_carteira_alfabetica():
    banco = sqlite3.connect('dados\\dados.db')
    cursor = banco.cursor()

    cursor.execute('SELECT * from papeis ORDER BY "nome"')
    dados = cursor.fetchall()

    return dados


# carteira 2, so o dinheiro restante
def dinheiro_restante():
    with open('dados\\dinheiro.txt', 'r') as leitura:
        return float(leitura.readline())


def abrir_arquivo():
    pass


def salvar_arquivo():
    pass


def mensagem_erro(mensagem):
    messagebox.showerror(title='ERRO AO REALIZAR OPERAÇÃO', message=mensagem)


def mensagem_sucesso(mensagem):
    messagebox.showinfo(title='OPERAÇÃO REALIZADA COM SUCESSO', message=mensagem)


if __name__ == '__main__':
    pass