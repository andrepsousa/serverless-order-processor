# Serverless Order Processor

Microsserviço serverless construído na AWS para o processamento assíncrono de pedidos de compra. Desenvolvido como resolução de desafio técnico.

## 🏗️ Arquitetura e Decisões Técnicas

O sistema foi desenhado para ser resiliente, escalável e totalmente contido no **AWS Free Tier**.

A arquitetura escolhida utiliza **SQS (Simple Queue Service)** em vez de DynamoDB Streams para o processamento assíncrono.
* **Justificativa:** O SQS fornece um excelente desacoplamento entre a recepção do pedido (que precisa ser rápida) e o processamento de pagamento (que pode demorar ou sofrer instabilidades de integrações externas). Isso protege o banco de dados de sobrecargas e permite o controle de falhas de forma independente.
* **Trace:** O AWS X-Ray (Tracing) está ativado no API Gateway e nas Lambdas para monitoramento de performance e identificação de gargalos.

**Fluxo da Aplicação:**
1. **API Gateway:** Recebe o `POST /orders` e o `GET /orders/{order_id}`.
2. **Lambda (CreateOrder):** Valida o payload, salva o pedido no DynamoDB com status `PENDING` e publica uma mensagem no SQS.
3. **SQS:** Enfileira os eventos de novos pedidos.
4. **Lambda (ProcessPayment):** Consome a fila SQS, simula o tempo de processamento externo e atualiza o status no DynamoDB para `PROCESSED`.
5. **Lambda (GetOrder):** Permite a consulta do status atualizado do pedido diretamente no DynamoDB.

## 🚀 Tecnologias Utilizadas
* Python 3.9+ (boto3)
* Serverless Framework v3
* AWS Lambda
* Amazon API Gateway
* Amazon DynamoDB
* Amazon SQS
* Pytest (Testes Unitários)

## 💻 Como rodar o projeto

### Pré-requisitos
* **Python 3.9+** e Pip
* **Node.js e NPM** (No Windows, pode ser instalado via terminal com: `winget install OpenJS.NodeJS.LTS`)
* **Serverless Framework v3:** `npm install -g serverless@3`
* **Credenciais da AWS** configuradas localmente (`serverless config credentials --provider aws --key KEY --secret SECRET`)

### Instalação e Deploy
1. Clone o repositório:
   ```bash
   git clone https://github.com/andrepsousa/serverless-order-processor.git
   cd serverless-order-processor
   ```
2. Crie e ative o ambiente virtual:
   * **Linux/macOS:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   * **Windows (PowerShell/CMD):**
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   * **Windows (Git Bash):**
     ```bash
     source venv/Scripts/activate
     ```
3. Instale as dependências do Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Faça o deploy na AWS:
   ```bash
   serverless deploy
   ```

## 🧪 Como testar a API

⚠️ **Aviso para usuários Windows:** Recomendamos executar os comandos cURL abaixo utilizando o **Git Bash** para evitar problemas nativos de formatação de aspas do PowerShell.

**1. Criar um Pedido (POST):**
Utilize o comando cURL abaixo (substitua a URL pela gerada no seu deploy):
```bash
curl -X POST https://SUA-URL-AQUI.execute-api.us-east-1.amazonaws.com/dev/orders \
-H "Content-Type: application/json" \
-d '{"product": "Logitech MX Keys S", "price": 650.00}'
```
*(Anote o `order_id` retornado na resposta)*

**2. Consultar o Pedido (GET):**
```bash
curl https://SUA-URL-AQUI.execute-api.us-east-1.amazonaws.com/dev/orders/COLE-O-ID-AQUI
```

## 🛠️ Testes Unitários
Para rodar a suíte de testes localmente com objetos Mock (sem consumir recursos da AWS):
```bash
pytest tests/
```

## 🧹 Limpeza de Recursos
Para garantir que não haja cobranças na conta AWS após os testes, destrua a stack provisionada executando:
```bash
serverless remove
```
Isso deletará as funções Lambda, Tabela do DynamoDB, Fila SQS e o API Gateway.