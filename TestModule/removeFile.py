import os
filename='a.txt'

def remove_file():
    if os.path.exists(filename):
        os.remove(filename)

def clear_file_cont(num):
    f=open(filename,'r+')
    f.seek(num,0)
    print f.readlines()
    #print f.readlines()
    len=f.tell()
    f.close()
    return len
def write_file():
    f = open(filename, 'a+')
    f.write('abcdef')
    f.close()

def read_row(rownum):
    f=open(filename,'r')
    count=0
    while True:
        line=f.readline()
        if line:
            print line,f.tell()
            count+=1
        else:
            break
    print count
    f.close()
def read_rows():
    f=open(filename,'r')
    s=f.readlines()
    print s
if __name__=='__main__':
    read_row(2)

