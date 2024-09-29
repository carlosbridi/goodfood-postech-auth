import json
import base64
import rsa

def base64url_decode(input):
    # Adiciona o padding se necessário
    padding = '=' * (4 - len(input) % 4) if len(input) % 4 != 0 else ''
    input += padding
    return base64.b64decode(input.replace('-', '+').replace('_', '/'))

def decode_jwt(token):
    # Divide o token em partes
    parts = token.split('.')
    
    if len(parts) != 3:
        raise ValueError("Token JWT deve ter 3 partes.")

    # Decodifica o cabeçalho e o payload
    header = json.loads(base64url_decode(parts[0]).decode('utf-8'))
    payload = json.loads(base64url_decode(parts[1]).decode('utf-8'))

    return header, payload, parts

def verify_signature(token, public_key):
    # Divide o token em partes
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Token JWT deve ter 3 partes.")
    
    # Calcula a assinatura e os dados que devem ser verificados
    signing_input = f"{parts[0]}.{parts[1]}".encode('utf-8')
    signature = base64url_decode(parts[2])

    # Verifica a assinatura usando a chave pública
    return rsa.verify(signing_input, signature, public_key)
    
def is_token_expired(payload):
    # Verifica a expiração do token
    if 'exp' in payload:
        # O valor de 'exp' deve ser um timestamp em segundos
        return payload['exp'] < time.time()  # Verifica se o token já expirou
    return True  # Se 'exp' não está presente, consideramos que o token é inválido

def lambda_handler(event, context):
    effect = 'Deny'
    
    headers = event['headers']
    authorization = headers['Authorization']

    public_key_pem = """
-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAMYOdHoJbVbVVCpcUAqbUdlymejlDNGgesN8pslralgG6cBphLUC8+hQ
SHtkIBxDFjWCV5A752cusN2hKPZTWeOIGXg5XZXB7ahlelyzysWDRovp/vZytVWv
nSJjtKh0KLH5//m2ZKD4ruDU6Wu93J3JGLWzW5p+7Ba4FrrpJS5JAgMBAAE=
-----END RSA PUBLIC KEY-----
"""
    public_key = rsa.PublicKey.load_pkcs1(public_key_pem.encode('utf-8'))

    try:
        # Decodifica o JWT e verifica a assinatura
        header, payload, parts = decode_jwt(authorization)
        
        if verify_signature(authorization, public_key):
            effect = 'Allow'
            
        if is_token_expired(payload):
            print("Token expirado.")
            effect = 'Deny'
    except Exception as e:
        print(f"Erro ao validar o token: {e}")

    response = {
        "principalId": 'user',
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": event['methodArn']
            }]
        }
    }
    return response
