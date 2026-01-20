# profitcli/context.py
from profitcli.profitdll.connector import ProfitDLLConnector

class AppContext:
    def __init__(self):
        self.dll = ProfitDLLConnector()

    def initialize(self):
        self.dll.connect()
