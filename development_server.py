#!/usr/bin/env python
import os
import boto3
import subprocess
import urllib

def get_role_credentials():
  os.environ["AWS_PROFILE"] = "cdo"
  sts = boto3.client('sts')
  return sts.assume_role(
    RoleArn='arn:aws:iam::475661607190:role/admin/Developer',
    RoleSessionName='role',
  )

def set_keys_for_child_process(aws_role):
  os.environ["AWS_ACCESS_KEY_ID"] = aws_role['Credentials']['AccessKeyId']
  os.environ["AWS_SECRET_ACCESS_KEY"] = aws_role['Credentials']['SecretAccessKey']
  os.environ["AWS_SESSION_TOKEN"] = aws_role['Credentials']['SessionToken']

def set_resources_for_child_process():
  os.environ['AWS_STORAGE_BUCKET_NAME'] = 'cdo-curriculum-devel'

set_keys_for_child_process(get_role_credentials())
set_resources_for_child_process()
subprocess.call(["python", "manage.py", "runserver_plus"])
