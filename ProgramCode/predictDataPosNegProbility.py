#! /usr/bin/env python2.7
#coding=utf-8

"""
Use a stored sentiment classifier to identifiy review positive and negative probability.
"""

import textProcessing as tp
import pickle
import itertools
import numpy as np
import time
import chardet
import xlwt
from random import shuffle
import types
import time
from matplotlib import pyplot as plt
from matplotlib import animation

import nltk
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

'''几点注意说明'''
'''
如果人工标注的数据（训练数据）发生更改，需要更改create_word_bigram_scores()函数里面的posdata，negdata来重新计算词语信息得分
需要以要预测数据所在的路劲作为参数
'''

'''1 导入要预测的数据，并将数据做分词以及去停用词处理，得到[[word1,word2,],[],]'''
#reviewDataSetPath='D:/ReviewHelpfulnessPrediction\ReviewSet/HTC_Z710t_review_2013.6.5.xlsx'
#sentiment_review = tp.seg_fil_senti_excel(reviewDataSetPath, 1, 4,'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')


'''计算 单个词语以及二元词语的信息增量得分'''
'''注意 需要导入带标签的积极以及消极评论语料库(如果训练数据发生修改的话，里面的相应参数需要修改)'''
def create_word_bigram_scores():
    posNegDir = 'D:/ReviewHelpfulnessPrediction\LabelReviewData'
    posdata = tp.seg_fil_senti_excel(posNegDir + '/posNegLabelData.xls', 1, 1,
                                     'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    negdata = tp.seg_fil_senti_excel(posNegDir + '/posNegLabelData.xls', 2, 1,
                                     'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')

    posWords = list(itertools.chain(*posdata))
    negWords = list(itertools.chain(*negdata))

    bigram_pos_finder = BigramCollocationFinder.from_words(posWords)
    posBigrams = bigram_pos_finder.nbest(BigramAssocMeasures.chi_sq, 5000)
    bigram_neg_finder = BigramCollocationFinder.from_words(negWords)
    negBigrams = bigram_neg_finder.nbest(BigramAssocMeasures.chi_sq, 5000)

    pos = posWords + posBigrams
    neg = negWords + negBigrams

    word_fd = FreqDist()
    cond_word_fd = ConditionalFreqDist()
    for word in pos:
        word_fd[word] += 1
        cond_word_fd['pos'][word] += 1
    for word in neg:
        word_fd[word] += 1
        cond_word_fd['neg'][word] += 1

    pos_word_count = cond_word_fd['pos'].N()
    neg_word_count = cond_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score

    return word_scores

