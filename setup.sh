#!/bin/bash
apt-get update
apt -y install python2.7 python-pip
pip2 install stomp.py awscli boto3
aws configure set aws_access_key_id AKIAI5FTY47RVDU737VA
aws configure set aws_secret_access_key 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
aws configure set default.region us-east-2

# tmp
aws ssm send-command --document-name "AWS-RunShellScript" --instance-ids "i-0358aea2ef64c716d" --parameters '{"commands":["python /home/ubuntu/hello.py"],"executionTimeout":["3600"]}' --timeout-seconds 600 --region us-east-2
scp -i ~/.ssh/aws_vm1.pem /home/ubuntu/launch.py ubuntu@13.58.62.215:/home/ubuntu


when calling the RunInstances operation: You are not authorized to perform this operation
