# core/callbacks.py
from .state import login_state

def on_trading_account(account):
    """
    Callback chamado pela ProfitDLL quando uma conta é recebida
    """
    login_state["accounts"].append(account)
    login_state["account_event"].set()
