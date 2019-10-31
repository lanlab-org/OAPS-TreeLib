from datetime import datetime



'''
current time:

print(str(datetime.now())[:-7])
'''

'''
str = 'Fuck'
for word in str.split():
    print(word)
'''

'''
email = '732199992@qq.com'
pre = email[:email.rfind('@')]
display = pre[:len(pre)//2]
suf = email[email.rfind('@')+1:]

for i in range(len(pre[len(pre)//2:])):
    display += '*'

print(display + suf)
'''




# def mydecor_milk(func):
#     def my_method():
#         return 'mydecor *' + func()
#     return my_method
#
#
# @mydecor_milk
# def coffee():
#     return 'mycoffee'
#
#
# print(coffee())



# list = [1,2,4,3]
# it = iter(list)
#
# for i in it:
#     print(i)
#
#
# for x in list:
#     print(x)


# import sys
# list = [1,2,3,4]
# it = iter(list)
#
# while True:
#     try:
#         print(next(it))
#     except StopIteration:
#         print('gay, chao chu fan wei le')
#         sys.exit()










#
# class ContactList(list):
#     def search(self, name):
#         matching_contacts = []
#
#         for contact in self:
#             if name in contact.name:
#                 matching_contacts.append(contact)
#
#         return matching_contacts
#
#
# class Contact:
#     all_contacts = ContactList()
#
#     def __init__(self, name):
#         self.name = name
#         self.all_contacts.append(self)
#
#
# c1 = Contact('tom A')
# c2 = Contact('Jerry B')
# c3 = Contact('funny c')
#
# for x in c1.all_contacts.search('   '):
#     print(x.name)


# class test:
#     list = [1, 2, 3, 4]
#
#     def __init__(self):
#         self.list = [5, 6, 7, 8]
#
#
# t = test()
#
# for i in t.list:
#     print(i)
#
# for i in test.list:
#     print(i)


# 所以我们创建一个generator后，基本上永远不会调用next()，而是通过for循环来迭代，并且不需要关心StopIteration的错误，generator非常强大，如果推算的算法比较复杂，用类似列表生成式的for循环无法实现的时候，还可以用函数来实现。
# a = (x*x for x in range(3))
#
# while True:
#     try:
#         print(next(a))
#     except StopIteration:
#         print('end')
#         break


# def fib(max):
#     n, a, b = 0, 0, 1
#     while n < max:
#         yield a
#         a, b = b, a+b
#         n = n + 1
#     return 'done'
#
# a = fib(10)
# print(a.__next__())
# print(a.__next__())
# print(a.__next__())
# print(a.__next__())
# print(a.__next__())
# print(a.__next__())
# print(a.__next__())


# class base:
#     pass
#
#
# class son(base):
#     pass
#
# b = base()
# s = son()
#
# print(isinstance(s, base))



# observer pattern----------------------------------------------------------
#
#
# class Inventory:
#     def __init__(self):
#         self.observers = []
#         self._product = None
#         self._quantity = 0
#
#     def attach(self, observer):
#         self.observers.append(observer)
#
#     @property
#     def product(self):
#         return self._product
#
#     @product.setter
#     def product(self, value):
#         self._product = value
#         self._update_observers()
#
#     @property
#     def quantity(self):
#         return self._quantity
#
#     @quantity.setter
#     def quantity(self, value):
#         self._quantity = value
#         self._update_observers()
#
#     def _update_observers(self):
#         for o in self.observers:
#             o()
#
#
# class ConsoleObserver:
#     def __init__(self, inventory):
#         self.inventory = inventory
#
#     def __call__(self):
#         print(self.inventory.product)
#         print(self.inventory.quantity)
#
#
# class UnitedKingdomObserver(ConsoleObserver):
#     def __call__(self):
#         print('Obsever from Britain')
#         print(self.inventory.product)
#         print(self.inventory.quantity)
#
#
# class UnitedStatesObserver(ConsoleObserver):
#     def __call__(self):
#         print('Obsever from America')
#         print(self.inventory.product)
#         print(self.inventory.quantity)
#
#
# i = Inventory()
# us_observer = UnitedStatesObserver(i)
# i.attach(us_observer)
#
#
# uk_obsever = UnitedKingdomObserver(i)
# i.attach(uk_obsever)
#
# i.product = 'E45'
# i.quantity = 2



# import  random
# class WarningMessage:
#     def __init__(self, s):
#         self.s = s
#
#     def __str__(self):
#         return self.s.upper()

list = [1,2,3,4]

item = iter(list)

print(next(item))





