import boto3
import json
from botocore.exceptions import ClientError


client = boto3.client('cognito-idp')

def lambda_handler(event, context):

    try:
        if isinstance(event, str):
            data = json.loads(event)
        else:
            data = event
    except json.JSONDecodeError:
        raise Exception("400 body inválido")
    
    nome = data.get('nome')
    cpf = data.get('cpf')
    if not nome or not cpf:
        raise Exception('400 Campos "nome" e "cpf" são obrigatórios.')
        
    user_pool_id = 'us-east-1_Q8ZsJSrsN'
        
    # Cria o usuário no Cognito
    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=cpf,
            UserAttributes=[
                {'Name': 'name', 'Value': nome}
            ],
            TemporaryPassword=cpf,
            MessageAction='SUPPRESS'  # Define para 'SUPPRESS' se você não quer que o Cognito envie o e-mail de convite
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'UsernameExistsException':
            raise Exception('400 Usuário já existe.')
        else:
            raise Exception('500') from e
    
    # Define a senha permanentemente se fornecida
    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=cpf,
        Password=cpf,
        Permanent=True
    )
    
    return json.dumps({
            'id': cpf,
            'nome': nome,
            'cpf': cpf
    })
