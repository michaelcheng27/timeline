import boto3


class DynamoDB:
    def __init__(self, table_name):
        self._dynamodb = boto3.resource('dynamodb').Table(table_name)
        self._hash_key_name = None

    def get_hash_key_name(self):
        if not self._hash_key_name:
            hash_key_schema = next(
                k for k in self._dynamodb.key_schema if k.get("KeyType") == "HASH")
            self._hash_key_name = hash_key_schema.get("AttributeName")

        return self._hash_key_name

    def put_item(self, item, not_override_exist_item=True):
        conditional_expression = f"attribute_not_exists({self.get_hash_key_name()})" if not_override_exist_item else ""
        self._dynamodb.put_item(
            Item=item,
            ConditionExpression=conditional_expression
        )
