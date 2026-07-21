# deadlock.py
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()
both_holding = threading.Barrier(2)
both_tried = threading.Barrier(2)
timed_out = [False, False]

def worker(first: threading.Lock, second: threading.Lock,
           index: int) -> None:
    with first:
        both_holding.wait()  # Neither releases "first" until now
        if second.acquire(timeout=0.2):
            second.release()
        else:
            timed_out[index] = True
        both_tried.wait()  # Neither releases "first" until now

t1 = threading.Thread(target=worker, args=(lock_a, lock_b, 0))
t2 = threading.Thread(target=worker, args=(lock_b, lock_a, 1))
t1.start()
t2.start()
t1.join()
t2.join()
print(f"deadlock detected: {all(timed_out)}")
#: deadlock detected: True
