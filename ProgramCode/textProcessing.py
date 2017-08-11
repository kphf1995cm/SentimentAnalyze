#! /usr/bin/env python2.7
#coding=utf-8

""" 
Read data from excel file and txt file.
Chinese word segmentation, postagger, sentence cutting and stopwords filtering function.
"""
'''
数据读取、中文分词 词性标注 句子切割 停用词过滤 格式转换
'''

import xlrd
import jieba
import jieba.posseg
import xlwt

'''导入用户词典增加中文分词的准确性 词典格式为：词语 词频（可以适时更新）'''
jieba.load_userdict('D:/ReviewHelpfulnessPrediction/PreprocessingModule/userdict.txt')

"""
input: An excel file with product review
	手机很好，很喜欢。
    三防出色，操作系统垃圾！
    Defy用过3年感受。。。
    刚买很兴奋。当时还流行，机还很贵
    ……
output:
    parameter_1: Every cell is a value of the data list. (unicode) 获取excel某一列值列表
    parameter_2: Excel row number. (int) 获取行数量
test code：
print(get_excel_data('D:/ReviewHelpfulnessPrediction\ReviewSet/HTC_Z710t_review_2013.6.5.xlsx',1,4,'data'))
"""
def get_excel_data(filepath, sheetnum, colnum, para):
    table = xlrd.open_workbook(filepath)
    sheet = table.sheets()[sheetnum-1]
    data = sheet.col_values(colnum-1)
    rownum = sheet.nrows
    if para == 'data':
        return data
    elif para == 'rownum':
        return rownum

"""
input:
    parameter_1: A txt file with many lines
    parameter_2: A txt file with only one line of data
output:
    parameter_1: Every line is a value of the txt_data list. (unicode) 获取行数据列表
    parameter_2: Txt data is a string. (str)
test code:
print get_txt_data('C:/Users\kuangp@wangsu.com\ReviewHelpfulnessPrediction27\PreprocessingModule\stopword.txt','lines')
"""
def get_txt_data(filepath, para):
    if para == 'lines':
        txt_file1 = open(filepath, 'r')
        txt_tmp1 = txt_file1.readlines()
        txt_tmp2 = ''.join(txt_tmp1)
        txt_data1 = txt_tmp2.decode('utf-8').split('\n')
        txt_data1.pop(len(txt_data1)-1) #去掉最后一行，因为最后一行有可能为空
        txt_file1.close()
        return txt_data1
    elif para == 'line':
        txt_file2 = open(filepath, 'r')
        txt_tmp = txt_file2.readline()
        txt_data2 = txt_tmp.decode('utf-8')
        txt_file2.close()
        return txt_data2


"""
分词操作
input: 这款手机大小合适。
output:
    parameter_1: 这 款 手机 大小 合适 。(unicode) 返回一个unicode字符串
    parameter_2: [u'\u8fd9', u'\u6b3e', u'\u624b\u673a', u'\u5927\u5c0f', u'\u5408\u9002', u'\uff0c']
                  返回unicode字符串列表
"""
def segmentation(sentence, para):
    if para == 'str':
        seg_list = jieba.cut(sentence)
        seg_result = ' '.join(seg_list)
        return seg_result
    elif para == 'list':
        seg_list2 = jieba.cut(sentence)
        seg_result2 = []
        for w in seg_list2:
            seg_result2.append(w)
        return seg_result2

#print segmentation('66666666666666666666666666666','str')


"""
词性标注
input: '这款手机大小合适。'
output:
    parameter_1 str: 这 r 款 m 手机 n 大小 b 合适 a 。 x
    parameter_2 list: [(u'\u8fd9', ['r']), (u'\u6b3e', ['m']),
    (u'\u624b\u673a', ['n']), (u'\u5927\u5c0f', ['b']),
    (u'\u5408\u9002', ['a']), (u'\u3002', ['x'])]
    [('你', 'r'), ('是', 'v'), ('谁', 'r')]
test code:
str_list=postagger('我喜欢你','str')
print str_list
"""
def postagger(sentence, para):
    if para == 'list':
        pos_data1 = jieba.posseg.cut(sentence)
        pos_list = []
        for w in pos_data1:
             pos_list.append((w.word, w.flag)) #make every word and tag as a tuple and add them to a list
        return pos_list
    elif para == 'str':
        pos_data2 = jieba.posseg.cut(sentence)
        pos_list2 = []
        for w2 in pos_data2:
            pos_list2.extend([w2.word, w2.flag])
        pos_str = ' '.join(pos_list2)
        return pos_str