'''挑选信息量大的前number个词语作为分类特征'''
def find_best_words(word_scores, number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words


'''2 特征提取，提取每句话里面的特征'''
'''两种方式 单词 单词+二元词'''
def best_word_features(words,best_words):
    return dict([(word, True) for word in words if word in best_words])
def best_word_features_com(words,best_words):
    d1 = dict([(word, True) for word in words if word in best_words])
    d2 = dict([(word, True) for word in nltk.bigrams(words) if word in best_words])
    d3 = dict(d1, **d2)
    return d3


''' 提取语句列表的特征'''
'''数据集应处理成这种形式：[[明天,天气],[],[],[],]'''
'''采用单词+二元词方式'''
def extract_features(dataset,best_words):
    feat = []
    for i in dataset:
        feat.append(best_word_features_com(i,best_words))
    return feat

'''3 分类预测'''
'''读取最佳分类器 最佳分类维度'''
def read_best_classifier_dimension():
    f = open('D:/ReviewHelpfulnessPrediction\BuildedClassifier/bestClassifierDimenAcc.txt')
    clf_dim_acc=f.readlines()
    src_data=''
    for x in clf_dim_acc:
        src_data+=x
    data=src_data.split('$')
    best_classifier=data[0]
    best_dimension=data[1]
    print best_classifier,best_dimension
    return best_classifier,best_dimension

start=time.clock()
best_classifier,best_dimension=read_best_classifier_dimension()
word_scores = create_word_bigram_scores() #计算词语信息得分
best_words = find_best_words(word_scores, int(best_dimension)) # 选取前best_dimension个信息得分高的词语作为特征 best_dimension根据最佳分类器的最佳维度来设定
end=time.clock()
print 'feature extract time:',end-start


'''输出类标签 分类概率 原始数据 原始数据特征 调试过程中采用'''
def predictDataSentimentPro(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,sheetNum,colNum,desDir):
    reviewDataSetPath=reviewDataSetDir+'/'+reviewDataSetName+reviewDataSetFileType
    oriDataPath=desDir+'/'+reviewDataSetName+'OriData.txt'
    oriDataFeaPath = desDir + '/' + reviewDataSetName + 'OriFea.txt'
    preResStorePath=desDir+'/'+reviewDataSetName+'ClassPro.txt'
    preTagStorePath=desDir+'/'+reviewDataSetName+'ClassTag.txt'
    start=time.clock()
    #reviewDataSetPath = 'D:/ReviewHelpfulnessPrediction\ReviewSet/HTC_Z710t_review_2013.6.5.xlsx'
    #reviewDataSetPath='D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet/pos_review.xlsx'
    review = tp.get_excel_data(reviewDataSetPath, sheetNum, colNum, "data")# 读取待分类数据
    #将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_senti_excel(reviewDataSetPath, sheetNum, colNum, 'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    #提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    #classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath='D:/ReviewHelpfulnessPrediction\BuildedClassifier/'+str(best_classifier)[0:15]+'.pkl'
    #装载分类器
    clf = pickle.load(open(classifierPath))
    #分类之预测数据类标签
    data_tag=clf.batch_classify(review_feature)
    p_file = open(preTagStorePath, 'w')
    for i in data_tag:
        p_file.write(str(i)+ '\n')
    p_file.close()
    #分类之预测数据积极、消极可能性
    pred = clf.batch_prob_classify(review_feature)
    # 记录分类结果 积极可能性 消极可能性
    p_file = open(preResStorePath, 'w')
    reviewCount = 0
    for i in pred:
        reviewCount += 1
        p_file.write(str(i.prob('pos')) + '\t' + str(i.prob('neg')) + '\n')
    p_file.close()
    # 记录原始数据
    p_file = open(oriDataPath, 'w')
    for d in review:
        p_file.write(d.encode('utf-8')+'\n')
    p_file.close()
    p_file = open(oriDataFeaPath, 'w')
    # 记录原始数据特征提取结果
    for d in review_feature:
        for w,b,in d.iteritems():
            if type(w) is not types.TupleType:
                p_file.write(w.encode('utf-8') +'\t')
            else:
                for x in w:
                    p_file.write(x.encode('utf-8') + '_')
        p_file.write('\n')
    p_file.close()
    end=time.clock()
    return reviewCount,end-start
'''只输出类标签 分类概率 实际应用中采用'''
def predDataSentPro(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,sheetNum,colNum,desDir):
    reviewDataSetPath=reviewDataSetDir+'/'+reviewDataSetName+reviewDataSetFileType
    preResStorePath=desDir+'/'+reviewDataSetName+'ClassPro.txt'
    preTagStorePath=desDir+'/'+reviewDataSetName+'ClassTag.txt'
    start=time.clock()
    sentiment_review = tp.seg_fil_senti_excel(reviewDataSetPath, sheetNum, colNum, 'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    #提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    #classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    #装载分类器
    clf = pickle.load(open(classifierPath))
    #分类之预测数据类标签
    data_tag=clf.batch_classify(review_feature)
    p_file = open(preTagStorePath, 'w')
    for i in data_tag:
        p_file.write(str(i)+ '\n')
    p_file.close()
    #分类之预测数据积极、消极可能性
    pred = clf.batch_prob_classify(review_feature)
    # 记录分类结果 积极可能性 消极可能性
    p_file = open(preResStorePath, 'w')
    reviewCount = 0
    for i in pred:
        reviewCount += 1
        p_file.write(str(i.prob('pos')) + '\t' + str(i.prob('neg')) + '\n')
    p_file.close()
    end=time.clock()
    return reviewCount,end-start
def predTxtDataSentPro(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,desDir):
    reviewDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    oriDataPath = desDir + '/' + reviewDataSetName + 'OriData.txt'
    oriDataFeaPath = desDir + '/' + reviewDataSetName + 'OriFea.txt'
    preResStorePath = desDir + '/' + reviewDataSetName + 'ClassPro.txt'
    preTagStorePath = desDir + '/' + reviewDataSetName + 'ClassTag.txt'
    start = time.clock()
    # reviewDataSetPath = 'D:/ReviewHelpfulnessPrediction\ReviewSet/HTC_Z710t_review_2013.6.5.xlsx'
    # reviewDataSetPath='D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet/pos_review.xlsx'
    review = tp.get_txt_data(reviewDataSetPath, "lines")  # 读取待分类数据
    # 将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_txt(reviewDataSetPath,'lines')
    # 提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    # classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    # 装载分类器
    clf = pickle.load(open(classifierPath))
    # 分类之预测数据类标签
    data_tag = clf.batch_classify(review_feature)
    p_file = open(preTagStorePath, 'w')
    for i in data_tag:
        p_file.write(str(i) + '\n')
    p_file.close()
    # 分类之预测数据积极、消极可能性
    pred = clf.batch_prob_classify(review_feature)
    # 记录分类结果 积极可能性 消极可能性
    p_file = open(preResStorePath, 'w')
    reviewCount = 0
    for i in pred:
        reviewCount += 1
        p_file.write(str(i.prob('pos')) + '\t' + str(i.prob('neg')) + '\n')
    p_file.close()
    # 记录原始数据
    p_file = open(oriDataPath, 'w')
    for d in review:
        p_file.write(d.encode('utf-8') + '\n')
    p_file.close()
    p_file = open(oriDataFeaPath, 'w')
    # 记录原始数据特征提取结果
    for d in review_feature:
        for w, b, in d.iteritems():
            p_file.write(w.encode('utf-8') + ' ' + str(b) + '\t')
        p_file.write('\n')
    p_file.close()
    end = time.clock()
    return reviewCount, end - start
# reviewDataSetDir='D:/ReviewHelpfulnessPrediction\ReviewDataFeature'
# reviewDataSetName='FiltnewoutOriData'
# reviewDataSetFileType='.txt'
# desDir='D:/ReviewHelpfulnessPrediction\ReviewDataFeature'
# recordNum,runningTime=predTxtDataSentPro(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,desDir)
# print 'handle sentences num:',recordNum,' running time:',runningTime
'''原始数据格式为txt或log,将原始数据 类标签 分类概率 原始数据特征写入txt文件中'''
'''返回：评论的积极可能性列表'''
def predictTxtDataSentTagProToTxt(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,desDir):
    reviewDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    preDataResPath = desDir + '/' + reviewDataSetName + 'RawDataTagProFea.txt'
    start = time.clock()
    review = tp.get_txt_data(reviewDataSetPath, "lines")  # 读取待分类数据
    # 将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_txt(reviewDataSetPath,'lines')
    # 提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    # classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    # 装载分类器
    clf = pickle.load(open(classifierPath))
    dataItemCount = len(sentiment_review)
    # 分类之预测数据类标签
    data_tag = clf.batch_classify(review_feature)
    # 分类之预测数据积极、消极可能性
    res_pro = clf.batch_prob_classify(review_feature)
    preResFile = open(preDataResPath,'w')
    posProbility = []
    for rowPos in range(dataItemCount):
        posProbility.append(res_pro[rowPos].prob('pos'))
        feature = ''
        # 特征里面可能出现二元词的情况
        for x in review_feature[rowPos].keys():
            if type(x) is not nltk.types.TupleType:
                feature += x
            else:
                feature += '_'.join(x)
            feature += ' '
        # preResFile.write(
        #         review[rowPos].encode('utf-8') + '\t' + str(data_tag[rowPos]))
        preResFile.write(
            review[rowPos].encode('utf-8')  + '\t' + str(data_tag[rowPos]) + '\t' + str(res_pro[rowPos].prob('pos')) + '\t' + str(
                res_pro[rowPos].prob('neg'))+'\t'+feature.encode('utf-8')+'\n')
    preResFile.close()
    end = time.clock()
    print 'handle sentences num:', dataItemCount, ' classify time:', end - start
    return posProbility,preDataResPath,review
'''原始数据格式为txt或log,将原始数据 类标签 分类概率 原始数据特征写入excel文件中'''
'''返回：评论的积极可能性列表'''
def predictTxtDataSentTagProToExcel(reviewDataSetPath,preDataResPath):
    # reviewDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    # preDataResPath = desDir + '/' + reviewDataSetName + 'RawDataTagProFea.xls'
    start = time.clock()
    review= tp.get_txt_data(reviewDataSetPath, "lines")  # 读取待分类数据
    # 将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_txt(reviewDataSetPath,'lines')
    # 提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    # classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    # 装载分类器
    clf = pickle.load(open(classifierPath))
    dataItemCount = len(sentiment_review)
    # 分类之预测数据类标签
    data_tag = clf.batch_classify(review_feature)
    # 分类之预测数据积极、消极可能性
    res_pro = clf.batch_prob_classify(review_feature)
    preResFile = xlwt.Workbook(encoding='utf-8')
    sheetName='RawDataTagProFea'
    sheetPos=0
    preResSheet = preResFile.add_sheet(sheetName+str(sheetPos))
    posProbility = []
    excelRowPos=0
    for rowPos in range(dataItemCount):
        if excelRowPos==65536:
            sheetPos+=1
            preResSheet=preResFile.add_sheet(sheetName+str(sheetPos))
            excelRowPos=0
        preResSheet.write(excelRowPos, 0, review[rowPos])  # 原始数据
        preResSheet.write(excelRowPos, 1, data_tag[rowPos])  # 类标签
        preResSheet.write(excelRowPos, 2, str(res_pro[rowPos].prob('pos')))  # 积极概率
        posProbility.append(res_pro[rowPos].prob('pos'))
        preResSheet.write(excelRowPos, 3, str(res_pro[rowPos].prob('neg')))  # 消极概率
        feature = ''
        # 特征里面可能出现二元词的情况
        for x in review_feature[rowPos].keys():
            if type(x) is not nltk.types.TupleType:
                feature += x
            else:
                feature += '_'.join(x)
            feature += ' '
        preResSheet.write(excelRowPos, 4, feature)  # 特征
        excelRowPos+=1
    preResFile.save(preDataResPath)
    end = time.clock()
    print 'handle sentences num:', dataItemCount, ' classify time:', end - start
    return posProbility,preDataResPath,review
def predictFromPosTxtDataSentTagProToExcel(windowSize,reviewDataSetPath,preDataResPath,last_pos):
    # reviewDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    # preDataResPath = desDir + '/' + reviewDataSetName + 'RawDataTagProFea.xls'
    start = time.clock()
    review,cur_pos = tp.get_txt_data_from_pos(windowSize,reviewDataSetPath, "lines",last_pos)  # 读取待分类数据
    # 将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_sentences(review)
    # 提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    # classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    # 装载分类器
    clf = pickle.load(open(classifierPath))
    dataItemCount = len(sentiment_review)
    # 分类之预测数据类标签
    data_tag = clf.batch_classify(review_feature)
    # 分类之预测数据积极、消极可能性
    res_pro = clf.batch_prob_classify(review_feature)
    preResFile = xlwt.Workbook(encoding='utf-8')
    sheetName='RawDataTagProFea'
    sheetPos=0
    preResSheet = preResFile.add_sheet(sheetName+str(sheetPos))
    posProbility = []
    excelRowPos=0
    for rowPos in range(dataItemCount):
        if excelRowPos==65536:
            sheetPos+=1
            preResSheet=preResFile.add_sheet(sheetName+str(sheetPos))
            excelRowPos=0
        preResSheet.write(excelRowPos, 0, review[rowPos])  # 原始数据
        preResSheet.write(excelRowPos, 1, data_tag[rowPos])  # 类标签
        preResSheet.write(excelRowPos, 2, str(res_pro[rowPos].prob('pos')))  # 积极概率
        posProbility.append(res_pro[rowPos].prob('pos'))
        preResSheet.write(excelRowPos, 3, str(res_pro[rowPos].prob('neg')))  # 消极概率
        feature = ''
        # 特征里面可能出现二元词的情况
        for x in review_feature[rowPos].keys():
            if type(x) is not nltk.types.TupleType:
                feature += x
            else:
                feature += '_'.join(x)
            feature += ' '
        preResSheet.write(excelRowPos, 4, feature)  # 特征
        excelRowPos+=1
    preResFile.save(preDataResPath)
    end = time.clock()
    print 'handle sentences num:', dataItemCount, ' classify time:', end - start
    return posProbility,preDataResPath,review,cur_pos
'''原始数据格式为excel,将原始数据 类标签 分类概率 原始数据特征写入excel文件中'''
'''返回：评论的积极可能性列表'''
def predictExcelDataSentTagProToExcel(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,sheetNum,colNum,desDir):
    reviewDataSetPath=reviewDataSetDir+'/'+reviewDataSetName+reviewDataSetFileType
    preDataResPath=desDir+'/'+reviewDataSetName+'RawDataTagProFea.xls'
    start=time.clock()
    review = tp.get_excel_data(reviewDataSetPath, sheetNum, colNum, "data")# 读取待分类数据
    #将待分类数据进行分词以及去停用词处理
    sentiment_review = tp.seg_fil_senti_excel(reviewDataSetPath, sheetNum, colNum, 'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    #提取待分类数据特征
    review_feature = extract_features(sentiment_review, best_words)
    #classifierPath = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature/sentiment_classifier.pkl'
    classifierPath = 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + str(best_classifier)[0:15] + '.pkl'
    #装载分类器
    clf = pickle.load(open(classifierPath))
    dataItemCount=len(sentiment_review)
    #分类之预测数据类标签
    data_tag=clf.batch_classify(review_feature)
    #分类之预测数据积极、消极可能性
    res_pro = clf.batch_prob_classify(review_feature)
    # 记录分类结果 积极可能性 消极可能性
    # 记录原始数据
    # 记录原始数据特征提取结果
    # for d in review_feature:
    #     for w,b,in d.iteritems():
    #         p_file.write(w.encode('utf-8') + ' '+str(b)+'\t')
    #     p_file.write('\n')
    # p_file.close()
    preResFile=xlwt.Workbook(encoding='utf-8')
    preResSheet=preResFile.add_sheet('RawDataTagProFea')
    posProbility=[]
    for rowPos in range(dataItemCount):
        preResSheet.write(rowPos,0,review[rowPos])#原始数据
        preResSheet.write(rowPos,1,data_tag[rowPos])#类标签
        preResSheet.write(rowPos,2,str(res_pro[rowPos].prob('pos')))#积极概率
        posProbility.append(res_pro[rowPos].prob('pos'))
        preResSheet.write(rowPos, 3, str(res_pro[rowPos].prob('neg')))#消极概率
        feature=''
        #feature='_'.join(review_feature[rowPos].keys())
       # print type(review_feature[rowPos].keys()),
        # 特征里面可能出现二元词的情况
        for x in review_feature[rowPos].keys():
            if type(x) is not nltk.types.TupleType:
                feature+=x
            else:
                feature+='_'.join(x)
            feature+=' '
        preResSheet.write(rowPos, 4, feature)#特征
    preResFile.save(preDataResPath)
    end=time.clock()
    print 'handle sentences num:', dataItemCount, ' classify time:', end-start
    return posProbility,preDataResPath,review
# reviewDataSetDir='D:/ReviewHelpfulnessPrediction\LabelReviewData'
# reviewDataSetName='test'
# reviewDataSetFileType='.xls'
# desDir='D:/ReviewHelpfulnessPrediction\ReviewDataFeature'
# posProbility,resSavePath,rawReview=predictExcelDataSentTagProToExcel(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,2,1,desDir)


'''绘制积极可能性波动动态曲线图 参数：积极可能性列表 时间间隔 窗口大小'''
def drawPosProbilityChangeLine(posProbility,timeInterval,windowSize):
    posProbilityLen=len(posProbility)
    fig = plt.figure()
    ax = plt.axes(xlim=(0, windowSize+1), ylim=(0, 1))
    line, = ax.plot([], [], lw=2)
    # initialization function: plot the background of each frame
    def init():
        line.set_data([], [])
        return line,
    # animation function. This is called sequentially
    # note: i is framenumber
    def animate(i):
        x = range(1, windowSize+1)
        y = posProbility[i:i + windowSize]
        line.set_data(x, y)
        return line,

    # call the animator. blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=posProbilityLen - windowSize, interval=timeInterval, blit=False)
    # anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
    plt.show()
'''绘制情感波动动态曲线图 参数：积极可能性列表 时间间隔 窗口大小 最小的情感值 最大的情感值'''
def drawSentimentChangeLine(posProbility,timeInterval,windowSize,minSentimentValue,maxSentimentValue):
    posProbilityLen=len(posProbility)
    fig = plt.figure()
    ax = plt.axes(xlim=(0, windowSize+1), ylim=(minSentimentValue, maxSentimentValue))
    line, = ax.plot([], [], lw=2)
    # initialization function: plot the background of each frame
    def init():
        line.set_data([], [])
        return line,
    # animation function. This is called sequentially
    # note: i is framenumber
    def animate(i):
        x = range(1, windowSize+1)
        y = posProbility[i:i + windowSize]
        line.set_data(x, y)
        return line,

    # call the animator. blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=posProbilityLen - windowSize, interval=timeInterval, blit=False)
    # anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
    plt.show()
'''绘制情感曲线图 并将图表保存在dstpath下'''
def drawSentimentLine(sentimentValueList,dstpath):
    plt.figure()
    x=range(1,len(sentimentValueList)+1)
    plt.plot(x,sentimentValueList)
    plt.title('Sentiment Curve Figure')
    plt.xlabel('Sentence Number')
    plt.ylabel('Sentiment Score')
    plt.savefig(dstpath)
'''绘制积极比率、消极比率饼状图'''
def drawPosNegRatioPie(posRatio,negRatio,dstpath):
    labels = 'Postive Ratio', 'Negtive Ratio', 'Objective Ratio'
    fracs = [posRatio, negRatio, 1-posRatio-negRatio]
    explode = [0, 0.1, 0]  # 0.1 凸出这部分，
    plt.axes(aspect=1)  # set this , Figure is round, otherwise it is an ellipse
    # autopct ，show percet
    plt.pie(x=fracs, labels=labels, explode=explode, autopct='%3.1f %%',
            shadow=True, labeldistance=1.1, startangle=90, pctdistance=0.6)
    plt.savefig(dstpath)

'''分析下积极情感可能性数据 '''
'''将数据拆分成windowSize片段，分析每一片段的总体情感，积极比率，消极比率'''
'''参数：积极可能性列表 窗口大小 积极边界 消极边界 异常情感得分边界'''
'''返回 情感得分列表 积极所占比率列表 消极所占比率列表 异常话语所在位置列表'''
def analyzeSentimentProList(posProbility,windowSize,posBounder,negBounder,strangeSentValueBounder):
    posProbilityLen=len(posProbility)
    posRatioList=[]
    negRatioList=[]
    sentimentValueList=[]
    strangeWordPos=[]
    if posProbilityLen>windowSize:
        upBounder=posProbilityLen-windowSize
        posNum = 0
        negNum = 0
        sentimentValue = 0
        for pos in range(0,windowSize):
            if posProbility[pos] <= negBounder:
                negNum += 1
                # sentimentValue-=1
                sentimentValue -= (negBounder - posProbility[pos]) / negBounder  # 根据消极可能性设置得分权重
            elif posProbility[pos] >= posBounder:
                posNum += 1
                # sentimentValue+=1
                sentimentValue += (posProbility[pos] - posBounder) / (1 - posBounder)
        posRatio=float(posNum)/float(windowSize)
        negRatio=float(negNum)/float(windowSize)
        posRatioList.append(posRatio)
        negRatioList.append(negRatio)
        sentimentValueList.append(sentimentValue)
        if sentimentValue<strangeSentValueBounder:
            strangeWordPos.append([0,windowSize-1,sentimentValue])
        for pos in range(windowSize,posProbilityLen):
            frontProbility=posProbility[pos-windowSize]
            '''减去最前面一个数'''
            if frontProbility <= negBounder:
                negNum -= 1
                # sentimentValue-=1
                sentimentValue += (negBounder - frontProbility) / negBounder  # 根据消极可能性设置得分权重
            elif frontProbility >= posBounder:
                posNum -= 1
                # sentimentValue+=1
                sentimentValue -= (frontProbility - posBounder) / (1 - posBounder)
            '''加上当前数'''
            if posProbility[pos] <= negBounder:
                negNum += 1
                # sentimentValue-=1
                sentimentValue -= (negBounder - posProbility[pos]) / negBounder  # 根据消极可能性设置得分权重
            elif posProbility[pos] >= posBounder:
                posNum += 1
                # sentimentValue+=1
                sentimentValue += (posProbility[pos] - posBounder) / (1 - posBounder)
            posRatio = float(posNum)/float(windowSize)
            negRatio = float(negNum)/float(windowSize)
            posRatioList.append(posRatio)
            negRatioList.append(negRatio)
            sentimentValueList.append(sentimentValue)
            if sentimentValue < strangeSentValueBounder:
                strangeWordPos.append([pos-windowSize+1, pos,sentimentValue])
    else:
        posNum = 0
        negNum = 0
        sentimentValue = 0
        for pos in range(posProbilityLen):
            if posProbility[pos] <= negBounder:
                negNum += 1
                # sentimentValue-=1
                sentimentValue -= (negBounder - posProbility[pos]) / negBounder  # 根据消极可能性设置得分权重
            elif posProbility[pos] >= posBounder:
                posNum += 1
                # sentimentValue+=1
                sentimentValue += (posProbility[pos] - posBounder) / (1 - posBounder)
        posRatio = float(posNum) / float(posProbilityLen)
        negRatio = float(negNum) / float(posProbilityLen)
        posRatioList.append(posRatio)
        negRatioList.append(negRatio)
        sentimentValueList.append(sentimentValue)
        if sentimentValue < strangeSentValueBounder:
            strangeWordPos.append([0, posProbilityLen-1,sentimentValue])
    return sentimentValueList,posRatioList,negRatioList,strangeWordPos
'''得到情感积极可能性平均子 数据可能会越界'''
def getMeanSentimentValue(posProbility):
    begin=time.clock()
    sentimentValue=0
    for x in posProbility:
        sentimentValue+=x
    end=time.clock()
    print 'calculate mean sentiment value time is:',end-begin
    return sentimentValue/len(posProbility)
'''得到整体积极比率'''
def getOverallPosRatio(posProbility,posBounder):
    begin=time.clock()
    posNum=0
    for x in posProbility:
        if x>=posBounder:
            posNum+=1
    end=time.clock()
    print 'calculate overall postive ratio time is:',end-begin
    return float(posNum)/len(posProbility)
'''得到整体消极比率'''
def getOverallNegRatio(posProbility,negBounder):
    begin=time.clock()
    negNum=0
    for x in posProbility:
        if x<=negBounder:
            negNum+=1
    end=time.clock()
    print 'calculate overall negtive ratio time is:',end-begin
    return float(negNum)/len(posProbility)
'''合并异常情感'''
def unionStrangeWordPos(strangeWordPos):
    finalStrangeWordPos=[]
    if len(strangeWordPos)<=0:
        return finalStrangeWordPos
    else:
        lastWordPos=strangeWordPos[0]
        count=1
        for pos in range(1,len(strangeWordPos)):
            if(strangeWordPos[pos][0]<=lastWordPos[1]):
                lastWordPos[1]=strangeWordPos[pos][1]
                lastWordPos[2]=(lastWordPos[2]*count+strangeWordPos[pos][2])/(count+1)
                count+=1
            else:
                finalStrangeWordPos.append(lastWordPos)
                lastWordPos=strangeWordPos[pos]
                count=1
        finalStrangeWordPos.append(lastWordPos)
        return finalStrangeWordPos
'''输出异常话语所在的位置 原始数据保存在excel文件中'''
def outputStrangeWordPosInExcel(finalStrangeWordPos,resSavePath):
    if len(finalStrangeWordPos)==0:
        print 'no strange sentences or strange sentences sentiment value set too low'
    else:
        print 'save path:',resSavePath
        for x in finalStrangeWordPos:
            startSheetNum = x[0] / 65536
            startRowNum = x[0] % 65536 + 1
            endSheetNum = x[1] / 65536
            endRowNum = x[1] % 65536 + 1
            print 'sheet ',startSheetNum,' row ',startRowNum,'-- sheet ',endSheetNum,' row ',endRowNum,'(',x[2],')','may have some strange sentences'
'''输出异常话语所在的位置 原始数据保存在txt文件中'''
def outputStrangeWordPosInTxt(finalStrangeWordPos,resSavePath):
    if len(finalStrangeWordPos)==0:
        print 'no strange sentences or strange sentences sentiment value set too low'
    else:
        print 'save path:',resSavePath
        for x in finalStrangeWordPos:
            print 'row ',x[0],'-- row ',x[1],'(',x[2],')','may have some strange sentences'

'''输出异常话语'''
def outputStrangeWords(finalStrangeWordPos,rawReview):
    for x in finalStrangeWordPos:
        for pos in range(x[0],x[1]+1):
            print rawReview[pos],'\t',
        print ''

'''保存异常话语到txt中'''
'''保存路径格式：特定目录+直播房间（ID或NAME）+指定时间'''
def saveStrangeWordsToTxt(finalStrangeWordPos,rawReview,savePath):
    if len(finalStrangeWordPos)==0:
        return 0
    f = open(savePath, 'w')
    f.write(str(len(finalStrangeWordPos))+'\n')
    for x in finalStrangeWordPos:
        f.write('...........................................................................\n')
        for pos in range(x[0],x[1]+1):
            f.write(rawReview[pos].encode('utf-8')+'\n')
    f.close()
    return 1



'''基于机器学习的情感分析 sentiment Analyze based machine learning running time: 17.5400478691 handle review num: 87642'''
'''参数：原始数据名称 原始数据文件格式 窗口大小 积极边界 消极边界 情感得分边界'''
def sentiAnalyzeBaseML(reviewDataSetName,reviewDataSetFileType,windowSize,posBounder,negBounder,sentScoreBounder,timeInterval=20):
    begin=time.clock()
    #reviewDataSetDir = 'D:/ReviewHelpfulnessPrediction\BulletData'
    reviewDataSetDir = 'D:/crambData\crambData2'
    #reviewDataSetName = 'lsj'
    #reviewDataSetFileType = '.log'
    desDir = 'D:/ReviewHelpfulnessPrediction\PredictClassRes'
    figDir = 'D:/ReviewHelpfulnessPrediction\SentimentLineFig'
    strangeWordDir='D:/ReviewHelpfulnessPrediction\StrangeWords'
    curTime=time.strftime('%Y.%m.%d.%H.%M.%S',time.localtime(time.time()))
    rawDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    strangeWordPath=strangeWordDir+'/'+reviewDataSetName+str(curTime)+'ML.txt'
    classifyResPath=desDir + '/' + reviewDataSetName+str(curTime) + 'ML.xls'

    posProbility, resSavePath, rawReview = predictTxtDataSentTagProToExcel(rawDataSetPath,classifyResPath)
    sentimentValueList, posRatioList, negRatioList, strangeWordPos = analyzeSentimentProList(posProbility, windowSize,
                                                                                             posBounder, negBounder,
                                                                                             sentScoreBounder)
    meanSentPosPro = getMeanSentimentValue(posProbility)
    overallPosRatio = getOverallPosRatio(posProbility, posBounder)
    overallNegRatio = getOverallNegRatio(posProbility, negBounder)
    print 'mean sentiment postive probility', meanSentPosPro
    finalStrangeWordPos = unionStrangeWordPos(strangeWordPos)
    #outputStrangeWordPosInExcel(finalStrangeWordPos, resSavePath)
    sentimentLinePath=figDir + '/' + reviewDataSetName +str(curTime)+ 'SCML.png'
    drawSentimentLine(sentimentValueList, sentimentLinePath)
    posNegRatioPath=figDir + '/' + reviewDataSetName+str(curTime) + 'PNRML.png'
    drawPosNegRatioPie(overallPosRatio, overallNegRatio, posNegRatioPath)
    #outputStrangeWords(finalStrangeWordPos, rawReview)
    saveStrangeWordsToTxt(finalStrangeWordPos,rawReview,strangeWordPath)

    #drawSentimentChangeLine(sentimentValueList, timeInterval, windowSize, -60, 60)
    end=time.clock()
    print 'sentiment Analyze based machine learning running time:',end-begin,'handle review num:',len(rawReview)

def sentiAnalyzeBaseMLFromPos(lastPos,childDir,reviewDataSetName,reviewDataSetFileType,windowSize,posBounder,negBounder,sentScoreBounder,timeInterval=20):
    begin=time.clock()
    #reviewDataSetDir = 'D:/ReviewHelpfulnessPrediction\BulletData'
    reviewDataSetDir = 'D:/crambData/'+childDir
    #reviewDataSetName = 'lsj'
    #reviewDataSetFileType = '.log'
    desDir = 'D:/ReviewHelpfulnessPrediction\PredictClassRes'
    figDir = 'D:/ReviewHelpfulnessPrediction\SentimentLineFig'
    strangeWordDir='D:/ReviewHelpfulnessPrediction\StrangeWords'
    curTime=time.strftime('%Y.%m.%d.%H.%M.%S',time.localtime(time.time()))
    rawDataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
    strangeWordPath=strangeWordDir+'/'+childDir+reviewDataSetName+str(curTime)+'ML.txt'
    classifyResPath=desDir + '/' + childDir+reviewDataSetName+str(curTime) + 'ML.xls'

    posProbility, resSavePath, rawReview,curPos = predictFromPosTxtDataSentTagProToExcel(windowSize,rawDataSetPath,classifyResPath,lastPos)
    sentimentValueList, posRatioList, negRatioList, strangeWordPos = analyzeSentimentProList(posProbility, windowSize,
                                                                                             posBounder, negBounder,
                                                                                             sentScoreBounder)
    meanSentPosPro = getMeanSentimentValue(posProbility)
    overallPosRatio = getOverallPosRatio(posProbility, posBounder)
    overallNegRatio = getOverallNegRatio(posProbility, negBounder)
    print 'mean sentiment postive probility', meanSentPosPro
    finalStrangeWordPos = unionStrangeWordPos(strangeWordPos)
    #outputStrangeWordPosInExcel(finalStrangeWordPos, resSavePath)
    sentimentLinePath=figDir + '/' + childDir+reviewDataSetName +str(curTime)+ 'SCML.png'
    drawSentimentLine(sentimentValueList, sentimentLinePath)
    posNegRatioPath=figDir + '/' + childDir+reviewDataSetName+str(curTime) + 'PNRML.png'
    drawPosNegRatioPie(overallPosRatio, overallNegRatio, posNegRatioPath)
    #outputStrangeWords(finalStrangeWordPos, rawReview)
    saveStrangeWordsToTxt(finalStrangeWordPos,rawReview,strangeWordPath)

    #drawSentimentChangeLine(sentimentValueList, timeInterval, windowSize, -60, 60)
    end=time.clock()
    print 'sentiment Analyze based machine learning running time:',end-begin,'handle review num:',len(rawReview)
    return curPos

'''每隔多长时间处理一次 timeSize/s'''
'''产生结果数据堆积 硬盘爆 适时删除'''
'''读取数据发生冲突'''
'''在wait时删除之前数据'''
'''抓取一些新的数据'''
def handleMutiRoomInfo(timeSize,childDirList,reviewDataSetNameList,reviewDataSetFileType,windowSize,posBounder,negBounder,sentScoreBounder,timeInterval=20):
    lastPosList=[]
    for p in range(len(reviewDataSetNameList)):
        lastPosList.append(windowSize)
    while True:
        begin=time.clock()
        for pos in range(len(reviewDataSetNameList)):
            lastPosList[pos]=sentiAnalyzeBaseMLFromPos(lastPosList[pos]-windowSize,childDirList[pos],reviewDataSetNameList[pos],reviewDataSetFileType,windowSize,posBounder,negBounder,sentScoreBounder,timeInterval)
        while time.clock()-begin<timeSize:
            pass

#sentiAnalyzeBaseML('lsj','.log',100,0.6,0.4,-60)

if __name__=='__main__':
    handleMutiRoomInfo(120,['crambData2','crambData3'],['output3','output3'],'.txt',50,0.6,0.4,-40)

'''整体评价 正确率较高 运行速度较快 handle sentences num: 87642  classify time: 18.191449251'''

