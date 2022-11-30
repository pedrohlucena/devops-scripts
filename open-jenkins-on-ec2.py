import json
import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv()) 

PROTOCOL = os.getenv('PROTOCOL')
PORT = int(os.getenv('PORT'))
REQUESTER = os.getenv('REQUESTER')
TARGET_SG = os.getenv('TARGET_SG')
REGION = os.getenv('REGION')
PROFILE = os.getenv('PROFILE')
INSTANCE_ID = os.getenv('INSTANCE_ID')
JENKINS_USERNAME = os.getenv('JENKINS_USERNAME')
JENKINS_PASSWORD = os.getenv('JENKINS_PASSWORD')

def revokeSecurityGroupIngress():
    process = subprocess.Popen(['aws', 'ec2', 'describe-security-groups', '--region', REGION,'--profile', PROFILE, '--group-ids', TARGET_SG, '--query', "SecurityGroups[*].{Name:GroupName,ID:GroupId,Permissions:IpPermissions}"], stdout=subprocess.PIPE)
    security_group_data = json.loads(process.communicate()[0])

    security_group_data_dictionary = security_group_data
    security_group_permissions = security_group_data_dictionary[0]['Permissions']
    security_group_protocols_dictionary = [x for x in security_group_permissions if x['IpProtocol'] == PROTOCOL]
    security_group_ports_dictionary = [x for x in security_group_protocols_dictionary if x['FromPort'] == PORT]
    security_group_ips = security_group_ports_dictionary[0]['IpRanges']
    old_ip = ([x for x in security_group_ips if x['Description'] == REQUESTER])[0]['CidrIp']

    os.system(f"aws ec2 revoke-security-group-ingress --region {REGION} --profile {PROFILE} --group-id {TARGET_SG} --protocol {PROTOCOL} --port {PORT} --cidr {old_ip}")

def authorizeSecurityGroupIngress(new_ip):
    params = [
        {
            "FromPort": PORT,
            "ToPort": PORT,
            "IpProtocol": PROTOCOL,
            "IpRanges": [
                {
                    "CidrIp": f"{new_ip}/32",
                    "Description": REQUESTER
                }
            ],
        }
    ]

    push = subprocess.call(['aws', 'ec2', 'authorize-security-group-ingress', '--region', REGION,'--profile', PROFILE, '--group-id', TARGET_SG, '--ip-permissions', f'{json.dumps(params)}'])

def changeIpInSecurityGroup(new_ip):
    revokeSecurityGroupIngress()
    authorizeSecurityGroupIngress(new_ip)

def configureWebDriver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)
    
def openJenkinsInBrowser(jenkins_url):
    driver = configureWebDriver()
    
    driver.get(f'{jenkins_url}')

    username_html_field = driver.find_element(By.NAME, "j_username")
    username_html_field.send_keys(JENKINS_USERNAME)

    password_html_field = driver.find_element(By.NAME,"j_password")
    password_html_field.send_keys(JENKINS_PASSWORD)

    driver.find_element(By.NAME,"Submit").click()
    

def getPublicIpv4DNS():
    aws_return = os.popen(f'aws ec2 describe-instance-status --region {REGION} --profile {PROFILE} --instance-ids {INSTANCE_ID}').read()
    ec2_instance_status = json.loads(aws_return)

    if len(ec2_instance_status['InstanceStatuses']) > 0:
        hasDns = False
        while hasDns == False:
            instance_data = os.popen(f'aws ec2 describe-instances --region {REGION} --profile {PROFILE} --instance-ids {INSTANCE_ID}').read()
            print(instance_data)
            instance_data = json.loads(instance_data)
            dns = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName']
            if dns:
                hasDns = True
                return dns
            time.sleep(3)
    else:
        print('Aparentemente a máquina está desligada.')

def getMyIp():
    return os.popen('curl ifconfig.me').read().strip()

def getJenkinsUrl(dns):
    return f'http://{dns}:3000/login?from=%2F'

def main():
    ip = getMyIp()
    changeIpInSecurityGroup(ip)
    dns = getPublicIpv4DNS()
    jenkins_url = getJenkinsUrl(dns)
    openJenkinsInBrowser(jenkins_url)
try:
    main()
except Exception as e:
    print(f'[ERRO] {str(e)}')
    raise Exception(e)