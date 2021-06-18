import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('tag')

tags = {
    '2171081757193': 'joao',
    '2491142008522': 'felipe',
}

for Id, User in tags.items():
    table.put_item(
        Item={
            'id': Id,
            'user': User
        }
    )
    print(Id, ': ', User)
