from PyQt5.QAxContainer import QAxWidget

class BankisBase(QAxWidget):
    def __init__(self):
        super().__init__('08E39D09-206D-43D1-AC78-D1AE3635A4E9')

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