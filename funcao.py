import yfinance as yf
import sqlite3
from tkinter import messagebox
from time import localtime, strftime


class Carteira:
    def __init__(self, pasta_origem, valor_inicial=1000):
        self.pasta_origem = pasta_origem
        self.valor_inicial = valor_inicial

    # carteira 2, so o dinheiro restante
    def dinheiro_restante(self):
        with open(self.pasta_origem + '/dinheiro.txt', 'r') as leitura:
            return float(leitura.readline())

    def compra(self, codigo_da_acao, quantidade):
        banco = sqlite3.connect(self.pasta_origem + '/dados.db')
        cursor = banco.cursor()
        preco_novo, codigo_da_acao = pega_dados(codigo_da_acao)
        total = preco_novo * quantidade

        try:
            cursor.execute(
                f'SELECT * FROM papeis WHERE "nome" = "{codigo_da_acao}"')
            dados = cursor.fetchall()
            preco_inicial = dados[0][1]
            quantidade_inicial = dados[0][2]
            quantidade_total = quantidade_inicial + quantidade
            valor_final = (preco_inicial * quantidade_inicial +
                           preco_novo * quantidade) / quantidade_total
            cursor.execute(f'''UPDATE papeis SET "preco" = "{valor_final}",
                           "quantidade" = "{quantidade_total}",
                           "total" = "{quantidade_total * valor_final}"
                           WHERE "nome" = "{codigo_da_acao}"''')
        except IndexError:
            cursor.execute(f'INSERT INTO papeis VALUES (?, ?, ?, ?)', (codigo_da_acao, preco_novo, quantidade,
                                                                       total))

        dinheiro_que_tenho = self.dinheiro_restante()
        if dinheiro_que_tenho - total < 0:
            banco.close()
            return False
        with open(self.pasta_origem + '/dinheiro.txt', 'w') as escrita:
            escrita.write(str(dinheiro_que_tenho - total))

        banco.commit()
        banco.close()
        print(
            f'COMPRADO: {codigo_da_acao}, {preco_novo}, {quantidade}, {preco_novo * quantidade}')
        return [codigo_da_acao, preco_novo, quantidade]

    def venda(self, codigo_da_acao, venderquantos):
        banco = sqlite3.connect(self.pasta_origem + '/dados.db')
        cursor = banco.cursor()
        preco_novo, codigo_da_acao = pega_dados(codigo_da_acao)

        cursor.execute(
            f'SELECT * FROM papeis WHERE "nome" = "{codigo_da_acao}"')
        dados = cursor.fetchall()
        if len(dados) == 0 or dados[0][2] - venderquantos < 0:
            return False
        elif dados[0][2] - venderquantos > 0:
            valor_inicial = dados[0][1]
            quantidade_inicial = dados[0][2]
            quantidade_final = quantidade_inicial - venderquantos
            valor_final = (valor_inicial * quantidade_inicial -
                           preco_novo * venderquantos) / quantidade_final
            cursor.execute(f'''UPDATE papeis SET "preco" = "{valor_final}",
                                   "quantidade" = "{quantidade_final}",
                                   "total" = "{quantidade_final * valor_final}"
                                   WHERE "nome" = "{codigo_da_acao}"''')
        elif dados[0][2] - venderquantos == 0:
            cursor.execute(
                f'DELETE FROM papeis WHERE "nome" = "{codigo_da_acao}"')

        dinheiro_sobra = self.dinheiro_restante()
        with open(self.pasta_origem + '/dinheiro.txt', 'w') as escrita:
            escrita.write(str(dinheiro_sobra + preco_novo * venderquantos))

        banco.commit()
        banco.close()

        print(
            f'VENDIDO: {codigo_da_acao}, {preco_novo}, {venderquantos}, {preco_novo * venderquantos}')
        return [codigo_da_acao, preco_novo, venderquantos]

    def enviar_carteira_alfabetica(self):  # carteira 1
        banco = sqlite3.connect(self.pasta_origem + '/dados.db')
        cursor = banco.cursor()

        cursor.execute('SELECT * from papeis ORDER BY "nome"')
        dados = cursor.fetchall()

        return dados


def pega_dados(codigo_da_acao):
    acao = yf.Ticker(f"{codigo_da_acao}.SA")
    info = (float(acao.info["regularMarketPrice"]), acao.info["symbol"][:-3])
    return info

def mensagem_erro(mensagem):
    messagebox.showerror(title='ERRO AO REALIZAR OPERAÇÃO', message=mensagem)


def mensagem_sucesso(mensagem):
    messagebox.showinfo(
        title='OPERAÇÃO REALIZADA COM SUCESSO', message=mensagem)


def mercado_ta_aberto():
    dia = strftime('%A', localtime())
    hora = int(strftime('%H%M', localtime()))

    if dia in ['Sunday', 'Saturday'] or hora <= 1000 or hora >= 1700:
        return False
    else:
        return True


if __name__ == '__main__':
    print(pega_dados('ABEV3'))
