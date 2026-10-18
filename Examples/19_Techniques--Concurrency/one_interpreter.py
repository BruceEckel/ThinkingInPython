# one_interpreter.py
from concurrent import interpreters

def grow(orders: list[int]) -> list[int]:
    orders.append(4)
    return orders

orders = [1, 2, 3]
interp = interpreters.create()
print(interp.call(grow, orders), orders)
#: [1, 2, 3, 4] [1, 2, 3]
queue = interpreters.create_queue()
interp.prepare_main(queue=queue)
interp.exec("queue.put(sum(range(10)))")
print(queue.get())
#: 45
interp.exec("queue.put('orders' in globals())")
print(queue.get())
#: False
interp.close()
