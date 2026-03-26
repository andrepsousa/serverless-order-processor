import json
import os
import boto3
from decimal import Decimal
from aws_xray_sdk.core import patch_all


patch_all()
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('ORDERS_TABLE', 'OrdersTable-dev')
table = dynamodb.Table(table_name)


def handler(event, context):
    try:
        order_id = event['pathParameters']['order_id']

        response = table.get_item(Key={'order_id': order_id})

        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Pedido não encontrado."})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(response['Item'], cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Erro ao buscar pedido: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Erro interno do servidor."})
        }
