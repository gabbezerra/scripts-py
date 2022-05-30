import string, requests, json, OpenSSL, datetime

url_project = "url_do_stash/projects?limit=1000"

#Hearder com token para autenticar no stash
headers = {
   "Accept": "application/json",
   "Authorization": "Bearer token_de_autenticacao"
}

# CONECTANDO E RECEBENDO O JSON
def get_connection(url:string):
    response = requests.request(
        "GET",
        url,
        headers=headers
    )
    items_json = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    items_dict = json.loads(items_json)
    return items_dict

# LISTANDO OS PROJETOS
def get_projects(project_url:string):
    list_projects = []
    items_dict = get_connection(project_url)["values"]
    for x in range (0 , len(items_dict)):
        list_projects.append(items_dict[x]['key'])
    return list_projects

# LISTANDO OS REPOSITORIOS DENTRO DOS PROJETOS
def get_repository(url_project:string):
    repository_list = []
    repo_dict = get_connection(url_project)["values"]
    for repo in range (0 , len(repo_dict)):
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
            all_urls.append(f"url_do_stash/projects/{projeto}/repos/{repo}/browse")
    return all_urls

# CRIANDO UMA LISTA DE PROJETOS QUE TEM CERTIFICADO
def get_certs():
    repo_list = get_all_urls()
    repo_with_certs = []
    repo_with_errors = []
    for repo in repo_list:
        repo_sem_browse = repo.replace("/browse","")
        try:
            items_certs = get_connection(repo) ["children"] ["values"]
            print('============================ Repo ============================')
            print(repo)
        except:
            repo_with_errors.append(repo)
        for cert in range (0 , len(items_certs)):
            try:
                extensoes = items_certs[cert]['path']['extension']
            except KeyError:
                error= items_certs[cert]['path']['name']
            else:
                if extensoes == "crt" or extensoes == "cert":
                    name_certs = items_certs[cert]['path']['name']
                    repo_with_certs.append(f"{repo_sem_browse}/raw/{name_certs}")
    print('============================ Repo com erros ============================')
    print(repo_with_errors)
    return repo_with_certs

# IDENTIFICANDO O TEMPO DE CADA CERTIFICADO
def date_certs(repo_certs):
   for url_certs in repo_certs:
      response = requests.request("GET",url_certs,headers=headers)
      certificado = response.content
      x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificado)
      expiry_date = datetime.datetime.strptime(x509.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%S%z')
      delta = expiry_date - datetime.datetime.now(datetime.timezone.utc)
      print ('============================ Certificado e data de expiracao ============================')
      print(f'Certificado do repo: {url_certs} expira em {delta.days} dia(s)')

# CHAMANDO FUNCAO
repositorio_certs = get_certs()
date_certs(repositorio_certs)
