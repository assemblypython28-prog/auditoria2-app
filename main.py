# main.py - App de Auditoria de Ativos em Kivy (versão offline)

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
import sqlite3
import os
import pandas as pd
from openpyxl import load_workbook
import io
import re
from datetime import datetime

Window.size = (360, 640)  # Tamanho típico de celular

# ===================== BANCO DE DADOS =====================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auditoria.db')

def criar_banco():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id TEXT NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            data_auditoria TEXT DEFAULT '',
            observacoes TEXT DEFAULT '',
            quantidade TEXT DEFAULT '1',
            local TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(obra_id, codigo)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_obra ON inventario (obra_id)')
    conn.commit()
    conn.close()

def conectar():
    return sqlite3.connect(DB_PATH)

# ===================== FUNÇÕES CRUD =====================
def carregar_dados(obra_id='default'):
    conn = conectar()
    c = conn.cursor()
    c.execute('''
        SELECT codigo, descricao, status, data_auditoria, observacoes, quantidade, local
        FROM inventario WHERE obra_id = ? ORDER BY codigo
    ''', (obra_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return []
    return [dict(zip(['codigo','descricao','status','data_auditoria','observacoes','quantidade','local'], row)) for row in rows]

def salvar_item(codigo, descricao, status='Pendente', data_aud='', obs='', qtd='1', local='', obra_id='default'):
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT id FROM inventario WHERE obra_id = ? AND codigo = ?', (obra_id, codigo))
    existe = c.fetchone()
    if existe:
        c.execute('''
            UPDATE inventario SET status=?, data_auditoria=?, observacoes=?, quantidade=?, local=?, updated_at=datetime('now')
            WHERE obra_id=? AND codigo=?
        ''', (status, data_aud, obs, qtd, local, obra_id, codigo))
    else:
        c.execute('''
            INSERT INTO inventario (obra_id, codigo, descricao, status, data_auditoria, observacoes, quantidade, local)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (obra_id, codigo, descricao, status, data_aud, obs, qtd, local))
    conn.commit()
    conn.close()

def deletar_obra(obra_id):
    conn = conectar()
    c = conn.cursor()
    c.execute('DELETE FROM inventario WHERE obra_id = ?', (obra_id,))
    conn.commit()
    conn.close()

def deletar_tudo():
    conn = conectar()
    c = conn.cursor()
    c.execute('DELETE FROM inventario')
    conn.commit()
    conn.close()

def listar_obras():
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT DISTINCT obra_id FROM inventario ORDER BY obra_id')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def normalizar(codigo):
    if not codigo:
        return ''
    return str(codigo).split('-')[0].lstrip('0')

def importar_excel(file_path, obra_id):
    try:
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
        # Limpeza similar à do código original
        if 'Codigo do Bem' not in df_raw.columns:
            df_raw.columns = df_raw.iloc[0]
            df_raw = df_raw.iloc[1:].reset_index(drop=True)
        mask = (
            df_raw['Codigo do Bem'].astype(str).str.match(r'^[0-9]{3,}', na=False) &
            df_raw['Descricao do Bem'].notna() &
            (df_raw['Descricao do Bem'].astype(str).str.strip() != '') &
            (~df_raw['Descricao do Bem'].astype(str).str.contains('Estel Servicos', na=False))
        )
        df_clean = df_raw.loc[mask, ['Codigo do Bem', 'Descricao do Bem']].copy()
        df_clean['Codigo do Bem'] = df_clean['Codigo do Bem'].astype(str).str.strip()
        if df_clean.empty:
            return 0, 0, 0

        # Salvar em lote
        conn = conectar()
        c = conn.cursor()
        novos = 0
        alterados = 0
        iguais = 0
        for _, row in df_clean.iterrows():
            codigo = str(row['Codigo do Bem'])
            descricao = str(row['Descricao do Bem'])
            c.execute('SELECT descricao, status FROM inventario WHERE obra_id = ? AND codigo = ?', (obra_id, codigo))
            existente = c.fetchone()
            if existente:
                if existente[0] != descricao:
                    # Mantém status se for 'Auditado'
                    status_manter = 'Auditado' if existente[1] == 'Auditado' else 'Pendente'
                    c.execute('''
                        UPDATE inventario SET descricao=?, status=?, updated_at=datetime('now')
                        WHERE obra_id=? AND codigo=?
                    ''', (descricao, status_manter, obra_id, codigo))
                    alterados += 1
                else:
                    iguais += 1
            else:
                c.execute('''
                    INSERT INTO inventario (obra_id, codigo, descricao, status, data_auditoria, observacoes, quantidade, local)
                    VALUES (?, ?, ?, 'Pendente', '', '', '1', '')
                ''', (obra_id, codigo, descricao))
                novos += 1
        conn.commit()
        conn.close()
        return novos, alterados, iguais
    except Exception as e:
        return -1, 0, 0

def exportar_excel(obra_id):
    dados = carregar_dados(obra_id)
    if not dados:
        return None
    df = pd.DataFrame(dados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
    output.seek(0)
    return output.read()

# ===================== INTERFACE KIVY =====================

class ItemRV(RecycleDataViewBehavior, BoxLayout):
    codigo = StringProperty('')
    descricao = StringProperty('')
    status = StringProperty('')
    data_aud = StringProperty('')
    obs = StringProperty('')
    qtd = StringProperty('')
    local = StringProperty('')
    obra_id = StringProperty('')
    index = 0

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.codigo = data.get('codigo', '')
        self.descricao = data.get('descricao', '')
        self.status = data.get('status', '')
        self.data_aud = data.get('data_auditoria', '')
        self.obs = data.get('observacoes', '')
        self.qtd = data.get('quantidade', '')
        self.local = data.get('local', '')
        self.obra_id = data.get('obra_id', 'default')
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Ao tocar no item, abre popup com detalhes e opção de auditar
            app = App.get_running_app()
            root = app.root
            if hasattr(root, 'mostrar_detalhes'):
                root.mostrar_detalhes(self.index)
        return super().on_touch_down(touch)

class RV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainScreen(BoxLayout):
    obra_id = StringProperty('default')
    dados = ListProperty([])
    filtro_status = StringProperty('Todos')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.obra_id = 'default'
        self.carregar_dados()

        # Cabeçalho
        header = BoxLayout(size_hint_y=0.08, padding=8, spacing=8)
        header.add_widget(Label(text='Auditoria de Ativos', font_size='18sp', bold=True, color=(0.2,0.2,0.2,1)))
        self.add_widget(header)

        # Seleção de obra
        obra_box = BoxLayout(size_hint_y=0.08, padding=8, spacing=8)
        obra_box.add_widget(Label(text='Obra:', size_hint_x=0.2))
        self.obra_input = TextInput(text=self.obra_id, multiline=False, size_hint_x=0.6)
        obra_box.add_widget(self.obra_input)
        btn_carregar = Button(text='Carregar', size_hint_x=0.2)
        btn_carregar.bind(on_press=self.trocar_obra)
        obra_box.add_widget(btn_carregar)
        self.add_widget(obra_box)

        # Abas: usar Spinner para navegar entre telas
        self.aba_atual = 'lista'
        self.spinner_abas = Spinner(
            text='Lista',
            values=('Lista', 'Busca', 'Cadastro', 'Dashboard', 'Sobre'),
            size_hint_y=0.06
        )
        self.spinner_abas.bind(text=self.mudar_aba)
        self.add_widget(self.spinner_abas)

        # Container para o conteúdo das abas
        self.conteudo = BoxLayout(orientation='vertical')
        self.add_widget(self.conteudo)

        # Inicializa com a aba Lista
        self.mostrar_lista()

    def trocar_obra(self, instance):
        nova = self.obra_input.text.strip()
        if nova:
            self.obra_id = nova
            self.carregar_dados()
            # Atualiza lista se estiver nela
            if self.aba_atual == 'lista':
                self.mostrar_lista()

    def carregar_dados(self):
        self.dados = carregar_dados(self.obra_id)

    def mudar_aba(self, spinner, texto):
        self.aba_atual = texto.lower()
        self.conteudo.clear_widgets()
        if texto == 'Lista':
            self.mostrar_lista()
        elif texto == 'Busca':
            self.mostrar_busca()
        elif texto == 'Cadastro':
            self.mostrar_cadastro()
        elif texto == 'Dashboard':
            self.mostrar_dashboard()
        elif texto == 'Sobre':
            self.mostrar_sobre()

    # =========== ABA LISTA ===========
    def mostrar_lista(self):
        self.conteudo.clear_widgets()
        # Filtro
        filtro_box = BoxLayout(size_hint_y=0.08, padding=4)
        filtro_box.add_widget(Label(text='Filtrar:', size_hint_x=0.2))
        self.spinner_filtro = Spinner(
            text='Todos',
            values=('Todos', 'Pendente', 'Auditado', 'Sobra', 'Sem Patrimonio'),
            size_hint_x=0.4
        )
        self.spinner_filtro.bind(text=self.filtrar_lista)
        filtro_box.add_widget(self.spinner_filtro)
        self.busca_input = TextInput(multiline=False, hint_text='Buscar...', size_hint_x=0.4)
        self.busca_input.bind(text=self.filtrar_lista)
        filtro_box.add_widget(self.busca_input)
        self.conteudo.add_widget(filtro_box)

        # RecycleView para lista
        self.rv = RV()
        self.rv.viewclass = 'ItemRV'
        self.rv.data = []
        self.rv_recycle_layout = RecycleBoxLayout(
            default_size=(None, 60),
            default_size_hint=(1, None),
            size_hint_y=None,
            height=60,
            orientation='vertical'
        )
        self.rv.add_widget(self.rv_recycle_layout)
        self.conteudo.add_widget(self.rv)
        self.filtrar_lista()

    def filtrar_lista(self, *args):
        filtro = self.spinner_filtro.text
        busca = self.busca_input.text.lower()
        dados_filtrados = []
        for item in self.dados:
            # Aplica filtro de status
            if filtro != 'Todos':
                if filtro == 'Sobra' and not item['descricao'].startswith('[SOBRA]'):
                    continue
                elif filtro == 'Sem Patrimonio' and not item['descricao'].startswith('[SEM PATRIMONIO]'):
                    continue
                elif filtro == 'Pendente' and (item['status'] != 'Pendente' or item['descricao'].startswith('[SOBRA]') or item['descricao'].startswith('[SEM PATRIMONIO]')):
                    continue
                elif filtro == 'Auditado' and (item['status'] != 'Auditado' or item['descricao'].startswith('[SOBRA]') or item['descricao'].startswith('[SEM PATRIMONIO]')):
                    continue
            # Busca textual
            if busca and busca not in item['codigo'].lower() and busca not in item['descricao'].lower():
                continue
            dados_filtrados.append(item)
        self.rv.data = dados_filtrados
        # Atualiza altura do recycleview
        self.rv_recycle_layout.height = len(dados_filtrados) * 60

    # =========== ABA BUSCA ===========
    def mostrar_busca(self):
        self.conteudo.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Buscar Item', size_hint_y=0.1))
        self.busca_input2 = TextInput(multiline=False, hint_text='Digite o código')
        layout.add_widget(self.busca_input2)
        btn_buscar = Button(text='Buscar', size_hint_y=0.1)
        btn_buscar.bind(on_press=self.buscar_item)
        layout.add_widget(btn_buscar)
        self.resultado_busca = ScrollView(size_hint_y=0.6)
        self.resultado_label = Label(text='', size_hint_y=None, halign='left', valign='top')
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.resultado_busca.add_widget(self.resultado_label)
        layout.add_widget(self.resultado_busca)
        self.conteudo.add_widget(layout)

    def buscar_item(self, instance):
        codigo = self.busca_input2.text.strip()
        if not codigo:
            return
        alvo = normalizar(codigo)
        for item in self.dados:
            if normalizar(item['codigo']) == alvo:
                self.mostrar_detalhes_item(item)
                return
        self.resultado_label.text = 'Item não encontrado.'

    def mostrar_detalhes_item(self, item):
        if item['status'] == 'Auditado':
            msg = f"Código: {item['codigo']}\nDescrição: {item['descricao']}\nStatus: Auditado\nData: {item['data_auditoria']}\nObs: {item['observacoes']}"
            pop = Popup(title='Item Auditado', content=Label(text=msg), size_hint=(0.8,0.6))
            pop.open()
        else:
            # Popup com opção de auditar
            layout = BoxLayout(orientation='vertical', padding=10)
            layout.add_widget(Label(text=f"Item: {item['descricao']}"))
            layout.add_widget(Label(text=f"Código: {item['codigo']}"))
            obs_input = TextInput(multiline=True, hint_text='Observações', height=100)
            layout.add_widget(obs_input)
            btn_auditar = Button(text='Auditar')
            layout.add_widget(btn_auditar)
            pop = Popup(title='Auditar Item', content=layout, size_hint=(0.8,0.6))
            def auditar(inst):
                data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                salvar_item(item['codigo'], item['descricao'], 'Auditado', data_agora, obs_input.text, item['quantidade'], item['local'], self.obra_id)
                self.carregar_dados()
                if self.aba_atual == 'lista':
                    self.filtrar_lista()
                pop.dismiss()
                self.resultado_label.text = f'"{item["descricao"]}" auditado!'
            btn_auditar.bind(on_press=auditar)
            pop.open()

    # =========== ABA CADASTRO ===========
    def mostrar_cadastro(self):
        self.conteudo.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Cadastrar Novo Item', size_hint_y=0.1))
        self.codigo_input = TextInput(hint_text='Código (opcional)', multiline=False)
        layout.add_widget(self.codigo_input)
        self.desc_input = TextInput(hint_text='Descrição *', multiline=False)
        layout.add_widget(self.desc_input)
        self.local_input = TextInput(hint_text='Local *', multiline=False)
        layout.add_widget(self.local_input)
        self.qtd_input = TextInput(hint_text='Quantidade', multiline=False, text='1')
        layout.add_widget(self.qtd_input)
        self.obs_cadastro = TextInput(hint_text='Observações', multiline=True, height=80)
        layout.add_widget(self.obs_cadastro)

        # Opções: Sobra ou Sem Patrimônio
        tipo_sp = Spinner(text='Normal', values=('Normal', 'Sobra', 'Sem Patrimonio'), size_hint_y=0.08)
        layout.add_widget(tipo_sp)

        btn_salvar = Button(text='Salvar', size_hint_y=0.08)
        btn_salvar.bind(on_press=lambda x: self.salvar_cadastro(tipo_sp.text))
        layout.add_widget(btn_salvar)
        self.conteudo.add_widget(layout)

    def salvar_cadastro(self, tipo):
        codigo = self.codigo_input.text.strip()
        desc = self.desc_input.text.strip()
        local = self.local_input.text.strip()
        qtd = self.qtd_input.text.strip() or '1'
        obs = self.obs_cadastro.text.strip()

        if not desc or not local:
            pop = Popup(title='Erro', content=Label(text='Preencha descrição e local.'), size_hint=(0.7,0.3))
            pop.open()
            return

        # Verifica duplicidade
        if tipo == 'Sobra':
            desc_final = f"[SOBRA] {desc}"
            if codigo:
                # Verifica se código já existe
                for item in self.dados:
                    if item['codigo'] == codigo:
                        pop = Popup(title='Erro', content=Label(text='Código já existe.'), size_hint=(0.7,0.3))
                        pop.open()
                        return
            else:
                # Gera código automático
                codigo = f"SOBRA_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex().upper()}"
        elif tipo == 'Sem Patrimonio':
            desc_final = f"[SEM PATRIMONIO] {desc}"
            if not codigo:
                codigo = f"SEM_PAT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex().upper()}"
        else:
            desc_final = desc
            if not codigo:
                pop = Popup(title='Erro', content=Label(text='Código obrigatório para item normal.'), size_hint=(0.7,0.3))
                pop.open()
                return

        # Verifica se o código já existe na obra
        for item in self.dados:
            if item['codigo'] == codigo:
                pop = Popup(title='Erro', content=Label(text='Código já existe nesta obra.'), size_hint=(0.7,0.3))
                pop.open()
                return

        # Salva
        data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_item(codigo, desc_final, 'Auditado', data_agora, obs, qtd, local, self.obra_id)
        self.carregar_dados()
        if self.aba_atual == 'lista':
            self.filtrar_lista()
        pop = Popup(title='Sucesso', content=Label(text='Item cadastrado!'), size_hint=(0.7,0.3))
        pop.open()
        # Limpa campos
        self.codigo_input.text = ''
        self.desc_input.text = ''
        self.local_input.text = ''
        self.qtd_input.text = '1'
        self.obs_cadastro.text = ''

    # =========== ABA DASHBOARD ===========
    def mostrar_dashboard(self):
        self.conteudo.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        total = len(self.dados)
        auditados = sum(1 for item in self.dados if item['status'] == 'Auditado')
        pendentes = total - auditados
        sobras = sum(1 for item in self.dados if item['descricao'].startswith('[SOBRA]'))
        sem_pat = sum(1 for item in self.dados if item['descricao'].startswith('[SEM PATRIMONIO]'))

        layout.add_widget(Label(text=f"Total: {total}", font_size='20sp'))
        layout.add_widget(Label(text=f"Auditados: {auditados}", font_size='18sp', color=(0,0.6,0,1)))
        layout.add_widget(Label(text=f"Pendentes: {pendentes}", font_size='18sp', color=(0.8,0.6,0,1)))
        layout.add_widget(Label(text=f"Sobras: {sobras}", font_size='18sp', color=(0.4,0.2,0.8,1)))
        layout.add_widget(Label(text=f"Sem Patrimônio: {sem_pat}", font_size='18sp', color=(0.2,0.4,0.8,1)))
        if total > 0:
            progresso = auditados / total
            layout.add_widget(Label(text=f"Progresso: {progresso*100:.1f}%", font_size='18sp'))
            # Barra de progresso simples
            bar = BoxLayout(size_hint_y=0.05, spacing=2)
            bar.add_widget(Label(text='', size_hint_x=progresso, background_color=(0,0.6,0,1)))
            bar.add_widget(Label(text='', size_hint_x=1-progresso, background_color=(0.8,0.6,0,1)))
            layout.add_widget(bar)
        self.conteudo.add_widget(layout)

    # =========== ABA SOBRE ===========
    def mostrar_sobre(self):
        self.conteudo.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Auditoria de Ativos', font_size='24sp', bold=True))
        layout.add_widget(Label(text='Versão offline 1.0', font_size='16sp'))
        layout.add_widget(Label(text='Desenvolvido por Robespierre Santana Silva', font_size='14sp', color=(0.4,0.4,0.4,1)))
        layout.add_widget(Label(text='Banco de dados local SQLite', font_size='14sp', color=(0.4,0.4,0.4,1)))
        layout.add_widget(Label(text='Funcionalidades: importar Excel, cadastro, auditoria, dashboard', font_size='14sp', color=(0.4,0.4,0.4,1)))
        self.conteudo.add_widget(layout)

    # =========== IMPORTAR EXCEL ===========
    def importar_excel_popup(self):
        # FileChooser para Android (ou desktop)
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView()
        content.add_widget(filechooser)
        btn_importar = Button(text='Importar', size_hint_y=0.1)
        content.add_widget(btn_importar)
        pop = Popup(title='Selecione o arquivo Excel', content=content, size_hint=(0.9,0.9))
        def importar(inst):
            if filechooser.selection:
                path = filechooser.selection[0]
                novos, alterados, iguais = importar_excel(path, self.obra_id)
                if novos == -1:
                    pop.dismiss()
                    pop_erro = Popup(title='Erro', content=Label(text='Falha ao importar.'), size_hint=(0.7,0.3))
                    pop_erro.open()
                else:
                    self.carregar_dados()
                    if self.aba_atual == 'lista':
                        self.filtrar_lista()
                    pop.dismiss()
                    pop_sucesso = Popup(title='Sucesso', content=Label(text=f'Importados: {novos} novos, {alterados} atualizados, {iguais} iguais'), size_hint=(0.8,0.4))
                    pop_sucesso.open()
        btn_importar.bind(on_press=importar)
        pop.open()

    # =========== EXPORTAR EXCEL ===========
    def exportar_excel(self):
        dados = exportar_excel(self.obra_id)
        if dados is None:
            pop = Popup(title='Erro', content=Label(text='Nenhum dado para exportar.'), size_hint=(0.7,0.3))
            pop.open()
            return
        # No Android, salvar em /storage/emulated/0/Download/
        filename = f"inventario_{self.obra_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        save_path = os.path.join(os.path.expanduser('~'), 'Downloads', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(dados)
        pop = Popup(title='Exportado', content=Label(text=f'Arquivo salvo em {save_path}'), size_hint=(0.8,0.4))
        pop.open()

class AuditoriaApp(App):
    def build(self):
        criar_banco()
        return MainScreen()

if __name__ == '__main__':
    AuditoriaApp().run()