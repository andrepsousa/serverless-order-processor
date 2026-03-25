import json
import os
import pytest
from unittest.mock import patch

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['ORDERS_TABLE'] = 'OrdersTable-dev'
os.environ['QUEUE_URL'] = 'http://localhost/queue'

from src.handlers.create_order import handler

@patch('src.handlers.create_order.dynamodb')
@patch('src.handlers.create_order.sqs')
def test_create_order_success(mock_sqs, mock_dynamodb):
    event = {
        'body': json.dumps({
            'product': 'Logitech MX Keys S',
            'price': 650.00
        })
    }

    response = handler(event, None)

    assert response['statusCode'] == 201

    body = json.loads(response['body'])
    assert body['message'] == "Pedido criado com sucesso!"
    assert 'order_id' in body

@patch('src.handlers.create_order.dynamodb')
@patch('src.handlers.create_order.sqs')
def test_create_order_missing_fields(mock_sqs, mock_dynamodb):
    event = {
        'body': json.dumps({
            'product': 'Mouse sem fio'
        })
    }

    response = handler(event, None)

    assert response['statusCode'] == 400

    body = json.loads(response['body'])
    assert 'Campos obrigatórios ausentes' in body['error']
    