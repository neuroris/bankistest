from bankisbase import BankisBase

class Bankis(BankisBase):
    def __init__(self, trader, log, key):
        super().__init__(trader, log, key)
        self.sent_w_param = 0
        self.received_w_param = 0

        self.init()
        self.test()

    def init(self):
        self.debug('Test initiated...')
        self.is_simulation_mode()
        self.get_account_list()
        self.debug('Account list', self.account_list)

        # Connect slots
        self.ReceiveData.connect(self.receive_data)
        self.ReceiveRealData.connect(self.receive_real_data)
        self.ReceiveErrorData.connect(self.receive_error_data)
        self.ReceiveSysMessage.connect(self.receive_sys_message)

    def test(self):
        self.set_single_data(0, 'J')
        self.set_single_data(1, '005930')
        self.request_data('SCP')

    def get_account_list(self):
        self.account_list = list()
        account_count = self.dynamic_call('GetAccountCount')
        for index in range(account_count):
            account = self.dynamic_call('GetAccount', index)
            self.account_list.append(account)
        if not self.account_list:
            self.info('Failed to get account information')
        else:
            self.info('Account information')
        return self.account_list

    def receive_data(self):
        self.debug('========== Data received ==========')

        field_count = self.dynamic_call('GetSingleFieldCount')
        self.debug('single field count:', field_count)

        value = self.dynamic_call('GetSingleData', 11, 0)
        attribute = self.dynamic_call('GetSingleData', 11, 1)
        self.debug('value', value)
        self.debug('attribute', attribute)

    def receive_real_data(self):
        self.debug('========== Real data received ==========')

    def receive_error_data(self):
        self.debug('========== Error data received ==========')

    def receive_sys_message(self, param):
        self.debug('========== System message received ==========')
        self.debug(param)

    def is_simulation_mode(self):
        simulation_mode = self.dynamic_call('IsVTS')
        if simulation_mode:
            self.debug('This connection is SIMULATION mode:')
        else:
            self.debug('This is REAL mode')

    def get_w_param(self):
        self.sent_w_param = self.dynamic_call('GetSendRqID')
        self.debug('sent sPARAM', self.sent_w_param)
        self.received_w_param = self.dynamic_call('GetRecvRqID')
        self.debug('received sPARAM', self.received_w_param)

    def get_item_info(self):
        item_code = '005930'
        item_s = self.dynamic_call('GetSingleDataStockMaster', item_code, 1)
        item_name = self.dynamic_call('GetSingleDataStockMaster', item_code, 2)
        self.debug('item standard code', item_s)
        self.debug('item name', item_name)

