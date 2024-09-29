import boto3
import json


def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    
    print(event)
    print(context)
    
    if event.get('pathParameters'):
        cpf = event['pathParameters'].get('cpf', None)
    
    if not cpf:
        raise Exception('400 "{cpf}" é obrigatório.')

    users = []
    
    list_users_params = {
        'UserPoolId': 'us-east-1_Q8ZsJSrsN'
    }
    filter_expression = f'username = "{cpf}"'
    list_users_params['Filter'] = filter_expression
    response = client.list_users(**list_users_params)
    
    users.extend(response.get('Users', []))
    
    if response['Users']:
        print("Usuário encontrado")
        return {
            "statusCode": 200,
            "body": json.dumps({
                'id': cpf,
                'nome': next((item['Value'] for item in response['Users'][0]['Attributes'] if item['Name'] == 'name'), None),
                'cpf': cpf
            })
        }
    else:
        raise Exception("401 Usuário não encontrado")