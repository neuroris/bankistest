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

        result = self.dynamicCall('IsVTS()')
        print(result)

        self.ReceiveData.connect(self.receive_data)
        self.ReceiveRealData.connect(self.receive_real_data)

        self.dynamicCall('SetSingleData(0, "005930")')
        # self.dynamicCall('SetSingleData(0, 005930)')

        self.dynamicCall('RequestData("SCPD")')

        field_count = self.dynamicCall('GetSingleFieldCount()')
        print('single field count:', field_count)

    def receive_data(self):
        print('Data received')
        data = self.dynamicCall('GetSingleData(0, 0)')
        print('Data:', data)

    def receive_real_data(self):
        print('Real data received')

    # def ReceiveData(self):
    #     print('Data Received')
    #     data = self.dynamicCall('GetSingleData()')