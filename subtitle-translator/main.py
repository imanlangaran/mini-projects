import os 
from googletrans import Translator

filepath = os.getcwd()

src_file  = "english-sub.srt"
dest_file = "farsi-sub.txt"

nums = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9']

translator = Translator()


with open(os.path.join(filepath, src_file)) as f:
    sub_lines = f.readlines()


with open(os.path.join(filepath, dest_file), 'w', encoding="utf-8") as f:
    for line_en in sub_lines:
        if line_en[0] in nums:
            f.write(line_en)

        elif line_en=='\n':
            f.write('\n')
            
        else:
            if line_en:
                print(line_en)
                line_fa = translator.translate(line_en, src='en', dest='fa')
                f.write(line_fa.text)