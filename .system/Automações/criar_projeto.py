import os
import json
import sys
import re

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def update_json_config(config_path, company, department, project):
    if not os.path.exists(config_path):
        data = {"empresas": {}}
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                data = {"empresas": {}}
    
    if "empresas" not in data:
        data["empresas"] = {}
        
    if company not in data["empresas"]:
        data["empresas"][company] = {"departamentos": {}}
        
    if "departamentos" not in data["empresas"][company]:
        data["empresas"][company]["departamentos"] = {}
        
    if department not in data["empresas"][company]["departamentos"]:
        data["empresas"][company]["departamentos"][department] = {"projetos": []}
        
    if "projetos" not in data["empresas"][company]["departamentos"][department]:
        data["empresas"][company]["departamentos"][department]["projetos"] = []
        
    projects = data["empresas"][company]["departamentos"][department]["projetos"]
    if project not in projects:
        projects.append(project)
        
    if "Geral" not in projects:
        projects.append("Geral")
        
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Configurações JSON atualizadas com sucesso em {config_path}")

def create_file_if_not_exists(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[NEW] Arquivo criado: {path}")
    else:
        print(f"[INFO] Arquivo ja existe: {path}")

def main():
    base_dir = r"c:\principe"
    config_path = os.path.join(base_dir, ".system", ".config", "empresas_config.json")
    
    company = sys.argv[1] if len(sys.argv) > 1 else "Pessoal"
    department = sys.argv[2] if len(sys.argv) > 2 else "Analise Pessoa"
    project = sys.argv[3] if len(sys.argv) > 3 else "Sistema de iA"
    
    # Normalização automática para evitar duplicar 'ViniciusPessoal' e usar sempre 'Vinicius'
    if company.lower() == "viniciuspessoal":
        company = "Vinicius"
        
    print(f"[START] Iniciando criacao do projeto para {company} -> {department} -> {project}...")
    
    # 1. Atualizar JSON
    update_json_config(config_path, company, department, project)
    
    # Caminhos de Pastas
    company_path = os.path.join(base_dir, "ArquivoProcessados", "Empresas", clean_filename(company))
    dept_path = os.path.join(company_path, clean_filename(department))
    project_path = os.path.join(dept_path, clean_filename(project))
    # Criar apenas o diretório do projeto
    os.makedirs(project_path, exist_ok=True)

    # 3. Criar a estrutura do Projeto dentro da pasta do Projeto
    # Diretórios de Transcrição e Análise
    transcricao_path = os.path.join(project_path, "4 - Transcrições")
    analise_path = os.path.join(project_path, "5 - Analise")
    
    os.makedirs(transcricao_path, exist_ok=True)
    os.makedirs(analise_path, exist_ok=True)
    print(f"[NEW] Pasta de Transcricao criada: {transcricao_path}")
    print(f"[NEW] Pasta de Analise criada: {analise_path}")
    
    # 1 - Diretrizes.md
    diretrizes_content = f"""---
tags:
  - projeto/diretrizes
  - {clean_filename(company).lower()}
  - {clean_filename(department).lower().replace(" ", "-")}
projeto: {project}
---

# 🎯 1 - Diretrizes: {project}

> **Diretrizes e escopo estratégico do projeto.**

## 📌 Objetivos
- Configuração e metas primárias de {project}.
- Definição de entregáveis e critérios de sucesso.

## 🏢 Informações da Empresa
- **Nome/Razão Social:** 
- **CNPJ/Identificação:** 
- **Setor/Nicho:** 

## 👥 Informação dos Responsáveis
- **Líder do Projeto:** 
- **Stakeholders Principais:** 
- **Contatos Úteis:** 

## 🔐 Arquivos e Senhas de Projetos
- **Repositórios/Diretórios:** 
- **Credenciais de Acesso (Seguras):** 
- **Links Importantes:** 
"""
    
    # 2 - Documentação.md
    documentacao_content = f"""---
tags:
  - projeto/documentacao
  - {clean_filename(company).lower()}
projeto: {project}
---

# 📖 2 - Documentação: {project}

> **Documentação técnica, conceitual e referências de apoio.**

## 📌 Arquitetura e Modelagem
- Detalhes de infraestrutura e funcionamento do sistema.
"""
    
    # 3 - Tarefas.md
    tarefas_content = f"""---
tags:
  - projeto/tarefas
  - {clean_filename(company).lower()}
projeto: {project}
---

# 📋 3 - Tarefas: {project}

## 🚀 Backlog do Projeto
- [ ] Definição e estruturação inicial
- [ ] Coleta de transcrições e atas
- [ ] Análises de requisitos e modelagem
"""
    
    create_file_if_not_exists(os.path.join(project_path, "1 - Diretrizes.md"), diretrizes_content)
    create_file_if_not_exists(os.path.join(project_path, "2 - Documentação.md"), documentacao_content)
    create_file_if_not_exists(os.path.join(project_path, "3 - Tarefas.md"), tarefas_content)
    
    print("[SUCCESS] Todo o ecossistema padrao de pastas e arquivos foi gerado com sucesso!")

if __name__ == "__main__":
    main()
