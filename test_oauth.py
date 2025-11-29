"""
Script para testar o servidor OAuth2
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def register_user(email, username, password, full_name=None):
    """Registra um novo usuário"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name
    }
    
    print(f"\n[COMMANDS] Registrando usuário: {username}")
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("[OK] Usuário registrado com sucesso!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print(f"[ERROR] Erro no registro: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None


def login_user(username, password):
    """Faz login e retorna o token"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    print(f"\n[SECURITY] Fazendo login: {username}")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("[OK] Login realizado com sucesso!")
        data = response.json()
        print(f"Token: {data['access_token'][:50]}...")
        print(f"Expira em: {data['expires_in']} segundos")
        return data['access_token']
    else:
        print(f"[ERROR] Erro no login: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None


def get_user_info(token):
    """Obtém informações do usuário autenticado"""
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\n👤 Obtendo informações do usuário")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("[OK] Informações obtidas com sucesso!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print(f"[ERROR] Erro: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None


def verify_token(token):
    """Verifica se o token é válido"""
    url = f"{BASE_URL}/auth/verify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\n[SEARCH] Verificando token")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("[OK] Token válido!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print(f"[ERROR] Token inválido: {response.status_code}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("[SECURITY] TESTE DO SERVIDOR OAUTH2")
    print("=" * 60)
    
    # Dados de teste
    test_user = {
        "email": "teste@exemplo.com",
        "username": "usuario_teste",
        "password": "senha123",
        "full_name": "Usuário de Teste"
    }
    
    # 1. Registrar usuário
    user = register_user(
        test_user["email"],
        test_user["username"],
        test_user["password"],
        test_user["full_name"]
    )
    
    if not user:
        print("\n[WARNING]  Usuário pode já existir, tentando fazer login...")
    
    # 2. Fazer login
    token = login_user(test_user["username"], test_user["password"])
    
    if token:
        # 3. Obter informações do usuário
        get_user_info(token)
        
        # 4. Verificar token
        verify_token(token)
    
    print("\n" + "=" * 60)
    print("[OK] Teste concluído!")
    print("=" * 60)
