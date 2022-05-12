from datetime import datetime
from bankisbase import BankisBase
from bankisdata import *
from wookitem import Item, BalanceItem, FuturesItem, Order
import math, time

class Bankis(BankisBase):
    def __init__(self, trader, log, key):
        super().__init__(trader, log, key)
        self.requests = dict()
        self.count = 0

        self.init()
        # self.request_deposit_info()

        self.test()

    def init(self):
        self.debug('Test initiated...')
        self.is_simulation_mode()

        account_list = self.get_account_list()
        if not account_list:
            return
        # self.account_number = self.futures_account_number
        self.account_number = self.general_account_number
        self.debug('Account list', self.account_list)

        # Connect slots
        self.ReceiveData.connect(self.on_receive_data)
        self.ReceiveRealData.connect(self.on_receive_real_data)
        self.ReceiveErrorData.connect(self.on_receive_error_data)
        self.ReceiveSysMessage.connect(self.on_receive_sys_message)

    def test(self):
        item_code = '122630'
        futures_code = '101S6000'

        # self.request_deposit_info()
        # self.request_portfolio_info()
        # self.request_futures_deposit_info()
        # self.request_futures_portfolio_info()
        # self.request_order_history()

        # self.request_stock_price(item_code)
        # self.request_stock_price_day(item_code, '20220113')

        # self.request_stock_price_min(item_code)
        # self.request_futures_stock_price_min(futures_code)
        # self.request_kospi200_index()

        # self.request_real_data('SC_R', item_code)
        # self.request_real_data('SH_R', item_code)
        # self.request_real_data('FC_R', futures_code)

        self.order(item_code, 12000, 1, '+매수', 'MARKET')

    def get_account_list(self):
        self.account_list = list()
        account_count = self.get_account_count()
        for index in range(account_count):
            account = self.get_account(index)
            self.account_list.append(account)
        for account in self.account_list:
            if account[-2:] == BANKIS_GENERAL_ACCOUNT_NUMBER_SUFFIX:
                self.general_account_number = account
            elif account[-2:] == BANKIS_FUTURES_ACCOUNT_NUMBER_SUFFIX:
                self.futures_account_number = account
            if self.general_account_number and self.futures_account_number:
                break

        if not self.account_list:
            self.info('Failed to get account information')
        else:
            self.info('Account information')
        return self.account_list

    def request_deposit_info(self):
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, self.password)
        self.set_single_data(3, 'N')
        self.set_single_data(4, 'Y')
        self.set_single_data(5, '01')
        self.set_single_data(6, 'N')
        self.request_data(SERVICE_DEPOSIT_INFO)
        self.event_loop.exec()

    def request_futures_deposit_info(self):
        password = self.get_encrypt_password(self.password)
        self.set_single_data(0, self.futures_account_number[:8])
        self.set_single_data(1, self.futures_account_number[8:])
        self.set_single_data(2, password)
        self.set_single_data(3, '01')
        self.set_single_data(4, '1')
        self.request_data(SERVICE_FUTURES_DEPOSIT_INFO)
        self.event_loop.exec()

    def request_portfolio_info(self):
        self.portfolio.clear()
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, self.password)
        self.set_single_data(3, 'N')
        self.set_single_data(4, 'Y')
        self.set_single_data(5, '02')
        self.set_single_data(6, 'N')
        self.request_data(SERVICE_PORTFOLIO_INFO)
        self.event_loop.exec()

    def request_futures_portfolio_info(self):
        self.portfolio.clear()
        password = self.get_encrypt_password(self.password)
        self.set_single_data(0, self.futures_account_number[:8])
        self.set_single_data(1, self.futures_account_number[8:])
        self.set_single_data(2, password)
        self.set_single_data(3, '01')
        self.set_single_data(4, '1')
        self.request_data(SERVICE_FUTURES_PORTFOLIO_INFO)
        self.event_loop.exec()

    def request_order_history(self):
        self.order_history.clear()
        today = datetime.now().strftime('%Y%m%d')
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, self.password)
        self.set_single_data(3, today)
        self.set_single_data(4, today)
        self.set_single_data(5, '00')
        self.set_single_data(6, '01')
        self.set_single_data(8, '00')
        self.set_single_data(11, '00')
        self.request_data(SERVICE_ORDER_HISTORY)
        self.event_loop.exec()

    def request_stock_price(self, item_code):
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.request_data(SERVICE_CURRENT_PRICE)

    def request_stock_price_day(self, item_code, date):
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.set_single_data(2, date)
        self.request_data(SERVICE_CURRENT_PRICE_DAY)

    def request_stock_price_min(self, item_code):
        self.chart_item_code = item_code
        if item_code not in self.chart_prices:
            self.chart_prices[item_code] = list()
        self.set_single_data(0, STOCK_MARKET)
        self.set_single_data(1, item_code)
        self.set_single_data(2, 60)
        self.set_single_data(3, 'Y')
        self.set_single_data(4, 'Y')
        self.request_data(SERVICE_STOCK_PRICE_MINUTE)
        self.event_loop.exec()

    def request_futures_stock_price_min(self, item_code):
        self.chart_item_code = item_code
        self.futures_item_code = item_code
        if item_code not in self.chart_prices:
            self.chart_prices[item_code] = list()
        bankis_code = self.get_bankis_futures_code(item_code)
        self.set_single_data(0, FUTURES_MARKET)
        self.set_single_data(1, bankis_code)
        self.set_single_data(2, 60)
        self.set_single_data(3, 'Y')
        self.request_data(SERVICE_FUTURES_STOCK_PRICE_MINUTE)
        self.event_loop.exec()

    def request_kospi200_index(self):
        self.chart_item_code = KOSPI200_CODE
        if KOSPI200_CODE not in self.chart_prices:
            self.chart_prices[KOSPI200_CODE] = list()
        self.set_single_data(0, 'U')
        self.set_single_data(1, KOSPI200_CODE_BANKIS)
        self.set_single_data(2, 60)
        self.request_data(SERVICE_KOSPI200_MIN)
        self.event_loop.exec()

    def order(self, item_code, price, amount, order_position, order_type, order_number=''):
        price = 0 if order_type == 'MARKET' else price
        self.order_position = order_position

        if item_code[:3] == FUTURES_CODE:
            pass
            # order_position_code = FUTURES_ORDER_POSITION[order_position]
            # trade_position = FUTURES_TRADE_POSITION[order_position]
            # order_type_code = FUTURES_ORDER_TYPE[order_type]
            # send_order = self.new_send_order_fo('order', self.screen_send_order, self.account_number)
            # send_order(item_code, order_position_code, trade_position, order_type_code, amount, price, order_number)
        else:
            order_type_code = ORDER_TYPE[order_type]
            if order_position == PURCHASE:
                self.order_purchase(item_code, price, str(amount), order_type_code)
            elif order_position == SELL:
                self.order_sale(item_code, price, str(amount), order_type_code)

    def order_purchase(self, item_code, price, amount, order_type_code):
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, self.password)
        self.set_single_data(3, item_code)
        self.set_single_data(4, order_type_code)
        self.set_single_data(5, amount)
        self.set_single_data(6, price)
        self.request_data(SERVICE_ORDER_PURCHASE)

    def order_sale(self, item_code, price, amount, order_type_code):
        self.set_single_data(0, self.account_number[:8])
        self.set_single_data(1, self.account_number[8:])
        self.set_single_data(2, self.password)
        self.set_single_data(3, item_code)
        self.set_single_data(4, order_type_code)
        self.set_single_data(5, amount)
        self.set_single_data(6, price)
        self.request_data(SERVICE_ORDER_SALE)

    def on_receive_data(self):
        rq_id = self.get_recv_rq_id()
        request = self.requests[rq_id]
        msg_code = self.get_req_msg_code()
        request_message = self.get_req_message()
        self.debug('========== Data received ({}:{}) =========='.format(request, rq_id))
        self.debug('Request message code:', msg_code)
        self.debug('Request message:', request_message)

        if request == SERVICE_DEPOSIT_INFO:
            self.get_deposit_info(request)
        elif request == SERVICE_PORTFOLIO_INFO:
            self.get_portfolio_info(request)
        elif request == SERVICE_FUTURES_DEPOSIT_INFO:
            self.get_futures_deposit_info(request)
        elif request == SERVICE_FUTURES_PORTFOLIO_INFO:
            self.get_futures_portfolio_info(request)
        elif request == SERVICE_ORDER_HISTORY:
            self.get_order_history(request)
        elif request == SERVICE_CURRENT_PRICE:
            self.get_stock_price(request)
        elif request == SERVICE_CURRENT_PRICE_DAY:
            self.get_stock_price_day(request)
        elif request == SERVICE_STOCK_PRICE_MINUTE:
            self.get_stock_price_min(request)
        elif request == SERVICE_FUTURES_STOCK_PRICE_MINUTE:
            self.get_futures_stock_price_min(request)
        elif request == SERVICE_KOSPI200_MIN:
            self.get_kospi200_index(request)
        elif request == SERVICE_ORDER_PURCHASE:
            self.obtain_executed_order_info(request)

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

    def get_deposit_info(self, request):
        self.deposit = self.get_multi_data(1, 0, 0)
        self.withdrawable_money = self.get_multi_data(1, 0, 2)
        self.orderable_money = self.get_multi_data(1, 0, 2)

        self.debug('deposit', self.deposit)
        self.debug('withdrawable', self.withdrawable_money)
        self.debug('orderable', self.orderable_money)

        self.event_loop.exit()

    def get_futures_deposit_info(self, request):
        self.deposit = self.get_multi_data(1, 0, 3)
        self.withdrawable_money = self.get_multi_data(1, 0, 26)
        self.orderable_money = self.get_multi_data(1, 0, 26)

        self.debug('deposit', self.deposit)
        self.debug('withdrawable', self.withdrawable_money)
        self.debug('orderable', self.orderable_money)

        self.event_loop.exit()

    def get_portfolio_info(self, request):
        number_of_record = self.get_multi_record_count(0)
        for record in range(number_of_record):
            get_data = self.new_get_multi_data(0, record)

            item = Item()
            item.item_code = get_data(0)
            item.item_name = get_data(1)
            item.current_price = int(get_data(11))
            item.purchase_price = float(get_data(9))
            item.holding_amount = int(get_data(7))
            item.purchase_sum = int(get_data(10))
            item.evaluation_sum = int(get_data(12))
            item.purchase_fee = self.get_fee(item, item.purchase_sum)
            item.evaluation_fee = self.get_fee(item, item.evaluation_sum)
            item.total_fee = round(item.purchase_fee + item.evaluation_fee, 0)
            item.tax = self.get_tax(item)
            item.profit = item.evaluation_sum - item.purchase_sum - item.total_fee - item.tax
            # item.profit_rate = item.profit / item.purchase_sum * 100
            item.profit_rate = math.trunc(item.profit / item.purchase_sum * 100 * 100) / 100

            self.portfolio[item.item_code] = item

            self.debug(item.purchase_fee)
            self.debug(item.evaluation_fee)
            self.debug(item.total_fee)
            self.debug(item.tax)
            self.debug(item.total_fee + item.tax)

            self.debug('item code', item.item_code)
            self.debug('item name', item.item_name)
            self.debug('current price', item.current_price)
            self.debug('purchase price', item.purchase_price)
            self.debug('holding amount', item.holding_amount)
            self.debug('purchase sum', item.purchase_sum)
            self.debug('evaluation sum', item.evaluation_sum)
            self.debug('profit', item.profit)
            self.debug('profit rate', item.profit_rate)
            self.debug('------------------------------------------------')

        if self.has_more_next_data():
            self.request_next_data(request)
        else:
            if number_of_record:
                # self.trader.update_order_variables()
                # self.trader.display_portfolio()
                self.info('Portfolio information')
            else:
                self.info('Portfolio information (No item found')
            self.trader.portfolio_acquired()

        self.event_loop.exit()

    def get_futures_portfolio_info(self, request):
        number_of_record = self.get_multi_record_count(0)
        for record in range(number_of_record):
            get_data = self.new_get_multi_data(0, record)

            item = Item()
            item.item_code = get_data(2)[3:11]
            # if not item.item_code:
            #     self.trader.display_portfolio()
            #     self.info('Portfolio information (NO ITEM)')
            #     return
            item.item_name = get_data(5)[7:]
            item.trade_position = self.standardize(get_data(6))
            item.holding_amount = int(get_data(7))
            item.purchase_price = round(float(get_data(9)), 2)
            item.purchase_sum = int(get_data(11))
            item.current_price = float(get_data(10))
            item.evaluation_sum = int(get_data(12))
            item.profit = int(get_data(13))

            item.purchase_fee = self.get_fee(item, item.purchase_sum)
            item.evaluation_fee = self.get_fee(item, item.evaluation_sum)
            item.total_fee = round(item.purchase_fee + item.evaluation_fee, 0)
            item.profit_rate = math.trunc(item.profit / item.purchase_sum * 100 * 100) / 100
            item.tax = self.get_tax(item)

            self.debug('item code', item.item_code)
            self.debug('item name', item.item_name)
            self.debug('trade position', item.trade_position)
            self.debug('holding amount', item.holding_amount)
            self.debug('purchase price', item.purchase_price)
            self.debug('purchase sum', item.purchase_sum)
            self.debug('current price', item.current_price)
            self.debug('evaluation sum', item.evaluation_sum)
            self.debug('profit', item.profit)
            self.debug('profit rate', item.profit_rate)
            self.debug('total fee', item.total_fee)
            self.debug('tax', item.tax)
        # self.get_data(request)

        if self.has_more_next_data():
            self.request_next_data(request)
        else:
            if number_of_record:
                # self.trader.update_order_variables()
                # self.trader.display_portfolio()
                self.info('Portfolio information (Futures)')
            else:
                self.info('Portfolio information (Futures) (No item found')
            self.trader.portfolio_acquired()
            self.event_loop.exit()

    def get_order_history(self, request):
        self.get_data(request)
        number_of_order = self.get_multi_record_count(0)
        for record in range(number_of_order):
            get_data = self.new_get_multi_data(0, record)

            order = Order()
            order.item_code = get_data(7)
            order.item_name = get_data(8)
            order.executed_time = get_data(26)
            order.order_amount = get_data(9)
            order.executed_amount_sum = get_data(12)
            order.open_amount = get_data(20)
            order.order_number = get_data(2)
            order.original_order_number = get_data(3)
            order.order_price = get_data(10)
            order.executed_price_avg = get_data(13)
            order.order_position = self.render_position(get_data(6))
            order.order_state = get_data(18)

            self.order_history[order.order_number] = order
            if order.open_amount != 0:
                self.open_orders[order.order_number] = order

        if self.has_more_next_data():
            self.request_next_data(request)
        else:
            # self.trader.display_order_history()
            # self.trader.display_open_orders()
            self.info('Order history information')
            self.event_loop.exit()

    def get_item_info(self):
        item_code = '005930'
        item_s = self.get_single_data_stock_master(item_code, 1)
        item_name = self.get_single_data_stock_master(item_code, 2)
        self.debug('item standard code', item_s)
        self.debug('item name', item_name)

    def get_stock_price(self, request):
        item_code = self.get_single_data(69, 0)
        current_price = self.get_single_data(11, 0)
        self.debug(item_code, current_price)

    def get_stock_price_day(self, request):
        day = self.get_single_data(0, 0)
        close_price = self.get_single_data(4, 0)
        self.debug(day, close_price)

    def get_stock_price_min(self, request):
        item_code = self.chart_item_code
        chart = self.chart_prices[item_code]
        today = int(datetime.today().strftime('%Y%m%d'))
        block_count = self.get_multi_block_count()
        for block in range(block_count):
            record_count = self.get_multi_record_count(block)
            for record in range(record_count):
                get_data = self.new_get_multi_data(block, record)
                current_date = get_data(0)
                current_time = get_data(1)
                transaction_time = current_date + current_time
                current_date = int(current_date)

                if current_date < today:
                    self.trader.process_past_chart_prices(item_code, chart)
                    self.event_loop.exit()
                    return

                open_price = int(get_data(3))
                high_price = int(get_data(4))
                low_price = int(get_data(5))
                current_price = int(get_data(2))
                volume = int(get_data(7))
                data = [transaction_time, open_price, high_price, low_price, current_price, volume]
                chart.insert(0, data)

        if self.has_more_next_data():
            self.request_next_data(request)

    def get_futures_stock_price_min(self, request):
        item_code = self.chart_item_code
        chart = self.chart_prices[item_code]
        today = int(datetime.today().strftime('%Y%m%d'))
        block_count = self.get_multi_block_count()
        for block in range(block_count):
            record_count = self.get_multi_record_count(block)
            for record in range(record_count):
                get_data = self.new_get_multi_data(block, record)
                current_date = get_data(0)
                current_time = get_data(1)
                transaction_time = current_date + current_time
                current_date = int(current_date)

                if current_date < today:
                    self.trader.process_past_chart_prices(item_code, chart)
                    self.event_loop.exit()
                    return

                open_price = float(get_data(3))
                high_price = float(get_data(4))
                low_price = float(get_data(5))
                current_price = float(get_data(2))
                volume = int(get_data(6))
                data = [transaction_time, open_price, high_price, low_price, current_price, volume]
                chart.insert(0, data)

        if self.has_more_next_data():
            self.request_next_data(request)

    def get_kospi200_index(self, request):
        item_code = self.chart_item_code
        chart = self.chart_prices[item_code]
        today = int(datetime.today().strftime('%Y%m%d'))
        block_count = self.get_multi_block_count()
        for block in range(block_count):
            record_count = self.get_multi_record_count(block)
            for record in range(record_count):
                get_data = self.new_get_multi_data(block, record)
                current_date = get_data(0)
                current_time = get_data(1)
                transaction_time = current_date + current_time
                current_date = int(current_date)

                field = self.get_multi_field_count(block, record)
                for i in range(field):
                    data = get_data(i)
                    print(i, data)
                print('------------------------------')

                # if current_date < today:
                #     self.trader.process_past_chart_prices(item_code, chart)
                #     self.debug('38383')
                #     self.event_loop.exit()
                #     return

                open_price = float(get_data(3))
                high_price = float(get_data(4))
                low_price = float(get_data(5))
                current_price = float(get_data(1))
                volume = int(get_data(6))
                data = [transaction_time, open_price, high_price, low_price, current_price, volume]
                chart.insert(0, data)

        if self.has_more_next_data():
            self.request_next_data(request)

    def obtain_executed_order_info(self, request):
        count = self.get_single_field_count()
        self.debug(count)
        for index in range(count):
            a = self.get_single_data(index, 0)
            self.debug(a)