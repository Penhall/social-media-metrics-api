from datetime import datetime, timedelta
from typing import Optional

def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> Optional[datetime]:
    """Converte string para datetime conforme formato especificado"""
    try:
        return datetime.strptime(date_str, fmt)
    except (ValueError, TypeError):
        return None

def format_date(date: datetime, fmt: str = "%Y-%m-%d") -> str:
    """Formata datetime para string conforme formato especificado"""
    return date.strftime(fmt)

def get_date_range(days: int = 7) -> tuple[datetime, datetime]:
    """Retorna intervalo de datas (hoje - dias, hoje)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def is_within_date_range(
    date: datetime, 
    start: datetime, 
    end: datetime
) -> bool:
    """Verifica se data está dentro do intervalo especificado"""
    return start <= date <= end