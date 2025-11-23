"""
Script simples para testar a comunicacao entre os servicos
Execute: python test_auth.py
"""

import requests

# URLs dos servicos
OAUTH_URL = "http://localhost:8001"
CLIENT_URL = "http://localhost:8080"

def test_auth():
    """Testa o fluxo de autenticacao"""
    
    # 1. Verificar se OAuth esta rodando
    try:
        resp = requests.get(f"{OAUTH_URL}/")
        print(f"[OK] OAuth rodando: {resp.status_code}")
    except:
        print("[ERROR] OAuth nao esta rodando na porta 8001")
        return
    
    # 2. Tentar login
    try:
        login_data = {"username": "admin", "password": "admin"}
        resp = requests.post(f"{OAUTH_URL}/auth/login", json=login_data)
        
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print(f"[OK] Login OK, token: {token[:20]}...")
            
            # 3. Testar caerel-client
            headers = {"Authorization": f"Bearer {token}"}
            resp2 = requests.get(f"{CLIENT_URL}/api/me", headers=headers)
            
            if resp2.status_code == 200:
                print("[OK] Caerel-client autenticado com sucesso!")
            else:
                print(f"[ERROR] Erro caerel-client: {resp2.status_code} - {resp2.text}")
        else:
            print(f"[ERROR] Erro login: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[ERROR] Erro: {e}")

if __name__ == "__main__":
    test_auth()