"""
切割句子
input: A review like this
    '这款手机大小合适，配置也还可以，很好用，只是屏幕有点小。。。总之，戴妃+是一款值得购买的智能手机。'
output: A multidimentional list
    [u'\u8fd9\u6b3e\u624b\u673a\u5927\u5c0f\u5408\u9002\uff0c',
    u'\u914d\u7f6e\u4e5f\u8fd8\u53ef\u4ee5\uff0c', u'\u5f88\u597d\u7528\uff0c',
    u'\u53ea\u662f\u5c4f\u5e55\u6709\u70b9\u5c0f\u3002', u'\u603b\u4e4b\uff0c',
    u'\u6234\u5983+\u662f\u4e00\u6b3e\u503c\u5f97\u8d2d\u4e70\u7684\u667a\u80fd\u624b\u673a\u3002']
    输出 ['。', '这款手机大小合适，', '配置也还可以，', '很好用，', '只是屏幕有点小。。。', '总之，', '戴妃+是一款值得购买的智能手机。']
Maybe this algorithm will have bugs in it 
无法处理标点符号出现在句首情况
"""
def cut_sentences_1(words):
    #words = (words).decode('utf8')
    start = 0
    i = 0 #i is the position of words
    sents = []
    punt_list = ',.!?:;~，。！？：；～ '.decode('utf8') # Sentence cutting punctuations
    for word in words:
        if word in punt_list and token not in punt_list:
            sents.append(words[start:i+1])
            start = i+1
            i += 1
        else:
            i += 1
            token = list(words[start:i+2]).pop()
    # if there is no punctuations in the end of a sentence, it can still be cutted
    if start < len(words):
        sents.append(words[start:])
    return sents
""" 没有问题 Sentence cutting algorithm without bug, but a little difficult to explain why"""
def cut_sentence_2(words):
    #words = (words).decode('utf8')
    start = 0
    i = 0 #i is the position of words
    token = 'meaningless'
    sents = []
    punt_list = ',.!?;~，。！？；～… '.decode('utf8')
    for word in words:
        if word not in punt_list:
            i += 1
            token = list(words[start:i+2]).pop()
            #print token
        elif word in punt_list and token in punt_list:
            i += 1
            token = list(words[start:i+2]).pop()
        else:
            sents.append(words[start:i+1])
            start = i+1
            i += 1
    if start < len(words):
        sents.append(words[start:])
    return sents


"""
中文分词并去停用词
input: An excel file with product reviews
    一个手机很好，很喜欢吧。
    三防出色，操作系统垃圾！
    Defy用过3年感受。。。
    刚买很兴奋。当时还流行，机还很贵
output: A multidimentional list of reviews
    ['手机', '很', '好', '很', '喜欢']
    ['三防', '出色', '操作系统', '垃圾']
    ['Defy', '用过', '3', '年', '感受']
    ['刚买', '很', '兴奋', '当时', '还', '流行', '机', '还', '很', '贵']
test code:
     seg_list=seg_fil_excel('s.xlsx',0,0)
for x in seg_list:
    print(x)
"""
def seg_fil_excel(filepath, sheetnum, colnum):
    # Read product review data from excel file and segment every review
    review_data = []
    for cell in get_excel_data(filepath, sheetnum, colnum, 'data')[0:get_excel_data(filepath, sheetnum, colnum, 'rownum')]:
        review_data.append(segmentation(cell, 'list')) # Seg every reivew
    
    # Read txt file contain stopwords
    stopwords = get_txt_data('D:/ReviewHelpfulnessPrediction/PreprocessingModule/stopword.txt', 'lines')

    # Filter stopwords from reviews
    seg_fil_result = []
    for review in review_data:
        fil = [word for word in review if word not in stopwords and word != ' ']
        seg_fil_result.append(fil)
        fil = []
 
    # Return filtered segment reviews
    return seg_fil_result
