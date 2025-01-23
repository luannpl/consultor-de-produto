import sys
import locale
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import os
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtGui import QIntValidator
from utils.cnpj import processar_cnpjs, buscar_informacoes
from utils.icone import baixar_icone, usar_icone
from db.conexao import conectar_com_banco
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QMessageBox
import asyncio
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def recurso_caminho(relativo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relativo)
    return os.path.join(os.path.abspath("."), relativo)
    
caminho_imagem = recurso_caminho("images\\icone.png")

class UserLogin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(400, 200, 900, 700)
        self.setStyleSheet("background-color: #030d18;")

        # Layout principal
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Campo de entrada para usuário
        self.user_label = QtWidgets.QLabel('Usuário:')
        self.user_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; margin: 0px; padding: 0px;")
        self.user_input = QtWidgets.QLineEdit()
        self.user_input.setPlaceholderText('Digite o usuário')
        self.user_input.setStyleSheet("font-size: 20px; padding: 8px; border: 1px solid #ccc; border-radius: 5px; ")

        # Campo de entrada para senha
        self.password_label = QtWidgets.QLabel('Senha:')
        self.password_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; margin: 0px; padding: 0px;")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText('Digite a senha')
        self.password_input.setStyleSheet("font-size: 20px; padding: 8px; border: 1px solid #ccc; border-radius: 5px; ")


        # Botão para login
        self.login_button = QtWidgets.QPushButton('Login')
        self.login_button.setStyleSheet("""QPushButton {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #001F3F;
        }
        QPushButton:hover {
            background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
            color:#ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
        }""")
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.login_button.clicked.connect(self.validate_login)

        # Cria um grupo para o layout
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 20px; border-radius: 10px;")
        group_box.setMaximumWidth(500)  # Aumentando a largura máxima do grupo
        group_box.setMinimumWidth(500)  # Define uma largura mínima para evitar colapso

        # Adiciona o layout ao grupo
        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.setSpacing(10)  # Ajusta o espaçamento vertical entre os widgets
        group_box_layout.setContentsMargins(10, 10, 10, 10)  # Ajusta margens internas do grupo
        group_box_layout.addWidget(self.user_label)
        group_box_layout.addWidget(self.user_input)
        group_box_layout.addWidget(self.password_label)
        group_box_layout.addWidget(self.password_input)
        group_box_layout.addWidget(self.login_button)
        group_box.setLayout(group_box_layout)

        # Mensagem de informação
        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)

        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

    def validate_login(self):
        user = self.user_input.text().strip()
        password = self.password_input.text().strip()
        conexao = conectar_com_banco()
        cursor = conexao.cursor()
        cursor.execute("USE projeto_produtos")
        cursor.execute("SELECT senha FROM user WHERE nome = %s", (user,))
        result = cursor.fetchone()
        
        if not result:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválidos.')
            return
        result = result[0]
        

        if password == result:
            self.main_window = MainWindow(user)
            usar_icone(self.main_window)
            self.main_window.showMaximized()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválidos.')
    
    
