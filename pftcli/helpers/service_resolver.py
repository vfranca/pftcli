"""
service_resolver.py

Helper único para resolução do ProfitService a partir do AppContext.
"""

from pftcli.context import AppContext
from pftcli.services.profit_service import ProfitService


def resolve_service(ctx: AppContext) -> ProfitService:
    """
    Resolve o ProfitService de forma padronizada.

    Levanta erro explícito se o serviço não estiver disponível,
    evitando estados silenciosos ou mágicos.
    """
    if not ctx:
        raise RuntimeError("AppContext não fornecido")

    service = getattr(ctx, "service", None)

    if service is None:
        raise RuntimeError("ProfitService não está disponível no AppContext")

    return service
