import aiohttp
import asyncio
import re
from functools import wraps
from time import time

# Função para criar cache
def create_cache(ttl=3600):  # Tempo de vida padrão de 1 hora
    cache_dict = {}
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str((args, frozenset(kwargs.items())))
            now = time()
            if key in cache_dict:
                cached_time, result = cache_dict[key]
                if now - cached_time <= ttl:
                    return result
            result = await func(*args, **kwargs)
            cache_dict[key] = (time(), result)
            return result
        return wrapper
    return decorator

# Função otimizada para remover caracteres não numéricos
def remover_caracteres_nao_numericos(valor):
    return re.sub(r'\D', '', valor)

# Lista de CNAEs pré-definida
lista_cnaes = [
    '4623108', '4623199', '4632001', '4637107', '4639701', '4639702', 
    '4646002', '4647801', '4649408', '4635499', '4637102', '4637199', 
    '4644301', '4632003', '4691500', '4693100', '3240099', '4649499', 
    '8020000', '4711301', '4711302', '4712100', '4721103', '4721104', 
    '4729699', '4761003', '4789005', '4771701', '4771702', '4771703', 
    '4772500', '4763601'
]

# lista_cnaes = [
#     '4644301', '4771701', '4771702','4771703'
# ]

# Dicionário para armazenar resultados em cache
cache_resultados = {}

# Função otimizada para buscar informações do decreto e CNAE
@create_cache()
async def buscar_informacoes(cnpj):
    url = f'https://minhareceita.org/{cnpj}'
    timeout = aiohttp.ClientTimeout(total=10)  # Timeout de 10 segundos
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as resposta:
                if resposta.status == 200:
                    dados = await resposta.json()
                    razao_social = dados.get('razao_social', '')
                    cnae_codigo = str(dados.get('cnae_fiscal', []))
                    existe_no_lista = "Sim" if cnae_codigo in lista_cnaes else "Não"
                    uf = dados.get('uf', '')
                    pegar_simples = dados.get('opcao_pelo_simples', '')
                    simples = "Sim" if pegar_simples == True else "Não"
                    return razao_social, cnae_codigo, existe_no_lista, uf, simples
                else:
                    print(f"Erro na requisição: Status {resposta.status}")
                    return None, None, None, None, None
        except asyncio.TimeoutError:
            print(f"Timeout: A requisição para o CNPJ {cnpj} demorou muito e foi cancelada.")
            return None, None, None, None, None
        except Exception as e:
            print(f"Ocorreu um erro ao buscar informações para o CNPJ {cnpj}: {e}")
            return None, None

# Função para processar uma lista de CNPJs
async def processar_cnpjs(cnpjs):
    resultados = {}
    tasks = []
    for cnpj in cnpjs:
        if cnpj in cache_resultados:
            # Se o CNPJ já estiver no cache, usa o resultado armazenado
            resultados[cnpj] = cache_resultados[cnpj]
        else:
            # Se o CNPJ não estiver no cache, cria uma tarefa para a requisição assíncrona
            tasks.append(_processar_cnpj(cnpj, resultados))
    
    await asyncio.gather(*tasks)
    return resultados

# Função auxiliar para processar cada CNPJ individualmente
async def _processar_cnpj(cnpj, resultados):
    cnae_codigo, existe_no_lista, uf, simples = await buscar_informacoes(cnpj)
    resultados[cnpj] = (cnae_codigo, existe_no_lista, uf, simples)
    cache_resultados[cnpj] = (cnae_codigo, existe_no_lista, uf, simples)


