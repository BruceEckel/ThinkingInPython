# from_snapshot.py
import app_settings
from app_settings import debug

app_settings.debug = True
print(debug, app_settings.debug)
#: False True
app_settings.show()
#: app_settings.debug is True
