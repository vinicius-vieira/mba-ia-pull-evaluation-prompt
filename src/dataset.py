"""
Dataset com 15 exemplos de bugs para avaliação.

Este módulo fornece funções para carregar e gerenciar o dataset de avaliação
do desafio Bug to User Story.

O dataset contém:
- 5 bugs SIMPLES (UI/UX, validação)
- 7 bugs MÉDIOS (integração, performance, segurança, lógica de negócio)
- 3 bugs COMPLEXOS (múltiplos problemas, severidade crítica)

IMPORTANTE: Não altere os dados do dataset! Apenas os prompts devem ser otimizados.
"""

import json
from typing import List, Dict, Any
from pathlib import Path


DATASET_PATH = Path(__file__).parent.parent / "datasets" / "bug_to_user_story.jsonl"


def load_dataset(file_path: str = None) -> List[Dict[str, Any]]:
    """
    Carrega o dataset de bugs a partir do arquivo JSONL.

    Args:
        file_path: Caminho do arquivo JSONL (opcional, usa o padrão se não informado)

    Returns:
        Lista de dicionários com os exemplos do dataset
    """
    path = Path(file_path) if file_path else DATASET_PATH
    examples = []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    example = json.loads(line)
                    examples.append(example)

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {path}")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSONL: {e}")
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")

    return examples


def get_dataset_stats(examples: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retorna estatísticas do dataset.

    Args:
        examples: Lista de exemplos (carrega automaticamente se não fornecida)

    Returns:
        Dict com estatísticas do dataset
    """
    if examples is None:
        examples = load_dataset()

    stats = {
        "total": len(examples),
        "by_complexity": {},
        "by_domain": {},
        "by_type": {},
    }

    for ex in examples:
        metadata = ex.get("metadata", {})

        complexity = metadata.get("complexity", "unknown")
        stats["by_complexity"][complexity] = stats["by_complexity"].get(complexity, 0) + 1

        domain = metadata.get("domain", "unknown")
        stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1

        bug_type = metadata.get("type", "unknown")
        stats["by_type"][bug_type] = stats["by_type"].get(bug_type, 0) + 1

    return stats


def get_examples_by_complexity(complexity: str, examples: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Filtra exemplos por complexidade.

    Args:
        complexity: "simple", "medium" ou "complex"
        examples: Lista de exemplos (carrega automaticamente se não fornecida)

    Returns:
        Lista filtrada de exemplos
    """
    if examples is None:
        examples = load_dataset()

    return [
        ex for ex in examples
        if ex.get("metadata", {}).get("complexity") == complexity
    ]


if __name__ == "__main__":
    print("=" * 60)
    print("DATASET DE AVALIAÇÃO - Bug to User Story")
    print("=" * 60)

    examples = load_dataset()
    stats = get_dataset_stats(examples)

    print(f"\n📊 Total de exemplos: {stats['total']}")

    print("\n📋 Por complexidade:")
    for complexity, count in stats["by_complexity"].items():
        print(f"   - {complexity}: {count}")

    print("\n🏷️  Por domínio:")
    for domain, count in stats["by_domain"].items():
        print(f"   - {domain}: {count}")

    print("\n🔧 Por tipo:")
    for bug_type, count in stats["by_type"].items():
        print(f"   - {bug_type}: {count}")

    print("\n📝 Exemplos simples:")
    simples = get_examples_by_complexity("simple", examples)
    for i, ex in enumerate(simples, 1):
        bug = ex["inputs"]["bug_report"][:80]
        print(f"   {i}. {bug}...")

    print()
