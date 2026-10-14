# greet_demo.py
from ask_tell import Capture, Scripted, greet

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
