import time

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

# Appended to static URLs (?v=...) so browsers fetch fresh CSS/JS after every restart
templates.env.globals["asset_version"] = str(int(time.time()))
