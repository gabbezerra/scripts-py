import string
import requests
import json
import OpenSSL
import datetime

url_project = "url_do_stash/projects?limit=1000"

# Hearder com token para autenticar no stash
headers = {
   "Accept": "application/json",
   "Authorization": "Bearer token_de_autenticacao"
}

# CONECTANDO E RECEBENDO O JSON


def get_connection(url: string):
    response = requests.request(
        "GET",
        url,
        headers=headers
    )
    items_json = json.dumps(json.loads(response.text),
                            sort_keys=True, indent=4, separators=(",", ": "))
    items_dict = json.loads(items_json)
    return items_dict

# LISTANDO OS PROJETOS
def get_projects(project_url: string):
    list_projects = []
    items_dict = get_connection(project_url)["values"]
    for x in range(0, len(items_dict)):
        list_projects.append(items_dict[x]['key'])
    return list_projects

# LISTANDO OS REPOSITORIOS DENTRO DOS PROJETOS
def get_repository(url_project: string):
    repository_list = []
    repo_dict = get_connection(url_project)["values"]
    for repo in range(0, len(repo_dict)):
        repository_list.append(repo_dict[repo]['name'])
    return repository_list

# LISTANDO TODAS AS URLS
def get_all_urls():
    proj_list = get_projects(url_project)
    all_urls = []
    for proj in proj_list:
        url_projeto = f"url_do_stash/projects/{proj}/repos?limit=1000"
        projeto = proj
        proj = get_repository(url_projeto)
        for repo in proj:
            all_urls.append(f"url_do_stash/projects/{projeto}/repos/{repo}/raw/src/main/resources/application.yml")
            all_urls.append(f"url_do_stash/projects/{projeto}/repos/{repo}/raw/src/main/resources/application-prod.yml")
    return all_urls

# CRIANDO UMA LISTA DE PROJETOS QUE TEM OS ARQUIVOS
def get_files():
   repo_files = get_all_urls()
   for url_file in repo_files:
      response = requests.request("GET",url_file,headers=headers)
      file_byte = response.content
      file_string = file_byte.decode("utf-8")
      find_param = file_string.find("clmon:9001")
      if find_param > 0:
          print (f"O Repo {url_file} possui o arquivo com o apontamento para o [clmon:9001]")
      else:
          print(f"Repositorio {url_file} sem clm")      

# Chamando funcao
get_files()

