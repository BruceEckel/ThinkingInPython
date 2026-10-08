# async_thermometer_demo.py
import asyncio
from async_thermometer import Thermometer

async def alarm(celsius: float) -> None:
    if celsius > 100:
        await asyncio.sleep(0.05)  # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)  # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer(15.0)
    t.connect(alarm)
    t.connect(log_reading)
    print("set 20:")
    await t.set_celsius(20)  # Below the alarm threshold
    print("set 150:")
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: set 20:
#: logged: 20C
#: set 150:
#: logged: 150C
#: alarm sent: 150C
