from bankisbase import BankisBase

class Bankis(BankisBase):
    def __init__(self):
        super().__init__()
        print('Bankis start')
        self.init()

    def init(self):
        print('Test initiated')
        account_count = self.dynamicCall('GetAccountCount()')
        account1 = self.dynamicCall('GetAccount(0)')
        account2 = self.dynamicCall('GetAccount(1)')
        account3 = self.dynamicCall('GetAccount(2)')
        print(account_count)
        print(account1, account2, account3)