class MainWindow(QtWidgets.QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)
        self.setStyleSheet("background-color: #030d18;")
        self.user = user

        # Layout principal
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Campo de entrada para CNPJ
        self.cnpj_label = QtWidgets.QLabel('Insira o CNPJ do fornecedor:')
        self.cnpj_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        self.cnpj_input = QtWidgets.QLineEdit()
        self.cnpj_input.setStyleSheet("font-size: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; ")
        self.cnpj_input.setFixedWidth(400)

        # Validador para aceitar apenas números e configurar máscara de CNPJ
        int_validator = QIntValidator()
        self.cnpj_input.setValidator(int_validator)
        self.cnpj_input.setInputMask('99.999.999/9999-99')

        # Layout para o campo de entrada do CNPJ
        cnpj_layout = QtWidgets.QHBoxLayout()
        cnpj_layout.addWidget(self.cnpj_label)
        cnpj_layout.addWidget(self.cnpj_input)

        # Botão para avançar
        self.next_button = QtWidgets.QPushButton('Avançar')
        self.next_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: #001F3F;
            }
            QPushButton:hover {
                background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
                color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
            }
        """)
        self.next_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.next_button.clicked.connect(self.validate_and_process_cnpj)

        # Cria um grupo para o layout
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 20px; border-radius: 10px;")


        # Adiciona o layout ao grupo
        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addLayout(cnpj_layout)
        group_box_layout.addWidget(self.next_button)
        group_box.setLayout(group_box_layout)

        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)
        # footer_layout.addStretch()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)
    
    def showEvent(self, event):
        """Limpa o campo de entrada sempre que a janela for exibida."""
        self.cnpj_input.clear()
        super().showEvent(event)

    def validate_and_process_cnpj(self):
        cnpj = self.cnpj_input.text().strip().replace('.', '').replace('/', '').replace('-', '')

        # Validações
        if not cnpj or len(cnpj) != 14:
            QMessageBox.warning(self, 'Erro', 'Por favor, insira um CNPJ válido.')
            return

        # Chamar a função para processar o CNPJ
        asyncio.run(self.process_cnpj(cnpj))

    async def process_cnpj(self, cnpj):
        try:
            razao_social, cnae_codigo, existe_no_lista, uf, simples = await buscar_informacoes(cnpj)

            if not cnae_codigo:  # Abrir próxima janela
                QMessageBox.warning(self, 'Erro', 'Não foi possível obter informações para o CNPJ fornecido.')
                return
            self.product_window_ce_sim = ProductWindowCESIM(self,razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples)
            usar_icone(self.product_window_ce_sim)  # Passando a variável correta
            self.product_window_ce = ProductWindowCE(self,razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples, self.user)  # Passando a variável correta
            usar_icone(self.product_window_ce)
            self.product_window_outros = ProductWindowOutros(self,razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples)
            usar_icone(self.product_window_outros)  # Passando a variável correta
            if uf == 'CE':
                if existe_no_lista == 'Sim':
                    self.product_window_ce_sim.showMaximized()
                else:
                    self.product_window_ce.showMaximized()
            else:
                self.product_window_outros.showMaximized()

            self.close()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Ocorreu um erro: {e}')

class ProductWindowCESIM(QtWidgets.QWidget):
    def __init__(self, main_window,razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Consultor de Produto')
        self.setStyleSheet("background-color: #030d18;")
        self.setGeometry(400, 200, 900, 700)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.info_label.setText(
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
            f"<hr>"
        )

        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.info_message.setText(
            f"<h1>CNPJ ESTÁ ISENTO DE IMPOSTOS NO CEARÁ.</h1>"
        )

        self.btn_voltar = QtWidgets.QPushButton('Nova Consulta')
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: #001F3F;
            }
            QPushButton:hover {
                background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
                color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
            }
        """)
        self.btn_voltar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_voltar.clicked.connect(self.voltar)

        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 16px; border-radius: 10px;")
        group_box.setFixedWidth(1000)

        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addWidget(self.info_label)
        group_box_layout.addWidget(self.info_message)
        group_box_layout.addWidget(self.btn_voltar)
        group_box_layout.addStretch()
        group_box.setLayout(group_box_layout)

        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)
        # footer_layout.addStretch()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        # center_layout.addWidget(self.info_message, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout) 

    def voltar(self):
        self.main_window.showMaximized()
        self.close()
