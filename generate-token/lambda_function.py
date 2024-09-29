import boto3
import json
import base64
import hashlib
import rsa  # Certifique-se de que esta biblioteca esteja incluída
from datetime import datetime, timedelta

# Chave privada hardcoded (exemplo RSA)
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDGDnR6CW1W1VQqXFAKm1HZcpno5QzRoHrDfKbJa2pYBunAaYS1
AvPoUEh7ZCAcQxY1gleQO+dnLrDdoSj2U1njiBl4OV2Vwe2oZXpcs8rFg0aL6f72
crVVr50iY7SodCix+f/5tmSg+K7g1OlrvdydyRi1s1uafuwWuBa66SUuSQIDAQAB
AoGAQbJLyqtT3IjY6VBDsLECvnl4Oju4O9Taw/uWK5v444gvg4a84XpAQ+BVmrCE
wjsyo78/onVsddqUCoBJ4SOW3f/xORzbQKK+SV8BazdMmPPzJTPfH4UFk+PJP+/S
4So5AWXSEE25dd2+IsYGpfX7cFsOl4q7tXUFVStTW157BLECQQDwq+EJfb4/OyG0
N1GYYTXvdHKO+v16nRhatFziHKbNbP8c5jiT9xxRtdN1g3ZAQtDA0jRKwymYUPTs
hjV128mtAkEA0qu+eJZadeLLfx8xxW/81FEsPoB27JyjlDpA3xkSg3A07rNNGHfQ
tiPyRiU53emdeYbItXd6QRJ99W8dvYrCjQJBAKKjhG/liasxSpV+zKUtDEXFa6Uz
+BfkEZE6UYp70j0Aa2YcLh/P3lNZjIzdSgwjGu8zHiNnv7QvAVTVXUtIPAECQGxH
QXqRLKVyj80ip14nFPe7UNY/CODMEXdaCYWhSVatEUeueG2fB3LWPuu2rmtUa0/O
6tH6Oqe/bWX8WnjVHPECPwTngCzFDW1YRcjs7X8mmXb2xfeU19EGQEsve/JtNz3o
++KGZ+eY2iMEzNLIxQkRq4mihiFAqhE+QekRzXlNyw==
-----END RSA PRIVATE KEY-----"""

# Função para codificar em Base64 URL Safe (sem "=" no final)
def base64url_encode(input_bytes):
    return base64.urlsafe_b64encode(input_bytes).rstrip(b'=')

# Cria o token JWT usando a chave privada hardcoded
def jwt_creator(expiration_minutes, cpf):
    # Cabeçalho do JWT
    header = {
        "alg": "RS256",  # Algoritmo de assinatura com chave privada
        "typ": "JWT"
    }
    
    # Payload do JWT
    payload = {
        'exp': (datetime.utcnow() + timedelta(minutes=expiration_minutes)).timestamp(),
        'cpf': cpf
    }

    # Codifica o cabeçalho e o payload em Base64 URL Safe
    encoded_header = base64url_encode(json.dumps(header).encode('utf-8'))
    encoded_payload = base64url_encode(json.dumps(payload).encode('utf-8'))

    # Concatena o cabeçalho e o payload com um ponto
    signing_input = encoded_header + b'.' + encoded_payload

    # Carrega a chave privada RSA
    private_key = rsa.PrivateKey.load_pkcs1(PRIVATE_KEY.encode('utf-8'))

    # Gera a assinatura do JWT usando SHA-256 e RSA
    signature = rsa.sign(signing_input, private_key, 'SHA-256')

    # Codifica a assinatura em Base64 URL Safe
    encoded_signature = base64url_encode(signature)

    # Concatena o token final: cabeçalho.payload.assinatura
    jwt_token = signing_input + b'.' + encoded_signature

    return jwt_token.decode('utf-8')

def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    
    try:
        if isinstance(event, str):
            data = json.loads(event)
        else:
            data = event
    except json.JSONDecodeError:
        raise Exception("400 body inválido")
    
    cpf = data.get('cpf')
    if not cpf:
        raise Exception('400 Campo "cpf" é obrigatório.')

    users = []
    
    list_users_params = {
        'UserPoolId': 'us-east-1_Q8ZsJSrsN'
    }
    filter_expression = f'username = "{cpf}"'
    list_users_params['Filter'] = filter_expression
    response = client.list_users(**list_users_params)
    
    users.extend(response.get('Users', []))
    
    if response['Users']:
        print("Usuário autenticado: " + cpf)
        # Gera e retorna o token JWT com chave privada hardcoded
        return jwt_creator(5, cpf)
    else:
        raise Exception("401 Usuário inválido")
