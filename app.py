import sys
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
from reportlab.pdfgen import canvas

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)
        

        # Layout principal
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Campo de entrada para CNPJ
        self.cnpj_label = QtWidgets.QLabel('Insira o CNPJ:')
        self.cnpj_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.cnpj_input = QtWidgets.QLineEdit()
        self.cnpj_input.setPlaceholderText('Digite o CNPJ aqui')
        self.cnpj_input.setStyleSheet("font-size: 16px; padding: 6px;")

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
        self.next_button.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #001F3F;")
        self.next_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.next_button.clicked.connect(self.validate_and_process_cnpj)

        # Adicionar widgets ao layout principal
        self.layout.addLayout(cnpj_layout)
        self.layout.addWidget(self.next_button)
        self.layout.addStretch()

        self.setLayout(self.layout)

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
            
            # Passar a informação sobre o CNAE para a próxima janela
            self.product_window_ce = ProductWindowCE(razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples)  # Passando a variável correta
            usar_icone(self.product_window_ce)
            self.product_window_outros = ProductWindowOutros(razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples)
            usar_icone(self.product_window_outros)  # Passando a variável correta
            if uf == 'CE':
                self.product_window_ce.showMaximized()
            else:
                self.product_window_outros.showMaximized()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Ocorreu um erro: {e}')