class ProductWindowCE(QtWidgets.QWidget):
    def __init__(self, main_window,razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples, user):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)
        self.setStyleSheet("background-color: #030d18;")
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.info_label.setText(
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
            f"<hr>"
        )

        # Campo para o código do produto
        self.product_code_label = QtWidgets.QLabel('Insira o código do produto:')
        self.product_code_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.product_code_input = QtWidgets.QLineEdit()
        self.product_code_input.setPlaceholderText('Digite o código do produto')
        self.product_code_input.setValidator(QIntValidator())
        self.product_code_input.setStyleSheet("font-size: 20px; padding: 6px; border: 1px solid #ccc; border-radius: 5px;")

        # Layouts para organizar os campos
        product_code_layout = QtWidgets.QHBoxLayout()
        product_code_layout.addWidget(self.product_code_label)
        product_code_layout.addWidget(self.product_code_input)

        # Botão de finalizar
        self.finish_button = QtWidgets.QPushButton('Consultar')
        self.finish_button.setStyleSheet("""QPushButton {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #001F3F;
        }
        QPushButton:hover {
            background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
            color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
        }""")
        self.finish_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.finish_button.clicked.connect(self.resumo)

        self.btn_voltar = QtWidgets.QPushButton('Novo Fornecedor')
        self.btn_voltar.setStyleSheet("""QPushButton {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #001F3F;
        }
        QPushButton:hover {
            background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
            color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
        }""")
        self.btn_voltar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_voltar.clicked.connect(self.voltar)

        # Cria um grupo para o layout
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 16px; border-radius: 10px;")
        group_box.setFixedWidth(800)
        # group_box.setMinimumWidth(600)

        # Adiciona o layout ao grupo
        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addWidget(self.info_label)
        group_box_layout.addLayout(product_code_layout)
        group_box_layout.addWidget(self.finish_button)
        group_box_layout.addWidget(self.btn_voltar)
        group_box_layout.addStretch()
        group_box.setLayout(group_box_layout)

        # Cria um layout horizontal para centralizar o conteúdo
        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)
        # footer_layout.addStretch()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        # center_layout.addWidget(self.info_message, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout) 

        self.cnae_valido = cnae_valido
        self.uf = uf
        self.simples = simples
        self.razao_social = razao_social
        self.cnae_codigo = cnae_codigo
        self.cnpj = cnpj
        self.user = user

    def voltar(self):
        self.main_window.showMaximized()
        self.close()

    def showEvent(self, event):
        """Limpa o campo de entrada sempre que a janela for exibida."""
        self.product_code_input.clear()
        super().showEvent(event)

    def converter_aliquota(self,aliquota):
        """Converte uma string que representa uma alíquota para um número."""
        # Remove o símbolo de porcentagem, se houver
        aliquota = aliquota.strip().replace("%", "")
        
        # Converte a string para um número
        try:
            aliquota = float(aliquota)
        except ValueError:
            raise ValueError("Alíquota inválida")
        
        return aliquota

    def generate_pdf(self, file_path, product_code, produto, ncm, aliquota):
        try:
            aliquota_adicional_convertida = 0
            print(self.simples)
            if self.simples == 'Não':
                aliquota_adicional = 0
            else:
                aliquota_adicional = '3.00%'
                aliquota_adicional_convertida = self.converter_aliquota(aliquota_adicional)
            
            
            
            aliquota_convertida = self.converter_aliquota(aliquota)
            aliquota_total = float(aliquota_convertida) + float(aliquota_adicional_convertida)
            aliquota_total = f"{aliquota_total:.2f}%"
            # Verificar se o diretório existe e criar se necessário
            output_dir = os.path.dirname(file_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Criação do documento PDF
            pdf = SimpleDocTemplate(file_path, pagesize=letter)

            # Dados para a tabela
            data = [
                ["Campo", "Informação"],
                ["Razão Social", self.razao_social],
                ["CNPJ", self.cnpj],
                ["CNAE", self.cnae_codigo],
                ["UF", self.uf],
                ["DECRETO", self.cnae_valido],
                ["SIMPLES", self.simples],
                ["Código do Produto", product_code],
                ["Produto", produto],
                ["NCM", ncm],
                ["Alíquota", aliquota],
                ["Alíquota (simples)", aliquota_adicional],
                ["Alíquota Total", aliquota_total],
            ]
            
            # Configuração da tabela
            table = Table(data, colWidths=[150, 300])  # Define larguras das colunas
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Fundo cinza para o cabeçalho
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Texto branco no cabeçalho
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Alinhamento à esquerda
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Fonte em negrito no cabeçalho
                ("FONTSIZE", (0, 0), (-1, -1), 12),  # Tamanho da fonte
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # Espaçamento abaixo do cabeçalho
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),  # Fundo bege para as demais células
                ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Grelha preta em todas as células
            ]))
            
            # Adiciona a tabela ao PDF
            elements = [table]
            pdf.build(elements)
            
            # Mensagem de sucesso
            QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso em:\n{file_path}")
        
        except PermissionError:
            # Trata o erro se o arquivo estiver aberto ou não puder ser gravado
            QMessageBox.warning(self, "Erro", f"Não foi possível salvar o arquivo.\n"
                                            f"Certifique-se de que o arquivo não está aberto")
        except Exception as e:
            # Trata qualquer outro erro genérico
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao gerar o PDF:\n{str(e)}")

    
    def resumo(self):
        user = self.user
        product_code = self.product_code_input.text().strip()
        conexao = conectar_com_banco()
        cursor = conexao.cursor()
        if user == 'atacado':
            cursor.execute("USE atacado_do_vale_comercio_de_alimentos_ltda")
            cursor.execute("SELECT produto, ncm, aliquota FROM cadastro_tributacao WHERE codigo = %s", (product_code,))
            result = cursor.fetchone()
        elif user == 'jm':
            cursor.execute("USE jm_supermercado_comercio_de_alimentos_ltda")
            cursor.execute("SELECT produto, ncm, aliquota FROM cadastro_tributacao WHERE codigo = %s", (product_code,))
            result = cursor.fetchone()
        else:
            cursor.execute("USE atacado_do_vale_comercio_de_alimentos_ltda")
            cursor.execute("SELECT produto, ncm, aliquota FROM cadastro_tributacao WHERE codigo = %s", (product_code,))
            result = cursor.fetchone()

        if result:
            produto, ncm, aliquota = result
        else:
            info_message = "Código de produto não encontrado."
            QtWidgets.QMessageBox.warning(self, 'Erro', info_message)
            return
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        produtos_folder = os.path.join(downloads_folder, "produtos")
        os.makedirs(produtos_folder, exist_ok=True)

        pdf_path = os.path.join(produtos_folder, f'{product_code}_{self.razao_social}.pdf')
        
        
        self.generate_pdf(pdf_path, product_code, produto, ncm, aliquota )
        # QtWidgets.QMessageBox.information(self, 'PDF Salvo', f'PDF salvo em: {pdf_path}')
        self.resumo_window = ResumoWindow(self, self.main_window ,self.razao_social, self.cnpj, self.cnae_valido, self.cnae_codigo, self.uf, self.simples, product_code, produto, ncm, aliquota)
        usar_icone(self.resumo_window)
        self.resumo_window.showMaximized()
        self.close()

