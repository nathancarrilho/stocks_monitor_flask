# ============================================
# PARTE 1: IMPORTAÇÕES (bibliotecas que vamos usar)
# ============================================
from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

# ============================================
# PARTE 2: CRIAR A APLICAÇÃO FLASK
# ============================================
app = Flask(__name__)

# ============================================
# PARTE 3: FUNÇÕES PARA BUSCAR DADOS DA BOLSA
# ============================================

def buscar_cotacao(simbolo):
    """
    Esta função vai na internet buscar o preço de uma ação
    Exemplo: buscar_cotacao("AAPL") vai buscar o preço da Apple
    """
    try:
        # URL da API do Yahoo Finance (gratuita)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
        
        # Cabeçalhos para parecer um navegador normal
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Faz a requisição para a API
        resposta = requests.get(url, headers=headers, timeout=10)
        dados = resposta.json()
        
        # Extrai as informações importantes
        if 'chart' in dados and dados['chart']['result']:
            info = dados['chart']['result'][0]['meta']
            
            preco_atual = info.get('regularMarketPrice', 0)
            preco_anterior = info.get('previousClose', preco_atual)
            mudanca = preco_atual - preco_anterior
            mudanca_percentual = (mudanca / preco_anterior * 100) if preco_anterior > 0 else 0
            
            # Retorna um dicionário com os dados organizados
            # IMPORTANTE: usar os mesmos nomes que o HTML espera
            return {
                'symbol': simbolo.upper(),  # HTML espera 'symbol'
                'price': round(preco_atual, 2),  # HTML espera 'price'
                'change': round(mudanca, 2),  # HTML espera 'change'
                'change_percent': f"{mudanca_percentual:.2f}%",  # HTML espera 'change_percent'
                'volume': info.get('regularMarketVolume', 0),  # HTML espera 'volume'
                'last_updated': datetime.now().strftime('%Y-%m-%d')  # HTML espera 'last_updated'
            }
    except Exception as erro:
        print(f"Erro ao buscar {simbolo}: {erro}")
        return None

