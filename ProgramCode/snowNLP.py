#! /usr/bin/env python2.7
#coding=utf-8
from snownlp import SnowNLP
import time
import random
import textProcessing as tp

def storeReviewSenValue(dataSetDir,dataSetName,dataSetFileType,sheetNum,colNum,dstDir):
    start=time.clock()
    dataSetPath = dataSetDir + '/' + dataSetName + dataSetFileType
    dstPath = dstDir + '/' + dataSetName + 'SnowNLPSentiment.txt'
    reviewSet=tp.get_excel_data(dataSetPath,sheetNum,colNum,'data')
    reviewSentiment=[]
    for review in reviewSet:
        s=SnowNLP(review)
        reviewSentiment.append(s.sentiments)
    reviewNum=0
    f=open(dstPath,'w')
    for x in reviewSentiment:
        f.write(str(x)+'\n')
        reviewNum+=1
    f.close()
    end=time.clock()
    return reviewNum,end-start

'''注意SnowNLP('') 不能处理空字符串，应把这种空字符串剔除掉'''
def storeTxtReviewSenValue(dataSetDir,dataSetName,dataSetFileType,dstDir):
    start=time.clock()
    dataSetPath = dataSetDir + '/' + dataSetName + dataSetFileType
    dstPath = dstDir + '/' + dataSetName + 'SnowNLPSentiment.txt'
    reviewSet=tp.get_txt_data(dataSetPath,'lines')
    reviewSentiment=[]
    rawReview=[]
    for review in reviewSet:
        if review=='':
            continue
        s=SnowNLP(review)
        rawReview.append(review)
        reviewSentiment.append(s.sentiments)
    reviewNum=0
    f=open(dstPath,'w')
    for pos in range(len(reviewSentiment)):
        f.write(str(rawReview[pos].encode('utf-8'))+'\t'+str(reviewSentiment[pos])+'\n')
        reviewNum+=1
    f.close()
    end=time.clock()
    return reviewNum,end-start


# reviewDataSetDir='D:/ReviewHelpfulnessPrediction\ReviewSet'
# reviewDataSetName='HTC_Z710t_review_2013.6.5'
# reviewDataSetFileType='.xlsx'
# desDir='D:/ReviewHelpfulnessPrediction\ReviewDataFeature'
# recordNum,runningTime=storeReviewSenValue(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,1,5,desDir)
# #recordNum,runningTime=storeReviewSenValue("D:\ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet",'neg_review','.xlsx', 1,1,'D:/ReviewHelpfulnessPrediction\ReviewDataFeature')
# print 'handle sentences num:',recordNum,' running time:',runningTime

reviewDataSetDir='D:/ReviewHelpfulnessPrediction\BulletData'
reviewDataSetName='lsj'
reviewDataSetFileType='.log'
desDir='D:/ReviewHelpfulnessPrediction\PredictClassRes'
recordNum,runningTime=storeTxtReviewSenValue(reviewDataSetDir,reviewDataSetName,reviewDataSetFileType,desDir)
print 'handle sentences num:',recordNum,' running time:',runningTime
