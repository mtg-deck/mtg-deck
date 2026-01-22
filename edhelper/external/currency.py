import httpx
from edhelper.infra.config import settings


def get_usd_to_brl_rate() -> float:
    """
    Busca a taxa de conversão USD para BRL.
    Pode usar uma API pública como exchangerate-api.io ou similar.
    """
    # Opção 1: Usar API pública gratuita (exemplo com exchangerate-api.io)
    # url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # Opção 2: Usar API do Banco Central do Brasil
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
    
    try:
        with httpx.Client() as client:
            resp = client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            
            if data and len(data) > 0:
                return float(data[0]["valor"])
            else:
                # Fallback: usar taxa fixa ou outra API
                return 5.0  # Taxa aproximada, ajuste conforme necessário
    except Exception:
        # Fallback em caso de erro
        return 5.0  # Taxa aproximada


def convert_usd_to_brl(usd_price: float) -> str:
    """
    Converte preço de USD para BRL e formata como string no formato brasileiro.
    """
    rate = get_usd_to_brl_rate()
    brl_price = usd_price * rate
    
    # Formatar como R$ X,XX
    return f"{brl_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")