class ProductWindowCE(QtWidgets.QWidget):
    def __init__(self, razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples):
        super().__init__()
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.info_label.setText(
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
        )

        # Campo para o código do produto
        self.product_code_label = QtWidgets.QLabel('Insira o código do produto:')
        self.product_code_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.product_code_input = QtWidgets.QLineEdit()
        self.product_code_input.setPlaceholderText('Digite o código do produto')
        self.product_code_input.setValidator(QIntValidator())
        self.product_code_input.setStyleSheet("font-size: 16px; padding: 6px;")

        # Campo para a quantidade
        self.quantity_label = QtWidgets.QLabel('Insira a quantidade:')
        self.quantity_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.quantity_input = QtWidgets.QLineEdit()
        self.quantity_input.setPlaceholderText('Digite a quantidade')
        self.quantity_input.setValidator(QIntValidator())
        self.quantity_input.setStyleSheet("font-size: 16px; padding: 6px;")

        # Campo para o valor
        self.value_label = QtWidgets.QLabel('Insira o valor:')
        self.value_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.value_input = QtWidgets.QLineEdit()
        self.value_input.setPlaceholderText('Digite o valor')
        self.value_input.setStyleSheet("font-size: 16px; padding: 6px;")

        # Layouts para organizar os campos
        product_code_layout = QtWidgets.QHBoxLayout()
        product_code_layout.addWidget(self.product_code_label)
        product_code_layout.addWidget(self.product_code_input)

        quantity_layout = QtWidgets.QHBoxLayout()
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_input)

        value_layout = QtWidgets.QHBoxLayout()
        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.value_input)

        # Botão de finalizar
        self.finish_button = QtWidgets.QPushButton('Consultar')
        self.finish_button.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #001F3F;")
        self.finish_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.finish_button.clicked.connect(self.finish_process)

        # Campo para exibir a mensagem de resumo
        self.result_label = QtWidgets.QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 14px; margin-top: 20px;")
        self.result_label.hide()  # Esconde o campo inicialmente

        # Adicionar widgets ao layout principal
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(product_code_layout)
        self.layout.addLayout(quantity_layout)
        self.layout.addLayout(value_layout)
        self.layout.addWidget(self.finish_button)
        self.layout.addWidget(self.result_label)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.cnae_valido = cnae_valido
        self.uf = uf
        self.simples = simples
        self.razao_social = razao_social
        self.cnae_codigo = cnae_codigo
        self.cnpj = cnpj

    def finish_process(self):
        # Obter os valores dos campos
        product_code = self.product_code_input.text().strip()
        quantity = self.quantity_input.text().strip()
        value = self.value_input.text().strip()

        # Verificar se todos os campos foram preenchidos
        if not product_code or not quantity or not value:
            self.result_label.setText("<p style='color: red;'>Por favor, preencha todos os campos.</p>")
            self.result_label.show()
            return

        # Calcular o valor total
        total_value = float(quantity) * float(value)
        total_valor_com_imposto = total_value

        # Consulta ao banco de dados (exemplo simplificado)
        conexao = conectar_com_banco()
        cursor = conexao.cursor()
        cursor.execute("USE atacado_do_vale_comercio_de_alimentos_ltda")
        cursor.execute("SELECT produto, ncm, aliquota FROM cadastro_tributacao WHERE codigo = %s", (product_code,))
        result = cursor.fetchone()

        if result:
            produto, ncm, aliquota = result
        else:
            info_message = "Código de produto não encontrado."
            QtWidgets.QMessageBox.warning(self, 'Erro', info_message)
            return

        # Se o CNPJ não tem CNAE válido, calcular imposto
        if self.cnae_valido == 'Não' and self.uf == 'CE' and self.simples == 'Não':
            if re.match(r'^\d', aliquota):
                aliquota_percentual = float(aliquota.replace('%', '').strip())
                valor_imposto = total_value * (aliquota_percentual / 100)
                total_valor_com_imposto += total_value * (aliquota_percentual / 100)

        # Criar mensagem de resumo
        info_message = f"""
            <p style="font-size: 28px;"><strong>Resumo</strong></p>
            <p style="font-size: 18px;"><strong>Código do Produto:</strong> {product_code}</p>
            <p style="font-size: 18px;"><strong>Produto:</strong> {produto}</p>
            <p style="font-size: 18px;"><strong>NCM:</strong> {ncm}</p>
            <p style="font-size: 18px;"><strong>Quantidade:</strong> {quantity}</p>
            <p style="font-size: 18px;"><strong>Valor Unitário:</strong> R$ {float(value):.2f}</p>
            <p style="font-size: 18px;"><strong>Valor Total:</strong> R$ {total_value:.2f}</p>
            <p style="font-size: 18px;"><strong>Aliquota:</strong> {aliquota}</p>
            <p style="font-size: 18px;"><strong>Valor do Imposto:</strong> R$ {valor_imposto:.2f}</p>
            <p style="font-size: 18px;"><strong>Valor Total com Imposto:</strong> R$ {total_valor_com_imposto:.2f}</p>
        """
        self.result_label.setText(info_message)
        self.result_label.show()

        # Gerar o PDF do resumo
        
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        produtos_folder = os.path.join(downloads_folder, "produtos")
        os.makedirs(produtos_folder, exist_ok=True)

        pdf_path = os.path.join(produtos_folder, f'{product_code}_{self.razao_social}.pdf')
        
        self.generate_pdf(pdf_path, product_code, produto, ncm, quantity, value, total_value, aliquota, valor_imposto ,total_valor_com_imposto)
        QtWidgets.QMessageBox.information(self, 'PDF Salvo', f'PDF salvo em: {pdf_path}')

    def generate_pdf(self, file_path, product_code, produto, ncm, quantity, value, total_value, aliquota, valor_imposto ,total_valor_com_imposto):
        pdf = canvas.Canvas(file_path, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, "Resumo de Consulta")

        pdf.drawString(100, 730, f"Razão Social: {self.razao_social}")
        pdf.drawString(100, 710, f"CNPJ: {self.cnpj}")
        pdf.drawString(100, 690, f"CNAE: {self.cnae_codigo}")
        pdf.drawString(100, 670, f"Código do Produto: {product_code}")
        pdf.drawString(100, 650, f"Produto: {produto}")
        pdf.drawString(100, 630, f"NCM: {ncm}")
        pdf.drawString(100, 610, f"Quantidade: {quantity}")
        pdf.drawString(100, 590, f"Valor Unitário: R$ {float(value):.2f}")
        pdf.drawString(100, 570, f"Valor Total: R$ {total_value:.2f}")
        pdf.drawString(100, 550, f"Aliquota: {aliquota}")
        pdf.drawString(100, 530, f"Valor do Imposto: R$ {valor_imposto:.2f}")
        pdf.drawString(100, 510, f"Valor Total com Imposto: R$ {total_valor_com_imposto:.2f}")

        pdf.save()

class ProductWindowOutros(QtWidgets.QWidget):
    def __init__(self, razao_social, cnpj, cnae_valido, cnae_codigo, uf, simples):
        super().__init__()
        self.setWindowTitle('Consultor de Produto')
        self.setGeometry(400, 200, 900, 700)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.info_label.setText(
            f"<h3>Razão Social: {razao_social}</h3>"
            f"<p><b>CNPJ:</b> {cnpj} | <b>CNAE:</b> {cnae_codigo} | <b>UF:</b> {uf}</p>"
            f"<p><b>Decreto:</b> {cnae_valido} | <b>Simples:</b> {simples}</p>"
        )

        self.quantity_label = QtWidgets.QLabel('Insira a quantidade:')
        self.quantity_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.quantity_input = QtWidgets.QLineEdit()
        self.quantity_input.setPlaceholderText('Digite a quantidade')
        self.quantity_input.setValidator(QIntValidator())
        self.quantity_input.setStyleSheet("font-size: 16px; padding: 6px;")

        quantity_layout = QtWidgets.QHBoxLayout()
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_input)

        self.layout.addWidget(self.info_label)
        self.layout.addLayout(quantity_layout)
        self.layout.addStretch()

        self.setLayout(self.layout)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    usar_icone(main_window)
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
