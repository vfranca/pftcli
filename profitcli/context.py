from pathlib import Path

from profitcli.profitdll.trade_subscription import TradeSubscriber
from profitcli.profitdll.initialize import initialize_profit_dll


class AppContext:
    """
    Contexto global da aplicação.

    Responsável por:
    - Inicializar a Profit DLL
    - Manter referências de callbacks (evitar GC)
    - Compartilhar estado entre plugins
    """

    def __init__(self):
        self.dll = None
        self.trade_subscriber = None

    def initialize(self):
        """
        Inicializa a Profit DLL e subsistemas.
        """
        dll_path = self._resolve_dll_path()

        # Carrega a DLL (WinDLL + argtypes/restype)
        self.dll = initialize_profit_dll(dll_path)

        # Inicializa subscritor de trades
        self.trade_subscriber = TradeSubscriber(self.dll)

    def _resolve_dll_path(self) -> str:
        """
        Resolve o caminho da Profit DLL.

        Ajuste conforme seu ambiente:
        - instalação local
        - variável de ambiente
        - config futura (YAML)
        """
        # Exemplo simples (ajuste conforme necessário)
        base = Path("C:/Profit/ProfitDLL")
        dll = base / "ProfitDLL64.dll"

        if not dll.exists():
            raise FileNotFoundError(
                f"Profit DLL não encontrada em {dll}"
            )

        return str(dll)
