"""
Utility functions for the project.

Por quê ter um módulo de utils?
- Funções reutilizáveis em vários lugares
- Evita duplicação de código
- Facilita testes unitários
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def load_json_file(filepath: str, default: Any = None) -> Dict:
    """
    Carrega arquivo JSON com tratamento de erros.
    
    Args:
        filepath: Caminho do arquivo
        default: Valor retornado se arquivo não existir
        
    Returns:
        Dados do JSON ou valor default
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON {filepath}: {e}")
        return default if default is not None else {}


def save_json_file(filepath: str, data: Dict, indent: int = 2):
    """
    Salva dados em arquivo JSON.
    
    Args:
        filepath: Caminho do arquivo
        data: Dados para salvar
        indent: Indentação (para legibilidade)
    """
    # Cria diretório se não existir
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def format_date(date_string: str, format: str = '%d/%m/%Y') -> str:
    """
    Formata string ISO de data para formato amigável.
    
    Por quê?
    - API retorna ISO 8601 (2024-01-26T10:30:00Z)
    - Usuários preferem formatos localizados
    
    Args:
        date_string: Data em formato ISO
        format: Formato de saída
        
    Returns:
        Data formatada
    """
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime(format)
    except:
        return date_string


def calculate_percentage(part: int, total: int) -> float:
    """
    Calcula percentual com segurança.
    
    Por quê função separada?
    - Evita divisão por zero
    - Centraliza arredondamento
    - Reutilizável
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def generate_progress_bar(percentage: float, length: int = 20, 
                         filled_char: str = '█', empty_char: str = '░') -> str:
    """
    Gera barra de progresso visual para README.
    
    Por quê visual?
    - Mais atrativo que números
    - Facilita comparação rápida
    - Padrão em perfis do GitHub
    
    Args:
        percentage: Valor entre 0 e 100
        length: Tamanho da barra
        filled_char: Caractere para parte preenchida
        empty_char: Caractere para parte vazia
        
    Returns:
        String com barra de progresso
        
    Exemplo:
        >>> generate_progress_bar(75, 10)
        '███████░░░'
    """
    filled = int((percentage / 100) * length)
    empty = length - filled
    return filled_char * filled + empty_char * empty


def humanize_number(num: int) -> str:
    """
    Formata números grandes de forma legível.
    
    Por quê?
    - 1000000 → 1M
    - 1500 → 1.5K
    - Mais limpo visualmente
    
    Args:
        num: Número para formatar
        
    Returns:
        String formatada
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def time_ago(date_string: str) -> str:
    """
    Converte data em string "tempo atrás".
    
    Por quê?
    - "2 dias atrás" é mais natural que "24/01/2024"
    - Comum em redes sociais
    - Mais intuitivo
    
    Args:
        date_string: Data em formato ISO
        
    Returns:
        String de tempo relativo
    """
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        now = datetime.now(date.tzinfo)
        diff = now - date
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "agora há pouco"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minuto{'s' if minutes != 1 else ''} atrás"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hora{'s' if hours != 1 else ''} atrás"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} dia{'s' if days != 1 else ''} atrás"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks} semana{'s' if weeks != 1 else ''} atrás"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} mês{'es' if months != 1 else ''} atrás"
        else:
            years = int(seconds / 31536000)
            return f"{years} ano{'s' if years != 1 else ''} atrás"
    except:
        return "data inválida"
