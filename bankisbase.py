from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from wookitem import Order
from wookutil import WookLog, WookUtil
from bankisdata import *
import time

class BankisBase(QAxWidget, WookLog, WookUtil):
    def __init__(self, trader, log, key):
        super().__init__('08E39D09-206D-43D1-AC78-D1AE3635A4E9')
        WookLog.custom_init(self, log)

        # For Signal
        self.trader = trader

        # Request limit
        self.previous_time = 0.0
        self.consecutive_interval_limit = 0.035

        # Deposit
        self.account_list = None
        self.account_number = 0
        self.general_account_number = ''
        self.futures_account_number = ''
        self.deposit = 0
        self.withdrawable_money = 0
        self.orderable_money = 0

        # Items and Orders
        self.portfolio = dict()
        self.monitoring_items = dict()
        self.balance = dict()
        self.open_orders = dict()
        self.order_history = dict()
        self.previous_order = Order()

        # Chart
        self.chart_prices = dict()
        self.chart_item_code = ''
        self.futures_item_code = ''
        self.is_running_chart = False

        # Eventloop
        self.event_loop = QEventLoop()

        # Variables
        self.password = '0000'

        # Fee and Tax
        self.futures_fee_ratio = 0.0000185
        self.etf_fee_ratio = 0.000146527
        self.general_fee_ratio = 0.000140527
        self.futures_tax_ratio = 0.0
        self.tax_ratio = 0.0023

    def get_bankis_futures_code(self, code):
        month = code[4]
        bankis_code = code[:4] + '0' + month if month.isdigit() else code[:4] + '12'
        return bankis_code

    def dynamic_call(self, function_name, *args):
        function_spec = '('
        for order in range(len(args)):
            parameter = 'p' + str(order)
            function_spec += parameter
            if order < len(args) - 1:
                function_spec += ', '
        function_spec += ')'
        function_spec = function_name + function_spec
        args = list(args)
        result = self.dynamicCall(function_spec, args)
        return result

    def set_single_data(self, field, value):
        self.dynamic_call('SetSingleData', field, value)

    def set_single_data_ex(self, block, field, value):
        self.dynamic_call('SetSingleDataEx', block, field, value)

    def set_multi_data(self, record, field, value):
        self.dynamic_call('SetMultiData', record, field, value)

    def set_multi_block_data(self, block, record, field, value):
        result = self.dynamic_call('SetMultiBlockData', block, record, field, value)
        return result

    def get_single_field_count(self):
        field_count = self.dynamic_call('GetSingleFieldCount')
        return field_count

    def get_multi_block_count(self):
        block_count = self.dynamic_call('GetMultiBlockCount')
        return block_count

    def get_multi_record_count(self, block):
        record_count = self.dynamic_call('GetMultiRecordCount', block)
        return record_count

    def get_multi_field_count(self, block, record):
        field_count = self.dynamic_call('GetMultiFieldCount', block, record)
        return field_count

    def get_single_data(self, field, attribute=0):
        data = self.dynamic_call('GetSingleData', field, attribute)
        return data

    def get_multi_data(self, block, record, field, attribute=0):
        data = self.dynamic_call('GetMultiData', block, record, field, attribute)
        return data

    def new_get_multi_data(self, *precedent_args):
        def custom_get_multi_data(*args):
            new_args = precedent_args + args
            result = self.get_multi_data(*new_args)
            return result
        return custom_get_multi_data

    def get_req_msg_code(self):
        code = self.dynamic_call('GetReqMsgCode')
        return code

    def get_rt_code(self):
        code = self.dynamic_call('GetRtCode')
        return code

    def get_req_message(self):
        message = self.dynamic_call('GetReqMessage')
        return message

    def request_data(self, service_option):
        self.check_time_rule()
        service = service_option.split('*')[0]
        self.dynamic_call('RequestData', service)
        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = service_option

    def request_next_data(self, service):
        self.check_time_rule()
        self.dynamic_call('RequestNextData', service)
        rq_id = self.get_send_rq_id()
        self.requests[rq_id] = service

    def request_real_data(self, service, field):
        self.check_time_rule()
        self.dynamic_call('RequestRealData', service, field)

    def unrequest_real_data(self, service, field):
        self.check_time_rule()
        self.dynamic_call('UnRequestRealData', service, field)

    def unrequest_all_real_data(self):
        self.check_time_rule()
        self.dynamic_call('UnRequestAllRealData')

    def has_more_next_data(self):
        result = self.dynamic_call('IsMoreNextData')
        return result

    def get_account_count(self):
        count = self.dynamic_call('GetAccountCount')
        return count

    def get_account(self, index):
        account = self.dynamic_call('GetAccount', index)
        return account

    def get_account_br_code(self, account):
        code = self.dynamic_call('GetAccountBrCode', account)
        return code

    def get_encrypt_password(self, password):
        encrypt_password = self.dynamic_call('GetEncryptPassword', password)
        return encrypt_password

    def get_overseas_stock_sise(self):
        info = self.dynamic_call('GetOverSeasStockSise')
        return info

    def get_send_rq_id(self):
        w_param = self.dynamic_call('GetSendRqID')
        return w_param

    def get_recv_rq_id(self):
        w_param = self.dynamic_call('GetRecvRqID')
        return w_param

    def get_single_data_stock_master(self, item_code, field):
        data = self.dynamic_call('GetSingleDataStockMaster', item_code, field)
        return data

    def is_vts(self):
        result = self.dynamic_call('IsVTS')
        return result

    def check_time_rule(self):
        time_interval = time.time() - self.previous_time
        if time_interval < self.consecutive_interval_limit:
            waiting_time = self.consecutive_interval_limit - time_interval
            print('now waiting consecutive interval')
            time.sleep(waiting_time)

        current_time = time.time()
        self.previous_time = current_time

    def get_data(self, request):
        block_count = self.get_multi_block_count()
        for block in range(block_count):
            record_count = self.get_multi_record_count(block)
            for record in range(record_count):
                field_count = self.get_multi_field_count(block, record)
                for field in range(field_count):
                    data = self.get_multi_data(block, record, field)
                    self.debug('block({}), record({}), field({})'.format(block, record, field), data)

        more_data = self.has_more_next_data()
        if more_data:
            self.request_next_data(request)

    def standardize(self, term):
        result = ''
        if term == '매수':
            result = '+' + term
        # elif term == '매도':
        #     result = '-' + term
        return result

    def get_fee(self, item, price):
        fee_ratio = self.general_fee_ratio
        if item.item_code[:3] == FUTURES_CODE:
            fee_ratio = self.futures_fee_ratio
        elif item.item_name[:5] == 'KODEX':
            fee_ratio = self.etf_fee_ratio
        fee = int(price * fee_ratio / 10) * 10
        return fee

    def get_tax(self, item):
        tax = 0
        if item.item_code[:3] == FUTURES_CODE:
            tax = int(item.evaluation_sum * self.futures_tax_ratio)
        elif item.item_name[:5] != 'KODEX':
            tax = round(item.evaluation_sum * self.tax_ratio)
        return tax