"""
中文分词并去停用词
参数里面需要加入停用词目录
input: An excel file with product reviews
    手机很好，很喜欢。
    三防出色，操作系统垃圾！
    Defy用过3年感受。。。
    刚买很兴奋。当时还流行，机还很贵
output: A multidimentional list of reviews, use different stopword list, so it will remain sentiment tokens.
['手机', '很', '好', '很', '喜欢']
['三防', '出色', '操作系统', '垃圾', '！']
['Defy', '用过', '3', '年', '感受']
['刚买', '很', '兴奋', '当时', '还', '流行', '机', '还', '很', '贵']
test code:
seg_list=seg_fil_senti_excel('s.xlsx',0,0,'sentiment_stopword.txt')
for x in seg_list:
    print(x)

"""
def seg_fil_senti_excel(filepath, sheetnum, colnum,sentimenstopwordtxtfilepath):
    # Read product review data from excel file and segment every review
    review_data = []
    for cell in get_excel_data(filepath, sheetnum, colnum, 'data')[0:get_excel_data(filepath, sheetnum, colnum, 'rownum')]:
        review_data.append(segmentation(cell, 'list')) # Seg every reivew
    
    # Read txt file contain sentiment stopwords
    sentiment_stopwords = get_txt_data(sentimenstopwordtxtfilepath, 'lines')
 
    # Filter stopwords from reviews
    seg_fil_senti_result = []
    for review in review_data:
        fil = [word for word in review if word not in sentiment_stopwords and word != ' ']
        seg_fil_senti_result.append(fil)
        fil = []
 
    # Return filtered segment reviews
    return seg_fil_senti_result
'''
中文分词并去停用词
从txt文件读取数据
每行代表一个数据项(可以改进 可尝试每一百行代表一个数据)
参数 para：line 表示只有一行数据，lines 表示有多行数据
'''
def seg_fil_txt(filepath,para):
    raw_data=get_txt_data(filepath,para)
    review_data=[]
    for single_data in raw_data:
        review_data.append(segmentation(single_data,'list'))
        # Read txt file contain stopwords
    stopwords = get_txt_data('D:/ReviewHelpfulnessPrediction/PreprocessingModule/stopword.txt', 'lines')

    # Filter stopwords from reviews
    seg_fil_result = []
    for review in review_data:
        fil = [word for word in review if word not in stopwords and word != ' ']
        seg_fil_result.append(fil)
        fil = []

    # Return filtered segment reviews
    return seg_fil_result
'''
中文分词并去停用词
将txt文件里所有数据当做一条记录处理
para：line 表示txt文件只有一行
      lines表示txt文件有多行
test code:
data=seg_fil_txt('C:/Users\kuangp@wangsu.com\ReviewHelpfulnessPrediction27\TestModel/testdata.txt','lines')
for x in data:
    print x,
'''
def seg_fil_txt_one_record(filepath,para):
    txt_sent=''
    if para == 'lines':
        txt_file1 = open(filepath, 'r')
        txt_tmp1 = txt_file1.readlines()
        txt_sent = ''.join(txt_tmp1)
        txt_file1.close()
    elif para == 'line':
        txt_file2 = open(filepath, 'r')
        txt_tmp = txt_file2.readline()
        txt_sent = ''.join(txt_tmp)
        txt_file2.close()
    seg_sent=segmentation(txt_sent, 'list')
    stopwords = get_txt_data('D:/ReviewHelpfulnessPrediction/PreprocessingModule/stopword.txt', 'lines')
    seg_sent_fil = [word for word in seg_sent if word not in stopwords and word != ' ' and word!='\n']
    return seg_sent_fil


'''将每一行txt文本数据写入到excel文件中 col_pos为要写入的excel文件列标'''
'''单个sheet最大行数是65535 如果txt文件行数过多，得将其存在多个sheet中'''
def save_txt_to_excel(txtpath,excelpath,col_pos):
    txt_file = open(txtpath, 'r')
    txt_tmp = txt_file.readlines()
    txt_tmp = ''.join(txt_tmp)
    txt_data= txt_tmp.decode('utf-8').split('\n')
    txt_file.close()
    excel_file=xlwt.Workbook(encoding='utf-8')
    sheet_name='label_data'
    sheet_pos=1
    excel_sheet=excel_file.add_sheet(sheet_name+str(sheet_pos))
    row_pos=0
    col_pos-=1
    excel_sheet.write(row_pos,col_pos,'review_data')
    row_pos+=1
    for x in txt_data:
        if row_pos==65536:
            sheet_pos+=1
            excel_sheet=excel_file.add_sheet(sheet_name+str(sheet_pos))
            row_pos=0
            excel_sheet.write(row_pos,col_pos,'review_data')
            row_pos=1
        excel_sheet.write(row_pos,col_pos,x)
        row_pos+=1

    excel_file.save(excelpath)

#save_txt_to_excel('D:/ReviewHelpfulnessPrediction\ReviewDataFeature/newoutOriData.txt','D:/ReviewHelpfulnessPrediction\LabelReviewData/test.xls',1)
#save_txt_to_excel('D:/ReviewHelpfulnessPrediction\ReviewDataFeature/FiltnewoutOriData.txt','D:/ReviewHelpfulnessPrediction\LabelReviewData/FiltData.xls',1)
























