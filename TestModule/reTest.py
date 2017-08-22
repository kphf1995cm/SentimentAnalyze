import re

x=raw_input('x=')
while x:
    print type(x)
    m=re.match('-?\d+\.?\d+',str(x))
    if m:
        print type(m),m,m.group(),type(m.group())
    x=raw_input('x=')