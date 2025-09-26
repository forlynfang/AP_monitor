#!usr/bin/python3

"""
This script is to check the AP status and send related alert to Teams channel in case any AP is lost from WLC.
"""
import sys
import json
import requests
from ftplib import FTP
from urllib3.exceptions import InsecureRequestWarning
import os
from colorama import init, Fore, Style
from dotenv import load_dotenv
init(autoreset=True) 
from netmiko import ConnectHandler


#os.chdir('C:/Users/ffang/Downloads/python')
#current_dir = os.getcwd()
#print(f"current work directory：{current_dir}")

#load_dotenv(dotenv_path=".env")
cisco_username = os.environ.get('CISCO_USERNAME')
cisco_password = os.environ.get('CISCO_PASSWORD')           
ftp_username = os.environ.get('FTP_USERNAME')
ftp_password = os.environ.get('FTP_PASSWORD') 
teams_webhook_url = os.environ.get('TEAMS_WEBHOOK')

# 定义设备连接参数
cisco_device = [
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'cnchen02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'conn_timeout': 45,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'sgsing01wc01',
        'username': cisco_username,
        'password': cisco_password,
       'conn_timeout': 45,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'jptkyo01wc01',
        'username': cisco_username,
        'password': cisco_password,
        'conn_timeout': 45,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'inhdrb02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'conn_timeout': 45,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'cnzyng02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'conn_timeout': 45,
        'port': 22,  # 默认SSH端口
    }
]

# 建立连接并执行命令
for device in cisco_device:
        host = device['host']
        
        try:
            with ConnectHandler(**device) as conn:
                text = conn.send_command('sh logging | in AP Event')  # 执行单条命令
                #print(text)
                        
                # 执行多条配置命令
                #config_commands = ['interface GigabitEthernet0/1', 'description Python-configured']
                #output = conn.send_config_set(config_commands)
                #print(output)
                
        except Exception as e:
            print(f"连接失败: {str(e)}")
            sys.exit(1)

        target = "Registered"

        target_RCV = " Joined"

        # 覆盖写入模式（文件存在则清空后保存）
        with open("output_AP.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
            f.write(text)

        def read_ftp_file(hostip, username, password, remote_path):
            """读取FTP服务器上的文本文件"""
            try:
                with FTP(hostip) as ftp:
                    ftp.login(user=username, passwd=password)
                    
                    # 创建临时文件
                    temp_file = 'temp_ftp_download_AP.txt'
                    
                    with open(temp_file, 'wb') as f:
                        ftp.retrbinary(f'RETR {remote_path}', f.write)
                    
                    # 读取文件内容
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 删除临时文件
                    os.remove(temp_file)
                    
                    return content
            except Exception as e:
                print(f"读取文件失败: {str(e)}")
                return None
        
        # 使用示例
        content = read_ftp_file('10.133.10.115', 'apacftp', 'P@ssw0rd', f'/python/{host}output_previous_AP_NEW.txt')
        #if content:
            #print("文件内容:", content)
        with open("output_previous_AP_NEW.txt", "w", encoding="utf-8") as f2:  # 推荐指定编码
            f2.write(content)
        # find lost AP============================================================================
        with open("output_AP.txt", 'r') as f11:
            found = False
            for line_num, line in enumerate(f11, 1):
                if target in line:
                    highlighted = line.replace(target, f"{Fore.RED}{target}{Style.RESET_ALL}")
                    
                    with open("output_AP.txt", 'r') as fc, open("output_previous_AP_NEW.txt", 'r', encoding='utf-8') as fp:    
                        lines_c = [line.rstrip('\n') for line in fc.readlines()]
                        lines_p = [line.rstrip('\n') for line in fp.readlines()]
                        lines_cc = line.rstrip('\n')
                        line_count_c = len(lines_c)
                        line_count_p = len(lines_p)
                        #print(f"line1={line_count_c} and line2={line_count_p}")
                        #print(f"{lines_pp}")
                        #print(f"{lines_c}")
                        if lines_cc not in lines_p :                                                                                     
                            print(f"One AP is lost on {host} : {highlighted.strip()}")
                            found = True
                            message = {
                            "text": f"WARNING: One AP is lost on {host} , related log is: {highlighted.strip()}. "
                            }
                            try:
                                teams_response = requests.post(
                                teams_webhook_url,
                                json=message,
                                headers={"Content-Type": "application/json"}
                            )
                                teams_response.raise_for_status()
                            except Exception as e:
                                print(f"Failed to send alert to MS Teams for {host}")       
                                
            if not found:
                print(f"All {line_count_c} APs are good on {host} ")  # :ml-citation{ref="3,7" data="citationList"}
                
        # find recovered AP============================================================================
        with open("output_AP.txt", 'r') as f11:
            found = False
            for line_num, line in enumerate(f11, 1):
                if target_RCV in line:
                    highlighted = line.replace(target, f"{Fore.RED}{target}{Style.RESET_ALL}")
                    
                    with open("output_AP.txt", 'r') as fc, open("output_previous_AP_NEW.txt", 'r', encoding='utf-8') as fp:    
                        lines_c = [line.rstrip('\n') for line in fc.readlines()]
                        lines_p = [line.rstrip('\n') for line in fp.readlines()]
                        lines_cc = line.rstrip('\n')
                        line_count_c = len(lines_c)
                        line_count_p = len(lines_p)
                        #print(f"line1={line_count_c} and line2={line_count_p}")
                        #print(f"{lines_pp}")
                        #print(f"{lines_c}")
                        if lines_cc not in lines_p :                                                                                     
                            print(f"One AP is back on {host} : {highlighted.strip()}")
                            found = True
                            message = {
                            "text": f"WARNING: One AP is recovered on {host} , related log is: {highlighted.strip()}. "
                            }
                            try:
                                teams_response = requests.post(
                                teams_webhook_url,
                                json=message,
                                headers={"Content-Type": "application/json"}
                            )
                                teams_response.raise_for_status()
                            except Exception as e:
                                print(f"Failed to send alert to MS Teams for {host}")    
    
        def upload_text_file(host, username, password, local_path, remote_path):
            """上传文本文件到FTP服务器"""
            try:
                with FTP(host) as ftp:
                    ftp.login(user=username, passwd=password)
                    
                    with open(local_path, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_path}', f)
                    
                    print(f"文件 {local_path} 已上传到 {remote_path}")
                    return True
            except Exception as e:
                print(f"上传文件失败: {str(e)}")
                return False

        # 使用示例
        with open(f"{host}output_previous_AP.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
            f.write(text)
        upload_text_file('10.133.10.115', ftp_username, ftp_password, f'{host}output_previous_AP.txt', f'/python/{host}output_previous_AP.txt')
