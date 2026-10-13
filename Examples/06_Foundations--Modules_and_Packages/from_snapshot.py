# from_snapshot.py
import app_settings
from app_settings import debug

app_settings.debug = True
print(f"{debug=} {app_settings.debug=}")
#: debug=False app_settings.debug=True
app_settings.show()
#: app_settings.debug is True
