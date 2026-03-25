import json
import os
import time
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('ORDERS_TABLE')

def handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            order_id = body.get('order_id')
            if not order_id:
                print("Mensagem ignorada: order_id não encontrado.")
                continue

            print(f"Inicianddo processamento do pedido: {order_id}")

            time.sleep(2)

            table.update_item(
                Key={'order_id': order_id},
                UpdateExpression="SET #status_alias = :new_status",
                ExpressionAttributeNames={'#status_alias': 'status'},
                ExpressionAttributeValues={':new_status': 'PROCESSED'}
            )

            print(f"Pedido {order_id} processado e atualizado com sucesso!")

        except Exception as e:
            print(f"Erro ao processar a mensagem do SQS: {e}")
            raise e
        
    return {
        'statusCode': 200,
        'body': "Lote processado"
        }
