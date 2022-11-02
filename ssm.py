import boto3

ssm_client = boto3.client('ssm')
response = ssm_client.send_command(
    InstanceIds=['i-0358aea2ef64c716d'],
    DocumentName='AWS-RunShellScript',
    Parameters={
        'commands':[
            'ifconfig',
            'ps',
            'ls /home/ubuntu -a'
        ]
    }
)
