import re

def match_test():
    x = raw_input('x=')
    while x:
        print type(x)
        m = re.match('-?\d+\.?\d+', str(x))
        if m:
            #print type(m), m, m.group(), type(m.group())
            print  re.sub('\.$','',m.group())
        x = raw_input('x=')

def search_test():
    x=raw_input('x=')
    while x:
        print type(x)
        m = re.search('\.$', str(x))
        if m:
            print type(m), m, m.group(), type(m.group())
        x = raw_input('x=')
def sub_test():
    x=raw_input('x=')
    while x:
        print type(x)
        m = re.sub('\.$','*',str(x))
        if m:
            print type(m), m
        x = raw_input('x=')
if __name__=='__main__':
    match_test()
