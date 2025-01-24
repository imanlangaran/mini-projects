import os
from datetime import datetime

os.popen("git add .")

commit_message = datetime.now().strftime("%m/%d %H:%M")
os.popen(f'git commit -m "{commit_message}"')
os.popen("git push")