class ResumoWindow(QtWidgets.QWidget):
    def __init__(self, product_window, main_window, razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples, product_code, produto, ncm, aliquota):
        super().__init__()
        self.product_window = product_window
        self.main_window = main_window
        self.setWindowTitle('Resumo da Consulta')
        self.setGeometry(400, 200, 900, 700)
        self.setStyleSheet("background-color: #030d18;")


        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        aliquota_adicional_convertida = 0
        print(simples)
        if simples == 'Não':
            aliquota_adicional = 0
        else:
            aliquota_adicional = '3.00%'
            aliquota_adicional_convertida = self.converter_aliquota(aliquota_adicional)
        
        
        
        aliquota_convertida = self.converter_aliquota(aliquota)
        aliquota_total = float(aliquota_convertida) + float(aliquota_adicional_convertida)
        aliquota_total = f"{aliquota_total:.2f}%"

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.info_label.setText(
            f"<h1>Resumo da Consulta</h1>"
            f"<h2>Dados do Fornecedor</h2>"
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
            f"<hr>"
            f"<h2>Dados do Produto</h2>"
            f"<p><b>Código do Produto:</b> {product_code}</p>"
            f"<p><b>Produto:</b> {produto}</p>"
            f"<p><b>NCM:</b> {ncm}</p>"
            f"<p><b>Aliquota:</b> {aliquota}</p>"
            f"<p><b>Aliquota Adicional(simples):</b> {aliquota_adicional}</p>"
            f"<p><b>Aliquota Total:</b> {aliquota_total}</p>"
        )

        self.btn_voltar = QtWidgets.QPushButton('Nova Consulta')
        self.btn_voltar.setStyleSheet("""QPushButton {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #001F3F;
        }
        QPushButton:hover {
            background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
            color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
        }""")
        self.btn_voltar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_voltar.clicked.connect(self.voltar)

        self.btn_home = QtWidgets.QPushButton('Novo Fornecedor')
        self.btn_home.setStyleSheet("""QPushButton {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #001F3F;
        }
        QPushButton:hover {
            background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
            color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
        }""")
        self.btn_home.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_home.clicked.connect(self.home)

        # Cria um grupo para o layout
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 10px; border-radius: 10px;")

        # Adiciona o layout ao grupo
        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addWidget(self.info_label)

        # Cria um layout horizontal para os botões
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_home)
        button_layout.addWidget(self.btn_voltar)

        group_box_layout.addLayout(button_layout)  # Adiciona o layout de botões
        group_box_layout.addStretch()
        group_box.setLayout(group_box_layout)

        # Cria um layout horizontal para centralizar o conteúdo
        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)
        # footer_layout.addStretch()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        # center_layout.addWidget(self.info_message, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

    def converter_aliquota(self,aliquota):
        """Converte uma string que representa uma alíquota para um número."""
        # Remove o símbolo de porcentagem, se houver
        aliquota = aliquota.strip().replace("%", "")
        
        # Converte a string para um número
        try:
            aliquota = float(aliquota)
        except ValueError:
            raise ValueError("Alíquota inválida")
        
        return aliquota

    def voltar(self):
        self.product_window.showMaximized()
        self.close()


    def home(self):
        self.main_window.showMaximized()
        self.close()

