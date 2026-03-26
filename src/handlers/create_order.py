import json
import os
import uuid
import boto3
from datetime import datetime, timezone
from decimal import Decimal
from aws_xray_sdk.core import patch_all

patch_all()
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

TABLE_NAME = os.environ.get('ORDERS_TABLE')
QUEUE_URL = os.environ.get('QUEUE_URL')

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'), parse_float=Decimal)

        if 'product' not in body or 'price' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Campos obrigatórios ausentes: 'product' e 'price'."})
            }

        order_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        order_item = {
            'order_id': order_id,
            'product': body['product'],
            'price': body['price'],
            'status': 'PENDING',
            'created_at': timestamp
        }

        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=order_item)

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({'order_id': order_id})
        )

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': "Pedido criado com sucesso!",
                'order_id': order_id
            })
        }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Payload JSON inválido."})
        }
    except Exception as e:
        print(f"Erro interno ao criar pedido: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "Erro interno do servidor."})
        }
