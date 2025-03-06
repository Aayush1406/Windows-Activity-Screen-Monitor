from datetime import datetime
import pytz

time = datetime.now(pytz.UTC)
t = time.isoformat()
print(type(t))