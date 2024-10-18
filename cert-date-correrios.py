import ssl
import socket
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import requests

def create_servicenow_ticket():
    # Configuração dos parâmetros para o chamado
    url = 'https://apis.pontoslivelo.com.br/livelo-on-call/incident?source=rundeck&team=cloud_datacenter'
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'title': "Certificado do Barramento Diferente do dos Correios.",
        'description': f'Verificar troca na doc: https://livelo.atlassian.net/wiki/spaces/IC/blog/2023/09/16/380239954/Import+do+Certificado+Correios+no+Barramento',
        'service': "Backup", 
        'environment': "INFRA", 
        'state': "open", 
        'impact': "2",
        'urgency': "2", 
        'incident_id':""
    }

    # Faz a chamada HTTP para criar o chamado
    response = requests.post(url, headers=headers, json=payload)
    
    #Verifica se a chamada foi bem-sucedida
    if response.status_code == 200:
        print('Chamado criado com sucesso no ServiceNow.')
    else:
        print('Erro ao criar chamado no ServiceNow. Código de status:', response.status_code)

def check_ssl_certificate(hostname, port=443):
    try:
        # Cria um contexto SSL
        context = ssl.create_default_context()
        
        # Estabelece uma conexão segura com o site
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Obtém as informações do certificado
                cert = ssock.getpeercert()
                
                # Obtém a data de validade do certificado
                valid_from = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                valid_until = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                
                return valid_until

                # Verifica se o certificado está dentro do período de validade
                current_time = datetime.now()
                if valid_from <= current_time <= valid_until:
                    print(f"O certificado SSL para {hostname} está válido até: {valid_until}.")
                else:
                    print(f"O certificado SSL para {hostname} não está válido.")
                    print(f"Válido de: {valid_from} até: {valid_until}")
                    
    except Exception as e:
        print(f"Erro ao verificar o certificado SSL do site: {str(e)}")

def check_local_certificate(cert_file_path):
    try:
        # Lê o certificado local em formato PEM
        with open(cert_file_path, 'rb') as cert_file:
            cert_data = cert_file.read()

        # Carrega o certificado local
        local_certificate = x509.load_pem_x509_certificate(cert_data, default_backend())

        # Obtém a data de validade do certificado local
        valid_from = local_certificate.not_valid_before
        valid_until = local_certificate.not_valid_after
        return valid_until
        # Verifica se o certificado local está dentro do período de validade
        current_time = datetime.now()
        if valid_from <= current_time <= valid_until:
            print(f"O certificado local está válido até: {valid_until}.")
        else:
            print(f"O certificado local não está válido.")
            print(f"Válido de: {valid_from} até: {valid_until}")
    except Exception as e:
        print(f"Erro ao verificar o certificado local: {str(e)}")

def lambda_handler(event, context):
    try:
        # Verifica o certificado do site e obtém a data de validade
        site_url = "apps.correios.com.br" 
        site_valid_until = check_ssl_certificate(site_url)

        # Verifica o certificado local e obtém a data de validade
        local_cert_path = 'correios_2023_set.cer'
        local_valid_until = check_local_certificate(local_cert_path)

        # Compara as datas de validade
        if local_valid_until is not None and site_valid_until is not None:
            if local_valid_until != site_valid_until:
                print(f"O certificado local {local_valid_until} é diferente do certificado do site {site_valid_until}.")
                create_servicenow_ticket()
            else:
                print(f"As datas de validade dos certificados são iguais {local_valid_until} e {site_valid_until} .")
                #create_servicenow_ticket()
        else:
            print("Não foi possível obter as datas de validade dos certificados.")

    except Exception as e:
        print(f"Erro ao comparar as datas de validade dos certificados: {str(e)}")

lambda_handler({},{})

