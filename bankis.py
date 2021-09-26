from bankisbase import BankisBase

class Bankis(BankisBase):
    def __init__(self):
        super().__init__()
        self.sent_w_param = 0
        self.received_w_param = 0

        self.init()

    def init(self):
        print('Test initiated')
        account_count = self.dynamic_call('GetAccountCount')
        stock_account = self.dynamic_call('GetAccount', 0)
        futures_account = self.dynamic_call('GetAccount', 1)
        is_simulation = self.dynamic_call('IsVTS')
        print('Number of accounts', account_count)
        print('Stock account:', stock_account)
        print('Futures account:', futures_account)
        print('Simulation :', is_simulation)

        # Event Connect
        self.ReceiveData.connect(self.receive_data)
        self.ReceiveRealData.connect(self.receive_real_data)
        self.ReceiveErrorData.connect(self.receive_error_data)
        self.ReceiveSysMessage.connect(self.receive_sys_message)

        item_code = '005930'
        item_s = self.dynamic_call('GetSingleDataStockMaster', item_code, 1)
        item_name = self.dynamic_call('GetSingleDataStockMaster', item_code, 2)
        print('item standard code', item_s)
        print('item name', item_name)

        self.dynamic_call('SetSingleData', 0, 'J')
        self.dynamic_call('SetSingleData', 1, '005930')
        self.dynamic_call('RequestData', 'SCP')
        self.sent_w_param = self.dynamic_call('GetSendRqID')
        print('sent sPARAM', self.sent_w_param)

    def receive_data(self):
        print('========== Data received ==========')
        self.received_w_param = self.dynamic_call('GetRecvRqID')
        print('received sPARAM', self.received_w_param)

        field_count = self.dynamic_call('GetSingleFieldCount')
        print('single field count:', field_count)

        value = self.dynamic_call('GetSingleData', 11, 0)
        attribute = self.dynamic_call('GetSingleData', 11, 1)
        print('value', value)
        print('attribute', attribute)

        # a = 0
        # b = 0
        # c = 0
        # d = 0
        # result = self.dynamic_call('GetMultiData', a, b, c, d)
        # print('Result:', result)
        # print('abcd', a, b, c, d)

    def receive_real_data(self):
        print('========== Real data received ==========')

    def receive_error_data(self):
        print('========== Error data received ==========')

    def receive_sys_message(self, param):
        print('========== System message received ==========')
        print(param)