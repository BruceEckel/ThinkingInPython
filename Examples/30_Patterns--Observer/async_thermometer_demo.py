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
    await t.set_celsius(20)  # Below the alarm threshold
    print("announced 20")
    await t.set_celsius(150)  # Triggers the alarm too
    print("announced 150")

asyncio.run(main())
#: logged: 20C
#: announced 20
#: logged: 150C
#: alarm sent: 150C
#: announced 150
