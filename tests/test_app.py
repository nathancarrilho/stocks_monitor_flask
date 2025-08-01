"""
Testes para Stock Dashboard
Cada função testa UMA coisa específica
"""
import sys
import os
import pytest
import json

# Adiciona o diretório raiz ao path para encontrar app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
except ImportError as e:
    print(f"❌ Erro ao importar app: {e}")
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📁 Arquivos Python encontrados:")
    for file in os.listdir('.'):
        if file.endswith('.py'):
            print(f"   - {file}")
    raise

# Configuração: cria um "cliente fake" para testar a app
@pytest.fixture
def client():
    """
    Fixture = preparação para os testes
    Cria um cliente que simula requisições HTTP
    """
    app.config['TESTING'] = True  # Modo de teste (não salva logs, etc)
    with app.test_client() as client:
        yield client

# TESTE 1: Página principal funciona?
def test_home_page(client):
    """
    Testa se GET / retorna código 200 (sucesso)
    É como perguntar: "O site abre?"
    """
    response = client.get('/')
    assert response.status_code == 200
    # Se não for 200, teste falha e pipeline para

# TESTE 2: API de teste responde corretamente?
def test_api_test_endpoint(client):
    """
    Testa se GET /api/test retorna JSON válido
    Verifica estrutura da resposta
    """
    response = client.get('/api/test')
    
    # Deve retornar 200 (sucesso)
    assert response.status_code == 200
    
    # Converte JSON para dicionário Python
    data = json.loads(response.data)
    
    # Verifica se tem os campos obrigatórios
    assert 'success' in data
    assert data['success'] == True
    assert 'message' in data

# TESTE 3: Endpoint de cotação tem estrutura correta?
def test_quote_endpoint_structure(client):
    """
    Testa se /api/quote/AAPL retorna dados no formato esperado
    IMPORTANTE: Não testa se AAPL existe, testa se FORMATO está correto
    """
    response = client.get('/api/quote/AAPL')
    
    # Pode dar 200 (encontrou) ou 404 (não encontrou)
    # Ambos são válidos - o importante é não dar 500 (erro de código)
    assert response.status_code in [200, 404]
    
    # Sempre deve retornar JSON válido
    data = json.loads(response.data)
    assert 'success' in data
    
    # Se encontrou dados (success=True), verifica estrutura
    if data['success']:
        assert 'data' in data
        stock_data = data['data']
        
        # Campos obrigatórios que o frontend espera
        required_fields = ['symbol', 'price', 'change', 'change_percent', 'volume']
        for field in required_fields:
            assert field in stock_data, f"Campo '{field}' está faltando!"

# TESTE 4: Múltiplas cotações funcionam?
def test_multiple_quotes_endpoint(client):
    """
    Testa se /api/multiple?symbols=AAPL,GOOGL funciona
    """
    response = client.get('/api/multiple?symbols=AAPL,GOOGL')
    
    # Sempre deve retornar 200 (mesmo se não encontrar dados)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'success' in data
    assert 'data' in data
    
    # data deve ser um dicionário (mesmo que vazio)
    assert isinstance(data['data'], dict)

# TESTE 5: Dados do gráfico têm formato correto?
def test_chart_endpoint_structure(client):
    """
    Testa se /api/chart/AAPL?days=7 retorna formato correto
    """
    response = client.get('/api/chart/AAPL?days=7')
    
    # Pode dar 200 ou 404, mas não 500
    assert response.status_code in [200, 404]
    
    data = json.loads(response.data)
    assert 'success' in data
    
    # Se encontrou dados, deve ser uma lista
    if data['success']:
        assert 'data' in data
        assert isinstance(data['data'], list)
        
        # Se tem dados, cada item deve ter campos de OHLC
        if len(data['data']) > 0:
            first_item = data['data'][0]
            chart_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
            for field in chart_fields:
                assert field in first_item, f"Campo '{field}' faltando nos dados do gráfico!"

# TESTE BÁSICO: Verifica se conseguimos importar a aplicação
def test_app_import():
    """
    Teste básico: verifica se conseguimos importar a aplicação
    """
    assert app is not None
    assert hasattr(app, 'test_client')