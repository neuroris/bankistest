from bankisbase import BankisBase
from bankisdata import *

class Bankis(BankisBase):
    def __init__(self, trader, log, key):
        super().__init__(trader, log, key)
        self.requests = dict()
        self.count = 0

        self.init()
        self.test()

    def init(self):
        self.debug('Test initiated...')
        self.is_simulation_mode()
        self.get_account_list()
        self.account_number = self.account_list[0]
        self.debug('Account list', self.account_list)

        # Connect slots
        self.ReceiveData.connect(self.on_receive_data)
        self.ReceiveRealData.connect(self.on_receive_real_data)
        self.ReceiveErrorData.connect(self.on_receive_error_data)
        self.ReceiveSysMessage.connect(self.on_receive_sys_message)

    def test(self):
        item_code = '122630'
        futures_code = '101R12'

        # self.request_stock_price(item_code)
        # self.request_stock_price_day(item_code)
        # self.request_stock_price_min(item_code)
        # self.request_real_data('SC_R', item_code)
        # self.request_real_data('SH_R', item_code)
        # self.request_real_data('FC_R', futures_code)

        password = self.get_encrypt_password('0000')
        self.debug(password)

        self.debug(self.account_number)

        self.order(30000, 2, item_code)

    def order(self, price, amount, item_code):
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, '0000')
        self.set_single_data(3, item_code)
        self.set_single_data(4, '01')
        # self.set_single_data(5, amount)
        self.set_single_data(5, '2')
        self.set_single_data(6, price)
        self.request_data('SCABO')

        print(self.account_number[:8])
        print(self.account_number[8:])

        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = 'SCABO'
        self.debug('SCABO', 'request ID', rq_id)

    def request_stock_price(self, item_code):
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.request_data('SCP')

        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = 'SCP'
        self.debug('SCP', 'sent request ID:', rq_id)

    def request_stock_price_day(self, item_code):
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.set_single_data(2, '20100930')
        self.request_data('SCPD')

        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = 'SCPD'
        self.debug('SCPD', 'sent request ID:', rq_id)

    def request_stock_price_min(self, item_code):
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.set_single_data(2, 60)
        self.set_single_data(3, 'Y')
        self.set_single_data(4, 'Y')
        self.request_data('PST01010300')

        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = 'PST01010300'
        self.debug('PST01010300', 'request ID', rq_id)

    def on_receive_data(self):
        rq_id = self.get_recv_rq_id()
        request = self.requests[rq_id]
        self.debug('========== Data received ({}:{}) =========='.format(request, rq_id))
        msg_code = self.get_req_msg_code()
        request_message = self.get_req_message()
        self.debug('Request message code:', msg_code)
        self.debug('Request message:', request_message)

        if request == 'SCP':
            self.get_stock_price()
        elif request == 'SCPD':
            self.get_stock_price_day()
        elif request == 'ELWP':
            self.get_elw_price()
        elif request == 'PST01010300':
            self.get_stock_price_min()

        del self.requests[rq_id]

    def on_receive_real_data(self):
        rq_id = self.get_recv_rq_id()
        self.debug('========== Real data received({})({}) =========='.format(rq_id, self.count))

        block_count = self.get_multi_block_count()
        self.debug('block count', block_count)

        record_count = self.get_multi_record_count(0)
        self.debug('record count', record_count)

        field_count = self.get_single_field_count()
        self.debug('count', field_count)

        # for field in range(count):
        #     data = self.get_single_data(field)
        #     self.debug(field, data)

        current_price = self.get_single_data(2)
        self.debug('current price', current_price)

        ask = self.get_single_data(3)
        self.debug('ask price', ask)

        self.count += 1

    def on_receive_error_data(self):
        self.debug('========== Error data received ==========')
        rt_code = self.get_rt_code()
        self.debug('rt code:', rt_code)

    def on_receive_sys_message(self, param):
        self.debug('========== System message received ==========')
        self.debug(param)

    def is_simulation_mode(self):
        simulation_mode = self.is_vts()
        if simulation_mode:
            self.debug('This connection is SIMULATION mode')
        else:
            self.debug('This is REAL mode')

    def get_account_list(self):
        self.account_list = list()
        account_count = self.get_account_count()
        for index in range(account_count):
            account = self.get_account(index)
            self.account_list.append(account)
        if not self.account_list:
            self.info('Failed to get account information')
        else:
            self.info('Account information')
        return self.account_list

    def get_item_info(self):
        item_code = '005930'
        item_s = self.get_single_data_stock_master(item_code, 1)
        item_name = self.get_single_data_stock_master(item_code, 2)
        self.debug('item standard code', item_s)
        self.debug('item name', item_name)

    def get_stock_price(self):
        field_count = self.get_single_field_count()
        self.debug('single field count:', field_count)

        value = self.get_single_data(11, 0)
        attribute = self.get_single_data(11, 1)
        self.debug('value', value)
        self.debug('attribute', attribute)
        self.debug('')

    def get_stock_price_day(self):
        field_count = self.get_single_field_count()
        self.debug('single field count:', field_count)

        day = self.get_single_data(0, 0)
        attribute = self.get_single_data(0, 1)
        self.debug('day', day)
        self.debug('attribute', attribute)
        self.debug('')

        close = self.get_single_data(4, 0)
        attribute = self.get_single_data(4, 1)
        self.debug('close', close)
        self.debug('attribute', attribute)
        self.debug('')

        for index in range(field_count):
            value = self.get_single_data(index, 0)
            self.debug(index, value)

        count = self.get_multi_record_count(0)
        self.debug(count)

    def get_stock_price_min(self):
        block_count = self.get_multi_block_count()
        self.debug('multi block count', block_count)

        for block in range(block_count):
            record_count = self.get_multi_record_count(block)
            self.debug('multi record count', record_count)

            for record in range(record_count):
                field_count = self.get_multi_field_count(block, record)
                self.debug('multi field count', field_count)

                for field in range(field_count):
                    data = self.get_multi_data(block, record, field)
                    self.debug('block({}), record({}), field({})'.format(block, record, field), data)

        answer = self.is_more_next_data()
        self.debug('answer', answer)

        self.request_next_data('PST01010300')
        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = 'PST01010300'

    def get_elw_price(self):
        field_count = self.get_single_field_count()
        self.debug('single field count:', field_count)

        value = self.get_single_data(11, 0)
        attribute = self.get_single_data(11, 1)
        self.debug('value', value)
        self.debug('attribute', attribute)
        self.debug('')

