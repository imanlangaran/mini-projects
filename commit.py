import os
from datetime import datetime

# os_out = os.popen("")

os_out = os.popen("git add .").read()

commit_message = datetime.now().strftime("%m/%d %H:%M")
os_out = os.popen(f'git commit -m "{commit_message}"').read()
