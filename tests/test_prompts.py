"""
Testes automatizados para validação de prompts.

Verifica se o prompt otimizado (v2) segue todas as boas práticas
e requisitos de qualidade definidos no desafio.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    """Fixture que carrega os dados do prompt v2."""
    data = load_prompts(PROMPT_V2_PATH)
    return data["bug_to_user_story_v2"]


@pytest.fixture
def system_prompt_text(prompt_data):
    """Fixture que retorna o texto do system_prompt."""
    return prompt_data.get("system_prompt", "")


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no prompt"
        system_prompt = prompt_data["system_prompt"]
        assert system_prompt is not None, "system_prompt é None"
        assert isinstance(system_prompt, str), "system_prompt deve ser uma string"
        assert len(system_prompt.strip()) > 0, "system_prompt está vazio"

    def test_prompt_has_role_definition(self, system_prompt_text):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        text_lower = system_prompt_text.lower()
        role_keywords = [
            "você é",
            "voce é",
            "you are",
            "atue como",
            "seu papel",
            "sua função",
            "product manager",
            "persona",
        ]
        has_role = any(keyword in text_lower for keyword in role_keywords)
        assert has_role, (
            "O prompt não define uma persona/role. "
            "Deve conter algo como 'Você é um Product Manager' ou similar."
        )

    def test_prompt_mentions_format(self, system_prompt_text):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text_lower = system_prompt_text.lower()
        format_keywords = [
            "markdown",
            "user story",
            "como um",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "criterios de aceitacao",
            "given-when-then",
            "dado-quando-então",
            "dado que",
            "formato",
        ]
        has_format = any(keyword in text_lower for keyword in format_keywords)
        assert has_format, (
            "O prompt não menciona formato Markdown ou User Story padrão. "
            "Deve exigir um formato de saída estruturado."
        )

    def test_prompt_has_few_shot_examples(self, system_prompt_text):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text_lower = system_prompt_text.lower()
        # Verificar presença de exemplos
        example_keywords = [
            "exemplo",
            "example",
            "bug report",
            "user story esperada",
            "entrada/saída",
            "few-shot",
        ]
        has_examples = any(keyword in text_lower for keyword in example_keywords)
        assert has_examples, (
            "O prompt não contém exemplos de entrada/saída (Few-shot). "
            "Deve incluir pelo menos 2 exemplos claros."
        )

        # Verificar que há pelo menos 2 exemplos
        example_count = text_lower.count("exemplo")
        assert example_count >= 2, (
            f"Encontrado(s) {example_count} exemplo(s), mínimo de 2 exemplos é necessário."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        # Verificar todos os campos de texto do prompt
        fields_to_check = ["system_prompt", "user_prompt", "description"]

        for field in fields_to_check:
            content = prompt_data.get(field, "")
            if content:
                assert "[TODO]" not in content, (
                    f"Encontrado [TODO] no campo '{field}'. "
                    "Remova todos os TODOs antes de finalizar."
                )
                assert "TODO" not in content.upper().split(), (
                    f"Encontrado TODO no campo '{field}'. "
                    "Remova todos os TODOs antes de finalizar."
                )

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}. "
            "Adicione as técnicas aplicadas no campo 'techniques_applied' do YAML."
        )

    def test_prompt_has_user_prompt(self, prompt_data):
        """Verifica se o campo 'user_prompt' existe e contém a variável de input."""
        assert "user_prompt" in prompt_data, "Campo 'user_prompt' não encontrado no prompt"
        user_prompt = prompt_data["user_prompt"]
        assert user_prompt is not None, "user_prompt é None"
        assert len(user_prompt.strip()) > 0, "user_prompt está vazio"
        assert "{bug_report}" in user_prompt, (
            "user_prompt deve conter a variável {bug_report}"
        )

    def test_prompt_structure_valid(self, prompt_data):
        """Verifica a estrutura geral do prompt usando a função de validação."""
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Prompt inválido: {', '.join(errors)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])