class ProductWindowOutros(QtWidgets.QWidget):
    def __init__(self, main_window,razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)
        self.setStyleSheet("background-color: #030d18;")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.info_label.setText(
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
            f"<hr>"
        )

        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.info_message.setText(
            f"<h1>CNPJ FORA DO CEARÁ.</h1>"
        )

        self.btn_voltar = QtWidgets.QPushButton('Nova Consulta')
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: #001F3F;
            }
            QPushButton:hover {
                background-color: #005588;  /* Cor de fundo quando o mouse passa sobre o botão */
                color: #ffffff;  /* Cor do texto quando o mouse passa sobre o botão */
            }
        """)
        self.btn_voltar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_voltar.clicked.connect(self.voltar)

        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("background-color: #440416; padding: 16px; border-radius: 10px;")
        group_box.setFixedWidth(800)

        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.addWidget(self.info_label)
        group_box_layout.addWidget(self.info_message)
        group_box_layout.addWidget(self.btn_voltar)
        group_box_layout.addStretch()
        group_box.setLayout(group_box_layout)

        self.info_message = QtWidgets.QLabel()
        self.info_message.setWordWrap(True)
        self.info_message.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center; margin-top: 65px; color: #fff;")
        data_atual = datetime.now()
        
        # Pega a data do mês anterior
        data_anterior = data_atual - relativedelta(months=1)
        mes_anterior = data_anterior.month
        ano_anterior = data_anterior.year

        self.info_message.setText(f"Atualizado até {mes_anterior}/{ano_anterior} v1.0.7")
        self.info_message.setAlignment(QtCore.Qt.AlignCenter)

        self.logo = QtWidgets.QLabel()
        self.logo.setAlignment(QtCore.Qt.AlignRight)  # Alinha a logo à direita
        self.logo.setPixmap(QtGui.QPixmap(caminho_imagem).scaled(100, 100))

        self.footer_message = QtWidgets.QLabel()
        self.footer_message.setWordWrap(True)
        self.footer_message.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; text-align: center; margin-top: 70px;")
        self.footer_message.setText("Desenvolvido por: Assertivus Contábil")
        self.footer_message.setAlignment(QtCore.Qt.AlignLeft)

        # Layout para centralizar o grupo de login

        # Layout para o rodapé
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addWidget(self.footer_message)
        footer_layout.addWidget(self.info_message)
        footer_layout.addWidget(self.logo)
        # footer_layout.addStretch()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(group_box, alignment=QtCore.Qt.AlignCenter)
        # center_layout.addWidget(self.info_message, alignment=QtCore.Qt.AlignCenter)
        center_layout.addStretch()

        # Layout principal geral
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(center_layout)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout) 


    def voltar(self):
        self.main_window.showMaximized()
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    login = UserLogin()
    usar_icone(login)
    login.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
