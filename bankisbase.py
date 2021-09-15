from PyQt5.QAxContainer import QAxWidget

class BankisBase(QAxWidget):
    def __init__(self):
        super().__init__('08E39D09-206D-43D1-AC78-D1AE3635A4E9')
        print('BankisBase start')