import os
import sqlite3
from tkinter import *
from tkinter import ttk

class Produto:
    def __init__(self, root):
        base_dir = os.path.dirname(__file__)
        db_folder = os.path.join(base_dir, 'database')
        os.makedirs(db_folder, exist_ok=True)
        self.db_path = os.path.join(db_folder, 'produtos.db')

        self.criar_tabela()

        self.janela = root
        self.janela.title("App Gestor de Produtos")
        self.janela.resizable(True, True)  # <-- aqui

        icone = os.path.join(base_dir, 'recursos', 'M6_P2_icon.ico')
        if os.path.exists(icone):
            self.janela.wm_iconbitmap(icone)

        estilo_bt = ttk.Style()
        estilo_bt.configure('My.TButton', font=('Calibri', 14, 'bold'))

        frame = LabelFrame(self.janela,
                           text="Registar um novo Produto",
                           font=('Calibri', 16, 'bold'))
        frame.grid(row=0, column=0, columnspan=3, pady=20, padx=10)

        Label(frame, text="Nome:", font=('Calibri', 13))\
            .grid(row=1, column=0, sticky=E)
        self.nome = Entry(frame, font=('Calibri', 13))
        self.nome.focus()
        self.nome.grid(row=1, column=1, padx=5, pady=5)

        Label(frame, text="Preço:", font=('Calibri', 13))\
            .grid(row=2, column=0, sticky=E)
        self.preco = Entry(frame, font=('Calibri', 13))
        self.preco.grid(row=2, column=1, padx=5, pady=5)

        self.mensagem = Label(self.janela, text="", fg="red",
                              font=('Calibri', 12))
        self.mensagem.grid(row=3, column=0, columnspan=3,
                           sticky=W+E, padx=10)

        botao_adicionar = ttk.Button(frame,
                                     text="Guardar Produto",
                                     command=self.add_produto,
                                     style='My.TButton')
        botao_adicionar.grid(row=3, column=0, columnspan=2,
                             sticky=W+E, pady=(10,0))

        estilo_tv = ttk.Style()
        estilo_tv.configure("mystyle.Treeview",
                            highlightthickness=0, bd=0,
                            font=('Calibri', 11))
        estilo_tv.configure("mystyle.Treeview.Heading",
                            font=('Calibri', 13, 'bold'))
        estilo_tv.layout("mystyle.Treeview",
                         [('mystyle.Treeview.treearea',
                           {'sticky':'nswe'})])

        self.tabela = ttk.Treeview(self.janela,
                                   height=10,
                                   columns=('Preço',),
                                   style="mystyle.Treeview")
        self.tabela.grid(row=4, column=0, columnspan=2,
                         padx=10, pady=10, sticky=W+E)
        self.tabela.heading('#0', text='Nome', anchor=CENTER)
        self.tabela.heading('Preço', text='Preço', anchor=CENTER)

        botao_eliminar = ttk.Button(self.janela,
                                    text='ELIMINAR',
                                    command=self.del_produto,
                                    style='My.TButton')
        botao_eliminar.grid(row=5, column=0,
                            sticky=W+E, padx=(10,5), pady=(0,10))

        botao_editar = ttk.Button(self.janela,
                                  text='EDITAR',
                                  command=self.edit_produto,
                                  style='My.TButton')
        botao_editar.grid(row=5, column=1,
                          sticky=W+E, padx=(5,10), pady=(0,10))

        self.get_produtos()


    def criar_tabela(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        );
        '''
        self.db_consulta(sql)


    def db_consulta(self, sql, parametros=()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            resultado = cursor.execute(sql, parametros)
            conn.commit()
        return resultado

    def get_produtos(self):

        for item in self.tabela.get_children():
            self.tabela.delete(item)


        query = 'SELECT * FROM produto ORDER BY nome DESC'
        produtos = list(self.db_consulta(query))


        for linha in produtos:
            self.tabela.insert('', 0, text=linha[1], values=(linha[2],))

        if produtos:
            print("\n📋 Lista de produtos:")
            for p in produtos:
                print(f" - {p[1]}: €{p[2]}")
        else:
            print("\n⚠️ Nenhum produto registado ainda.")

    def validacao_nome(self):
        return len(self.nome.get().strip()) > 0


    def validacao_preco(self):
        return len(self.preco.get().strip()) > 0

    def add_produto(self):
        nome_valido = self.validacao_nome()
        preco_valido = self.validacao_preco()

        if nome_valido and preco_valido:
            # Consulta SQL com placeholders e parâmetros
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'
            parametros = (self.nome.get(), self.preco.get())
            self.db_consulta(query, parametros)

            print("✅ Dados guardados no banco.")
            self.mensagem['text'] = f'Produto "{self.nome.get()}" adicionado com êxito'

            # Limpa os campos do formulário
            self.nome.delete(0, END)
            self.preco.delete(0, END)

        elif nome_valido and not preco_valido:
            print("⚠️ O preço é obrigatório")
            self.mensagem['text'] = 'O preço é obrigatório'

        elif not nome_valido and preco_valido:
            print("⚠️ O nome é obrigatório")
            self.mensagem['text'] = 'O nome é obrigatório'

        else:
            print("⚠️ O nome e o preço são obrigatórios")
            self.mensagem['text'] = 'O nome e o preço são obrigatórios'

        # Atualiza tabela após tentativa
        self.get_produtos()

    def del_produto(self):
        self.mensagem['text'] = ''
        try:
            selecionado = self.tabela.selection()[0]
            nome = self.tabela.item(selecionado)['text']
        except IndexError:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return
        sql = 'DELETE FROM produto WHERE nome = ?'
        self.db_consulta(sql, (nome,))
        self.mensagem['text'] = f'Produto "{nome}" eliminado com êxito'
        self.get_produtos()


    def edit_produto(self):
        self.mensagem['text'] = ''
        try:
            sel = self.tabela.selection()[0]
            nome = self.tabela.item(sel)['text']
            preco_antigo = self.tabela.item(sel)['values'][0]
        except IndexError:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return

        janela_editar = Toplevel(self.janela)
        janela_editar.title("Editar Produto")
        janela_editar.resizable(True, True)  # <-- e aqui
        icone = os.path.join(os.path.dirname(__file__),
                             'recursos', 'icon.ico')
        if os.path.exists(icone):
            janela_editar.wm_iconbitmap(icone)

        frame_ep = LabelFrame(janela_editar,
                              text="Editar o seguinte Produto",
                              font=('Calibri', 16, 'bold'))
        frame_ep.grid(row=0, column=0, columnspan=2,
                      padx=10, pady=20)

        Label(frame_ep, text="Nome antigo:", font=('Calibri', 13))\
            .grid(row=1, column=0, sticky=E)
        Entry(frame_ep, font=('Calibri', 13),
              state='readonly',
              textvariable=StringVar(janela_editar, value=nome))\
            .grid(row=1, column=1, padx=5, pady=5)

        Label(frame_ep, text="Nome novo:", font=('Calibri', 13))\
            .grid(row=2, column=0, sticky=E)
        ent_novo_nome = Entry(frame_ep, font=('Calibri', 13))
        ent_novo_nome.grid(row=2, column=1, padx=5, pady=5)
        ent_novo_nome.focus()

        Label(frame_ep, text="Preço antigo:", font=('Calibri', 13))\
            .grid(row=3, column=0, sticky=E)
        Entry(frame_ep, font=('Calibri', 13),
              state='readonly',
              textvariable=StringVar(janela_editar, value=preco_antigo))\
            .grid(row=3, column=1, padx=5, pady=5)

        Label(frame_ep, text="Preço novo:", font=('Calibri', 13))\
            .grid(row=4, column=0, sticky=E)
        ent_novo_preco = Entry(frame_ep, font=('Calibri', 13))
        ent_novo_preco.grid(row=4, column=1, padx=5, pady=5)

        botao_atualizar = ttk.Button(
            frame_ep,
            text="Atualizar Produto",
            style='My.TButton',
            command=lambda: self.atualizar_produtos(
                ent_novo_nome.get(),
                nome,
                ent_novo_preco.get(),
                preco_antigo,
                janela_editar
            )
        )
        botao_atualizar.grid(row=5, column=0,
                             columnspan=2,
                             sticky=W+E,
                             pady=(10,0))


    def atualizar_produtos(self, novo_nome, antigo_nome,
                           novo_preco, preco_antigo, janela_editar):
        modificado = False
        sql = 'UPDATE produto SET nome = ?, preco = ? WHERE nome = ? AND preco = ?'

        if novo_nome and novo_preco:
            params = (novo_nome, novo_preco, antigo_nome, preco_antigo)
            modificado = True
        elif novo_nome:
            params = (novo_nome, preco_antigo, antigo_nome, preco_antigo)
            modificado = True
        elif novo_preco:
            params = (antigo_nome, novo_preco, antigo_nome, preco_antigo)
            modificado = True
        else:
            params = ()
            modificado = False

        if modificado:
            self.db_consulta(sql, params)
            janela_editar.destroy()
            self.mensagem['text'] = f'Produto "{antigo_nome}" atualizado com êxito'
            self.get_produtos()
        else:
            janela_editar.destroy()
            self.mensagem['text'] = f'Nenhuma alteração para "{antigo_nome}"'


def iniciar_interface():
    print("⚡ Iniciando interface…")
    root = Tk()
    app = Produto(root)
    root.mainloop()

if __name__ == '__main__':
    iniciar_interface()