def buscar_dados_historicos(simbolo, dias=30):
    """
    Busca dados históricos de uma ação para fazer gráficos
    Exemplo: buscar_dados_historicos("AAPL", 30) - últimos 30 dias
    """
    try:
        # Calcula as datas
        from datetime import datetime, timedelta
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)
        
        # Converte para timestamp (formato que a API entende)
        timestamp_inicio = int(data_inicio.timestamp())
        timestamp_fim = int(data_fim.timestamp())
        
        # URL da API do Yahoo Finance para dados históricos
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
        parametros = {
            'period1': timestamp_inicio,
            'period2': timestamp_fim,
            'interval': '1d',  # 1 dia
            'includePrePost': 'true'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resposta = requests.get(url, params=parametros, headers=headers, timeout=10)
        dados = resposta.json()
        
        if 'chart' in dados and dados['chart']['result']:
            resultado = dados['chart']['result'][0]
            timestamps = resultado['timestamp']
            precos = resultado['indicators']['quote'][0]
            
            dados_grafico = []
            
            # Para cada dia, pega os dados
            for i, timestamp in enumerate(timestamps):
                data = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                # Verifica se todos os dados existem
                if (precos['open'][i] is not None and 
                    precos['high'][i] is not None and
                    precos['low'][i] is not None and
                    precos['close'][i] is not None):
                    
                    dados_grafico.append({
                        'date': data,
                        'open': round(float(precos['open'][i]), 2),
                        'high': round(float(precos['high'][i]), 2),
                        'low': round(float(precos['low'][i]), 2),
                        'close': round(float(precos['close'][i]), 2),
                        'volume': int(precos['volume'][i] or 0)
                    })
            
            return dados_grafico
            
    except Exception as erro:
        print(f"Erro ao buscar dados históricos de {simbolo}: {erro}")
        return []
    """
    Esta função vai na internet buscar o preço de uma ação
    Exemplo: buscar_cotacao("AAPL") vai buscar o preço da Apple
    """
    try:
        # URL da API do Yahoo Finance (gratuita)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
        
        # Cabeçalhos para parecer um navegador normal
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Faz a requisição para a API
        resposta = requests.get(url, headers=headers, timeout=10)
        dados = resposta.json()
        
        # Extrai as informações importantes
        if 'chart' in dados and dados['chart']['result']:
            info = dados['chart']['result'][0]['meta']
            
            preco_atual = info.get('regularMarketPrice', 0)
            preco_anterior = info.get('previousClose', preco_atual)
            mudanca = preco_atual - preco_anterior
            mudanca_percentual = (mudanca / preco_anterior * 100) if preco_anterior > 0 else 0
            
            # Retorna um dicionário com os dados organizados
            # IMPORTANTE: usar os mesmos nomes que o HTML espera
            return {
                'symbol': simbolo.upper(),  # HTML espera 'symbol'
                'price': round(preco_atual, 2),  # HTML espera 'price'
                'change': round(mudanca, 2),  # HTML espera 'change'
                'change_percent': f"{mudanca_percentual:.2f}%",  # HTML espera 'change_percent'
                'volume': info.get('regularMarketVolume', 0),  # HTML espera 'volume'
                'last_updated': datetime.now().strftime('%Y-%m-%d')  # HTML espera 'last_updated'
            }
    except Exception as erro:
        print(f"Erro ao buscar {simbolo}: {erro}")
        return None

# ============================================
# PARTE 4: ROTAS (páginas da aplicação)
# ============================================

@app.route('/')
def pagina_inicial():
    """
    Rota principal - quando alguém acessa http://localhost:5000/
    Mostra a página HTML com o dashboard
    """
    return render_template('dashboard.html')

@app.route('/api/test')
def teste_api():
    """Endpoint para testar se a API está funcionando"""
    return jsonify({
        'success': True,
        'message': 'API funcionando!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/quote/<simbolo>')
def obter_cotacao(simbolo):
    """
    API para buscar uma cotação específica
    Exemplo: GET /api/quote/AAPL
    Retorna dados em formato JSON
    """
    # Busca os dados usando nossa função
    cotacao = buscar_cotacao(simbolo)
    
    if cotacao:
        # Se encontrou dados, retorna sucesso
        return jsonify({
            'success': True,  # Mudei de 'sucesso' para 'success' para bater com o HTML
            'data': cotacao   # Mudei de 'dados' para 'data' para bater com o HTML
        })
    else:
        # Se não encontrou, retorna erro
        return jsonify({
            'success': False,
            'error': f'Não consegui encontrar dados para {simbolo}'
        }), 404

@app.route('/api/chart/<simbolo>')
def obter_dados_grafico(simbolo):
    """
    API para buscar dados históricos para gráficos
    Exemplo: GET /api/chart/AAPL?days=30
    """
    # Pega quantos dias o usuário quer (padrão 30)
    dias = request.args.get('days', 30, type=int)
    
    # Busca os dados históricos
    dados_historicos = buscar_dados_historicos(simbolo, dias)
    
    if dados_historicos and len(dados_historicos) > 0:
        return jsonify({
            'success': True,
            'data': dados_historicos
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Não consegui obter dados históricos para {simbolo}'
        }), 404

@app.route('/api/multiple')
def obter_multiplas_cotacoes():
    """
    API para buscar várias cotações de uma vez
    Exemplo: GET /api/multiple?symbols=AAPL,GOOGL,MSFT
    """
    # Pega os símbolos da URL (ex: ?symbols=AAPL,GOOGL)
    from flask import request  # Precisamos importar request
    simbolos_texto = request.args.get('symbols', '')  # Mudei de 'simbolos' para 'symbols'
    simbolos_lista = [s.strip().upper() for s in simbolos_texto.split(',') if s.strip()]
    
    resultados = {}
    
    # Para cada símbolo, busca a cotação
    for simbolo in simbolos_lista[:5]:  # Máximo 5 para não sobrecarregar
        cotacao = buscar_cotacao(simbolo)
        if cotacao:
            resultados[simbolo] = cotacao
    
    return jsonify({
        'success': True,  # Mudei para 'success'
        'data': resultados  # Mudei para 'data'
    })

@app.route('/api/teste')
def teste_api():
    """
    Rota simples para testar se a API está funcionando
    """
    return jsonify({
        'sucesso': True,
        'mensagem': 'API funcionando!',
        'horario': datetime.now().isoformat()
    })

# ============================================
# PARTE 5: EXECUTAR A APLICAÇÃO
# ============================================
if __name__ == '__main__':
    print("🚀 Iniciando o servidor...")
    print("📊 Dashboard disponível em: http://localhost:5000")
    print("🔧 API de teste em: http://localhost:5000/api/teste")
    
    # Roda o servidor Flask
    app.run(
        host='0.0.0.0',  # Aceita conexões de qualquer IP
        port=5000,       # Porta 5000
        debug=True       # Modo de desenvolvimento (mostra erros)
    )