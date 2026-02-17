"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: "bug_to_user_story_v2")
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        username = os.getenv("USERNAME_LANGSMITH_HUB", "")
        if not username:
            print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
            return False

        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        # Criar ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        # Nome completo no Hub
        full_name = f"{username}/{prompt_name}"

        print(f"📤 Fazendo push do prompt: {full_name}")
        print(f"   Descrição: {prompt_data.get('description', 'N/A')}")
        print(f"   Versão: {prompt_data.get('version', 'N/A')}")
        print(f"   Tags: {prompt_data.get('tags', [])}")
        print(f"   Técnicas: {len(prompt_data.get('techniques_applied', []))} técnicas aplicadas")

        # Push para o LangSmith Hub (público)
        hub.push(
            full_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", "Prompt otimizado para Bug to User Story"),
            tags=prompt_data.get("tags", []),
        )

        print(f"   ✓ Push realizado com sucesso!")
        print(f"   🔗 Acesse em: https://smith.langchain.com/hub/{full_name}")
        return True

    except Exception as e:
        print(f"   ❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    # Campos obrigatórios
    required_fields = ['description', 'system_prompt', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    # Verificar se system_prompt não está vazio
    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    # Verificar TODOs remanescentes
    if 'TODO' in system_prompt or '[TODO]' in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    # Verificar técnicas aplicadas (mínimo 2)
    techniques = prompt_data.get('techniques_applied', [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    # Verificar se user_prompt existe
    user_prompt = prompt_data.get('user_prompt', '').strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    # Carregar prompt otimizado
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    print(f"📂 Carregando prompt de: {yaml_path}")

    data = load_yaml(yaml_path)
    if data is None:
        print(f"\n❌ Falha ao carregar {yaml_path}")
        return 1

    # Extrair dados do prompt
    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)

    if prompt_data is None:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        return 1

    # Validar prompt
    print("\n🔍 Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print("   ✓ Prompt válido!")

    # Fazer push
    print()
    success = push_prompt_to_langsmith(prompt_key, prompt_data)

    if success:
        print("\n✅ Push concluído com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Verifique o prompt no LangSmith Hub")
        print("2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        print("\n❌ Falha no push do prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
