import sys
import re
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtGui import QIntValidator
from utils.cnpj import processar_cnpjs, buscar_informacoes
from db.conexao import conectar_com_banco
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QMessageBox
import asyncio

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
            self.product_window = ProductWindow(razao_social,cnpj ,existe_no_lista, cnae_codigo, uf, simples)  # Passando a variável correta
            self.product_window.showMaximized()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Ocorreu um erro: {e}')


class ProductWindow(QtWidgets.QWidget):
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
        self.finish_button = QtWidgets.QPushButton('Enviar')
        self.finish_button.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #001F3F;")
        self.finish_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.finish_button.clicked.connect(self.finish_process)

        # Adicionar widgets ao layout principal
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(product_code_layout)
        self.layout.addLayout(quantity_layout)
        self.layout.addLayout(value_layout)
        self.layout.addWidget(self.finish_button)
        self.layout.addStretch()

        self.setLayout(self.layout)

        # Armazenar a informação sobre o CNAE
        self.cnae_valido = cnae_valido
        self.uf = uf
        self.simples = simples

    def finish_process(self):
        # Obter os valores dos campos
        product_code = self.product_code_input.text().strip()
        quantity = self.quantity_input.text().strip()
        value = self.value_input.text().strip()

        # Verificar se todos os campos foram preenchidos
        if not product_code or not quantity or not value:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        # Calcular o valor total
        total_value = float(quantity) * float(value)
        total_valor_com_imposto = total_value

        conexao = conectar_com_banco()
        cursor = conexao.cursor()
        cursor.execute("USE atacado_do_vale_comercio_de_alimentos_ltda")
        cursor.execute("SELECT produto, ncm, aliquota FROM cadastro_tributacao WHERE codigo = %s", (product_code,))

        result = cursor.fetchone()
        print(result)
        if result:
            produto, ncm, aliquota = result
        else:
            print(f"Nenhum registro encontrado para o código {product_code}.")
            info_message = "Código de produto não encontrado."
            QtWidgets.QMessageBox.warning(self, 'Erro', info_message)
            return
        # Se o CNPJ não tem CNAE válido, adicionar R$ 10 ao total
        if self.cnae_valido == 'Não' and self.uf == 'CE' and self.simples == 'Não':

            if re.match(r'^\d', aliquota):

                aliquota_percentual = float(aliquota.replace('%', '').strip()) 
                total_valor_com_imposto += total_value * (aliquota_percentual/100)

            else:
                print(f"Alíquota 0")
        
        info_message = f"""
        <h3 style="color: #2e86c1; text-align: center;">Resumo</h3>
        <p><strong>Código do Produto:</strong> {product_code}</p>
        <p><strong>Produto:</strong> {produto}</p>
        <p><strong>NCM:</strong> {ncm}</p>
        <p><strong>Quantidade:</strong> {quantity}</p>
        <p><strong>Valor Unitário:</strong> R$ {float(value):.2f}</p>
        <p><strong>Valor Total:</strong> <span style="color: #28b463;">R$ {total_value:.2f}</span></p>
        <p><strong>Aliquota:</strong> {aliquota}</p>
        <p><strong>Valor Total com Imposto:</strong> <span style="color: #c0392b;">R$ {total_valor_com_imposto:.2f}</span></p>
        """
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Resumo do Produto")
        msg_box.setIcon(QtWidgets.QMessageBox.Information)  # Ícone de informação
        msg_box.setTextFormat(QtCore.Qt.RichText)  # Habilitar formatação HTML
        msg_box.setText(info_message)

        # Configurar o botão
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        ok_button = msg_box.button(QtWidgets.QMessageBox.Ok)
        ok_button.setStyleSheet("background-color: #2e86c1; color: white; font-weight: bold;")

        # Exibir a mensagem
        msg_box.exec()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
