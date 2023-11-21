import os

os_out = os.popen("tree -I *.jpg -I *.zip -I *.md -I *.png -I *.tif").read()

os_out = os_out[0:os_out[:-1].rfind("\n")]

os_out = os_out.replace(".", "mini-projects",1) 

out_str = """
# Mini projects

In this repo i'll upload my personal mini projects and files

## Directory Tree

```
"""

out_str += os_out
out_str += "```"

with open("README.md","w") as b:
    b.write(out_str)
    b.close()
    