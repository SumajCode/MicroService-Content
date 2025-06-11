import json

def test_health_endpoint(client):
    """Test que verifica que el endpoint /health funciona correctamente"""
    response = client.get('/health')
    
    # Verificar que la respuesta es exitosa
    assert response.status_code == 200
    
    # Verificar que la respuesta es JSON válido
    data = json.loads(response.data)
    
    # Verificar la estructura de la respuesta
    assert data['status'] == 'success'
    assert data['code'] == 200
    assert data['message'] == 'Servicio funcionando correctamente'
    assert 'data' in data
    assert data['data']['service'] == 'MicroService-Content'
    assert data['data']['version'] == '2.0.0'
    assert data['data']['testing'] == True

def test_home_endpoint(client):
    """Test que verifica que el endpoint raíz funciona correctamente"""
    response = client.get('/')
    
    # Verificar que la respuesta es exitosa
    assert response.status_code == 200
    
    # Verificar que la respuesta es JSON válido
    data = json.loads(response.data)
    
    # Verificar la estructura de la respuesta
    assert data['status'] == 'success'
    assert data['code'] == 200
    assert 'endpoints' in data['data']
    assert data['data']['testing'] == True

def test_404_error_handler(client):
    """Test que verifica el manejo de errores 404"""
    response = client.get('/endpoint-inexistente')
    
    # Verificar que devuelve 404
    assert response.status_code == 404
    
    # Verificar que la respuesta es JSON válido
    data = json.loads(response.data)
    
    # Verificar la estructura del error
    assert data['status'] == 'error'
    assert data['code'] == 404
    assert data['message'] == 'Endpoint no encontrado'
    assert data['data'] is None
