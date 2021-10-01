from PyQt5.QAxContainer import QAxWidget
from wookutil import WookLog, WookUtil

class BankisBase(QAxWidget, WookLog, WookUtil):
    def __init__(self, trader, log, key):
        super().__init__('08E39D09-206D-43D1-AC78-D1AE3635A4E9')
        WookLog.custom_init(self, log)

        # Deposit
        self.account_list = None
        self.account_number = 0
        self.deposit = 0
        self.withdrawable_money = 0
        self.orderable_money = 0

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

    def get_req_msg_code(self):
        code = self.dynamic_call('GetReqMsgCode')
        return code

    def get_rt_code(self):
        code = self.dynamic_call('GetRtCode')
        return code

    def get_req_message(self):
        message = self.dynamic_call('GetReqMessage')
        return message

    def request_data(self, service):
        self.dynamic_call('RequestData', service)

    def request_next_data(self, service):
        self.dynamic_call('RequestNextData', service)

    def request_real_data(self, service, field):
        self.dynamic_call('RequestRealData', service, field)

    def unrequest_real_data(self, service, field):
        self.dynamic_call('UnRequestRealData', service, field)

    def unrequest_all_real_data(self):
        self.dynamic_call('UnRequestAllRealData')

    def is_more_next_data(self):
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