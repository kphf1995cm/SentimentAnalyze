# encoding=utf-8

import os
import time
filename='D:/crambData\crambData6/output3.txt'

def remove_file():
    if os.path.exists(filename):
        os.remove(filename)

def clear_file_cont(num):
    f=open(filename,'r+')
    f.seek(num,0)
    s=f.readlines()
    tmp=''.join(s)
    ll=tmp.split('\n')
    f.close()
    return ll
def write_file():
    f = open(filename, 'a+')
    f.write('abcdef')
    f.close()

def read_row(rownum):
    f=open(filename,'r')
    count=0
    row_pos=[]
    while True:
        line=f.readline()
        if line:
            row_pos.append(f.tell())
            count+=1
        else:
            break
    if count<rownum:
        return 0
    else:
        return row_pos[count-rownum]
    f.close()

def get_txt_data_from_window_pos(windowSize,filepath, para,pos):
    if para == 'lines':
        f = open(filepath, 'r')
        f.seek(pos,0)
        row_pos=[]
        row_data=[]
        row_count=0
        while True:
            line=f.readline()
            if line:
                row_data.append(line)
                row_count+=1
                row_pos.append(len(line))
            else:
                break
        data_str=''.join(row_data)
        data_list=data_str.split('\n')
        data_list.pop(len(data_list)-1)
        f.close()
        if row_count<windowSize:
            return data_list,pos
        else:
            pos_sum=0
            for pos in range(row_count-windowSize+1):
                pos_sum+=row_pos[pos]
            return data_list,pos_sum+pos

def read_rows():
    f=open(filename,'r')
    s=f.readlines()
    print s

def get_txt_data_from_pos(filepath, para,pos):
    if para == 'lines':
        txt_file1 = open(filepath, 'r')
        txt_file1.seek(pos,0)
        txt_tmp1 = txt_file1.readlines()
        txt_tmp2 = ''.join(txt_tmp1)
        txt_data1 = txt_tmp2.decode('utf-8').split('\n')
        txt_data1.pop(len(txt_data1)-1) #去掉最后一行，因为最后一行有可能为空
        cur_pos=txt_file1.tell()
        txt_file1.close()
        return txt_data1,cur_pos
    elif para == 'line':
        txt_file2 = open(filepath, 'r')
        txt_file2.seek(pos, 0)
        txt_tmp = txt_file2.readline()
        txt_data2 = txt_tmp.decode('utf-8')
        cur_pos = txt_file2.tell()
        txt_file2.close()
        return txt_data2,cur_pos

def testScrab(timeInterval):
    pos=0
    while True:
        begin = time.clock()
        data, pos = get_txt_data_from_pos(filename, 'lines', pos)
        print len(data),pos
        for x in data:
            print x
        while time.clock() - begin < timeInterval:
            pass

def test():
    f=open(filename,'r')
    pos_set=[]
    while True:
        line=f.readline()
        if line:
            pos_set.append(f.tell())
        else:
            break
    f.close()
    return pos_set

if __name__=='__main__':
    testScrab(10)


