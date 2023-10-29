import codecs
import sys

# filename = r"E:\DriveE\ido_writings\MSGES\MSG1.TXT"
filename = sys.argv[1]
result = filename + '.NEW'

with codecs.open(filename, encoding='cp862') as f:
    lines = f.read().splitlines()

def fix_ulti(str):
    res = str
    res = res.replace('0.','ם.')
    res = res.replace('O ','ם ')
    res = res.replace('.0','.ם')
    res = res.replace(',0',',ם')
    res = res.replace(' O',' ם')
    res = res[::-1]
    return res


revs = [fix_ulti(line) for line in lines]


for rev in revs:
    print((rev))
#

with codecs.open(result, "w", "utf-16") as f:
    for rev in revs:
        f.write(rev+'\r\n')
