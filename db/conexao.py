import mysql.connector
from mysql.connector import Error

def conectar_com_banco():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user= 'root',
            password='1234',
            database='atacado_do_vale_comercio_de_alimentos_ltda'
        )
        if conexao.is_connected():
            print('Conectado ao banco de dados')
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    
