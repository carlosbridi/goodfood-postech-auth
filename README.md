# AWS goodfood-postech-auth

Este repositório contém os fontes de autenticação do projeto GoodFood.

## Pré-requisitos

- Python 3
- Zip

## Funções

### generate-token (Autenticação | Login)

1. `cd generate-token`
2. `pip install rsa -t .`
3. `zip -r9 lambda_function.zip .`
4. Fazer Upload do ZIP no Console do Lambda.


### lambda-authorizer (Autenticação | Validação do token)

1. `cd lambda-authorizer`
2. `pip install rsa -t .`
3. `zip -r9 lambda_function.zip .`
4. Fazer Upload do ZIP no Console do Lambda.


### cadastroUsuario (Cadastrar um cliente)

1. `cd cadastroUsuario`
2. `zip -r9 lambda_function.zip .`
3. Fazer Upload do ZIP no Console do Lambda.


### find-by-cpf (Buscar cadastro de cliente pelo CPF)

1. `cd find-by-cpf`
2. `zip -r9 lambda_function.zip .`
3. Fazer Upload do ZIP no Console do Lambda.
