"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt de baixa qualidade do LangSmith Hub
    e salva localmente em YAML.

    Returns:
        dict com dados do prompt ou None se falhar
    """
    prompt_name = "leonanluppi/bug_to_user_story_v1"

    print(f"📥 Fazendo pull do prompt: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso do Hub")

        # Extrair informações do prompt
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": "",
                "user_prompt": "",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        # Extrair mensagens do ChatPromptTemplate
        if hasattr(prompt, 'messages'):
            for msg in prompt.messages:
                msg_type = msg.__class__.__name__
                # Extrair o template string
                template = ""
                if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                    template = msg.prompt.template
                elif hasattr(msg, 'content'):
                    template = msg.content

                if 'System' in msg_type:
                    prompt_data["bug_to_user_story_v1"]["system_prompt"] = template
                elif 'Human' in msg_type:
                    prompt_data["bug_to_user_story_v1"]["user_prompt"] = template

        return prompt_data, prompt

    except Exception as e:
        print(f"   ❌ Erro ao fazer pull: {e}")
        print(f"\n   Verifique:")
        print(f"   - LANGSMITH_API_KEY está configurada no .env")
        print(f"   - O prompt '{prompt_name}' existe no Hub")
        return None, None


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    # Fazer pull
    prompt_data, prompt_obj = pull_prompts_from_langsmith()

    if prompt_data is None:
        print("\n❌ Falha ao fazer pull dos prompts.")
        return 1

    # Salvar localmente
    output_path = "prompts/bug_to_user_story_v1.yml"
    if save_yaml(prompt_data, output_path):
        print(f"\n✅ Prompt salvo em: {output_path}")
    else:
        print(f"\n❌ Erro ao salvar prompt em: {output_path}")
        return 1

    # Salvar também em raw_prompts.yml
    raw_path = "prompts/raw_prompts.yml"
    if save_yaml(prompt_data, raw_path):
        print(f"✅ Cópia salva em: {raw_path}")

    print("\n📋 Próximos passos:")
    print("1. Analise o prompt em prompts/bug_to_user_story_v1.yml")
    print("2. Crie o prompt otimizado em prompts/bug_to_user_story_v2.yml")
    print("3. Faça push: python src/push_prompts.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
