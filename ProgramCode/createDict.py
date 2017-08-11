#! /usr/bin/env python2.7
#coding=utf-8

import textProcessing as tp
def unionDict(dict1Path,dict2Path):
    dict1=tp.get_txt_data(dict1Path,'lines')
    dict2=tp.get_txt_data(dict2Path,'lines')
    dict={}
    for x in dict1:
        dict.setdefault(x,1)
    for x in dict2:
        if dict.has_key(x)==False:
            dict.setdefault(x,1)
        else:
            dict[x]+=1
    return dict