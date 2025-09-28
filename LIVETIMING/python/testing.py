# class test:
#     def __init__(self, john: str, jeff: str, *args, **kwargs):
#         self.john = john
#         self.jeff = jeff
#         for key in kwargs.keys():
#             self.__setattr__(key, kwargs.get(key))
#         print(self.jim)

# f = test(john="John", jeff="Jeff", jim="Jim")
import serial.tools.list_ports

print(serial.tools.list_ports.comports())