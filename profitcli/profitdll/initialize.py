# profitcli/profitdll/initialize.py

from ctypes import WinDLL

from profitcli.profitdll.profit_dll import initializeDll


def initialize_profit_dll(dll_path: str) -> WinDLL:
    """
    Inicializa a Profit DLL e configura argtypes/restype.

    Centralizar isso aqui evita:
    - imports circulares
    - duplicação
    - bagunça no contexto
    """
    return initializeDll(dll_path)
