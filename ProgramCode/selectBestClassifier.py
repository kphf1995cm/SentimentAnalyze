#! /usr/bin/env python2.7
#coding=utf-8
''''''
'''
使用积极和消极的评论作为语料库训练一个情感分类器
使用了带标记的评论作为训练集
'''
'''
                                           注意事项
如果训练数据（标记数据）发生更改，需要修改posNegDir ，pos_review，neg_review，使得pos_review，neg_review指向标注的积极以及消极评论
最佳分类器 最佳维度保存在D:/ReviewHelpfulnessPrediction\BuildedClassifier/'+'bestClassifierDimenAcc.txt目录下
'''

import textProcessing as tp
import pickle
import itertools
from random import shuffle

import nltk
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

import sklearn
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import RadiusNeighborsClassifier
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.neural_network import MLPClassifier


'''1 导入数据模块'''

posNegDir = 'D:/ReviewHelpfulnessPrediction\LabelReviewData'
pos_review = tp.seg_fil_senti_excel(posNegDir + '/posNegLabelData.xls', 1, 1, 'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
neg_review = tp.seg_fil_senti_excel(posNegDir + '/posNegLabelData.xls', 2, 1, 'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
print 'postive review num is:',len(pos_review),'negtive review num is:',len(neg_review)

shuffle(pos_review)
shuffle(neg_review)

pos = pos_review
neg = neg_review


"""
# Cut positive review to make it the same number of nagtive review (optional)

shuffle(pos_review)
size = int(len(pos_review)/2 - 18)

pos = pos_review[:size]
neg = neg_review

"""


'''2 特征提取模块'''
'''
方式1：使用全部词语 或 二元词语 或 词语+二元词语 作为特征（不推荐使用）
'''
def bag_of_words(words):
    return dict([(word, True) for word in words])
def bigrams(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return bag_of_words(bigrams)
def bigram_words(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return bag_of_words(words + bigrams)
def get_all_words():
    posdata = pos_review
    negdata = neg_review
    posWords = list(itertools.chain(*posdata))
    negWords = list(itertools.chain(*negdata))
    return posWords+negWords

'''
方式2：降维处理，选取信息量大的 词语或二元词语或词语+二元词语 作为特征
'''
'''
方式2的步骤一：计算单个词语 二元词语 单个词语+二元词语 的信息得分
              注意点 引用了导入数据模块的全局变量 pos_review和neg_review
'''
def create_word_scores():
    # posNegDir = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet'
    # posdata = tp.seg_fil_senti_excel(posNegDir + '/pos_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    # negdata = tp.seg_fil_senti_excel(posNegDir + '/neg_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    posdata=pos_review
    negdata=neg_review

    posWords = list(itertools.chain(*posdata))
    negWords = list(itertools.chain(*negdata))

    word_fd = FreqDist()
    cond_word_fd = ConditionalFreqDist()
    for word in posWords:
        word_fd[word] += 1
        cond_word_fd['pos'][word] += 1
    for word in negWords:
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
def create_bigram_scores():
    # posNegDir = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet'
    # posdata = tp.seg_fil_senti_excel(posNegDir + '/pos_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    # negdata = tp.seg_fil_senti_excel(posNegDir + '/neg_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    posdata = pos_review
    negdata = neg_review

    posWords = list(itertools.chain(*posdata))
    negWords = list(itertools.chain(*negdata))

    bigram_pos_finder = BigramCollocationFinder.from_words(posWords)
    posBigrams = bigram_pos_finder.nbest(BigramAssocMeasures.chi_sq, 8000)
    bigram_neg_finder = BigramCollocationFinder.from_words(negWords)
    negBigrams = bigram_neg_finder.nbest(BigramAssocMeasures.chi_sq, 8000)

    pos = posBigrams
    neg = negBigrams

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
def create_word_bigram_scores():
    # posNegDir = 'D:/ReviewHelpfulnessPrediction\FeatureExtractionModule\SentimentFeature\MachineLearningFeature\SenimentReviewSet'
    # posdata = tp.seg_fil_senti_excel(posNegDir + '/pos_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    # negdata = tp.seg_fil_senti_excel(posNegDir + '/neg_review.xlsx', 1, 1,
    #                                  'D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt')
    posdata = pos_review
    negdata = neg_review

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

'''word_scores 作为全局变量，其是字典类型，表示每个词语的信息得分 {词语：得分，}'''
word_scores = create_word_bigram_scores()
#word_scores=create_word_scores()

'''
方式2的步骤二：根据信息量得分进行排序，选取排名靠前的number个作为特征
'''
def find_best_words(number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words
def sort_word_score():
    words=sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)
    return words

# '''best_words 作为全局变量，其实列表类型，表示所挑选出的信息量最高词语特征 [词语1，词语2] 参数1500表示最佳特征数量'''
# best_words=find_best_words(1500)

'''
提取出一句话里面所含有的特征
三种形式：单个词 二元词 单个词+二元词
'''
def best_word_features(words,best_words):
    return dict([(word, True) for word in words if word in best_words])
def best_word_features_bi(words,best_words):
    return dict([(word, True) for word in nltk.bigrams(words) if word in best_words])
def best_word_features_com(words,best_words):
    d1 = dict([(word, True) for word in words if word in best_words])
    d2 = dict([(word, True) for word in nltk.bigrams(words) if word in best_words])
    d3 = dict(d1, **d2)
    return d3


'''3 获取规范化数据模块'''
'''提取积极评论以及消极评论数据特征以及类标签，将每条评论表示为 特征，类标签 列表形式 [{word1：score1，}，tag]'''
'''使用全局变量pos_review,neg_review'''
def pos_features(feature_extraction_method,best_words):
    posFeatures = []
    for i in pos_review:
        posWords = [feature_extraction_method(i,best_words),'pos']
        posFeatures.append(posWords)
    return posFeatures
def neg_features(feature_extraction_method,best_words):
    negFeatures = []
    for j in neg_review:
        negWords = [feature_extraction_method(j,best_words),'neg']
        negFeatures.append(negWords)
    return negFeatures

'''
构建训练集和测试集 8:2 比例
参数 维度dimension 决定了best_words,进而决定每个评论里面所包含的特征
返回 积极训练数据 消极训练数据 测试数据特征 测试数据类标签
'''
def get_trainset_testset_testtag(dimension):
    best_words=find_best_words(dimension)
    posFeatures = pos_features(best_word_features_com,best_words) #提取积极文本里面的数据
    negFeatures = neg_features(best_word_features_com,best_words) #提取消极文本里面的数据
    # shuffle(posFeatures)  # 将序列的所有元素随机排列
    # shuffle(negFeatures)
    train_pos = int(len(pos_review) * 0.8)
    train_neg = int(len(neg_review) * 0.8)
    train_set_pos = posFeatures[:train_pos]
    train_set_neg = negFeatures[:train_neg]
    test_set=posFeatures[train_pos:] + negFeatures[train_neg:]
    test_fea,test_tag=zip(*test_set) # 将特征和类标签分离开
    return train_set_pos,train_set_neg,test_fea,test_tag

'''将训练数据划分成开发训练集 以及开发测试集 比例为8:2'''
def get_dev_train_test_data(train_set_pos,train_set_neg):
    shuffle(train_set_pos)  # 将序列的所有元素随机排列
    shuffle(train_set_neg)
    train_pos = int(len(train_set_pos) * 0.8)
    train_neg = int(len(train_set_neg) * 0.8)
    train_set = train_set_pos[:train_pos] + train_set_neg[:train_neg]
    test_set=train_set_pos[train_pos:] + train_set_neg[train_neg:]
    test_fea,test_tag=zip(*test_set) # 将特征和类标签分离开
    return train_set,test_fea,test_tag


'''
构建训练集 选取 单词+二元词形式
将所有数据作为训练数据
'''
def get_trainset(dimension):
    best_words=find_best_words(dimension) #排序 挑前dimension个
    posFeatures = pos_features(best_word_features_com,best_words) #提取积极文本里面的数据
    negFeatures = neg_features(best_word_features_com,best_words) #提取消极文本里面的数据
    shuffle(posFeatures)  # 将序列的所有元素随机排列
    shuffle(negFeatures)
    size_pos = int(len(pos_review))
    size_neg = int(len(neg_review))
    train_set = posFeatures[:size_pos] + negFeatures[:size_neg]
    return train_set


'''4 训练分类器，并且评估分类效果'''

# train_set,test,tag_test=get_trainset_testset_testtag(1500)
# def clf_score(classifier):
#     classifier = SklearnClassifier(classifier)
#     classifier.train(train_set)
#     predict = classifier.batch_classify(test)
#     return accuracy_score(tag_test, predict)
#
# print 'BernoulliNB`s accuracy is %f' %clf_score(BernoulliNB())
# #print 'GaussianNB`s accuracy is %f' %clf_score(GaussianNB())
# print 'MultinomiaNB`s accuracy is %f' %clf_score(MultinomialNB())
# print 'LogisticRegression`s accuracy is %f' %clf_score(LogisticRegression())
# print 'SVC`s accuracy is %f' %clf_score(SVC(gamma=0.001, C=100., kernel='linear'))
# print 'LinearSVC`s accuracy is %f' %clf_score(LinearSVC())
# print 'NuSVC`s accuracy is %f' %clf_score(NuSVC())



# 5. After finding the best classifier, then check different dimension classification accuracy

'''获取分类器精度'''
def get_accuracy_score(classifier,train_set,test,tag_test):
    classifier = SklearnClassifier(classifier)
    classifier.train(train_set)
    pred = classifier.batch_classify(test)
    return accuracy_score(tag_test, pred,'macro')#积极类 消极类精度加权平均值
    #return accuracy_score(tag_test, pred)#只考虑积极类精度
'''
  挑选出最佳分类器以及最优特征维度
  返回分类器 维度 精度
  分类结果保存在 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + 'classifierDimenAcc.txt'
'''
def get_best_classfier_and_dimention():
    bestClassfier = ''
    bestDimention = '0'
    curAccuracy = 0.0
    dimention = range(500, 3100, 200)
    for d in dimention:
        train_set_pos, train_set_neg, test_fea, test_tag=get_trainset_testset_testtag(int(d))
        trainset,test,tag_test=get_dev_train_test_data(train_set_pos,train_set_neg)
        BernoulliNBScore=get_accuracy_score(BernoulliNB(),trainset,test,tag_test)
        MultinomialNBScore=get_accuracy_score(MultinomialNB(),trainset,test,tag_test)
        LogisticRegressionScore=get_accuracy_score(LogisticRegression(),trainset,test,tag_test)
        SVCScore=get_accuracy_score(SVC(),trainset,test,tag_test)
        LinearSVCScore=get_accuracy_score(LinearSVC(),trainset,test,tag_test)
        NuSVCScore=get_accuracy_score(NuSVC(probability=True),trainset,test,tag_test)
        if BernoulliNBScore>curAccuracy:
            curAccuracy=BernoulliNBScore
            bestClassfier=BernoulliNB()
            bestDimention=d
        if MultinomialNBScore>curAccuracy:
            curAccuracy=MultinomialNBScore
            bestClassfier=MultinomialNB()
            bestDimention=d
        if LogisticRegressionScore>curAccuracy:
            curAccuracy=LogisticRegressionScore
            bestClassfier=LogisticRegression()
            bestDimention=d
        if SVCScore>curAccuracy:
            curAccuracy=SVCScore
            bestClassfier=SVC()
            bestDimention=d
        if LinearSVCScore>curAccuracy:
            curAccuracy=LinearSVCScore
            bestClassfier=LinearSVC()
            bestDimention=d
        if NuSVCScore>curAccuracy:
            curAccuracy=NuSVCScore
            bestClassfier=NuSVC()
            bestDimention=d
        classifierNameList=['BernoulliNB()'.decode('utf-8'),'MultinomialNB()'.decode('utf-8'),'LogisticRegression()'.decode('utf-8'),'SVC()'.decode('utf-8'),'LinearSVC()'.decode('utf-8'),'NuSVC()'.decode('utf-8')]
        classifierAccList=[str(BernoulliNBScore).decode('utf-8'),str(MultinomialNBScore).decode('utf-8'),str(LogisticRegressionScore).decode('utf-8'),str(SVCScore).decode('utf-8'),str(LinearSVCScore).decode('utf-8'),str(NuSVCScore).decode('utf-8')]
        f = open('D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + 'classifierDimenAcc.txt', 'a')
        for pos in range(len(classifierAccList)):
            f.write(classifierNameList[pos]+'\t'+str(d).decode('utf-8')+'\t'+classifierAccList[pos]+'\n')
        f.close()
        print 'dimension is',int(d)
        print 'BernoulliNB`s accuracy is %f' % BernoulliNBScore
        print 'MultinomiaNB`s accuracy is %f' % MultinomialNBScore
        print 'LogisticRegression`s accuracy is %f' % LogisticRegressionScore
        print 'SVC`s accuracy is %f' % SVCScore
        print 'LinearSVC`s accuracy is %f' % LinearSVCScore
        print 'NuSVC`s accuracy is %f' % NuSVCScore
        print

    return bestClassfier,bestDimention,curAccuracy


'''
  挑选出最佳分类器以及最优特征维度
  返回分类器 维度 精度
  分类结果保存在 'D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + 'classifierDimenAcc.txt'
'''
def get_best_classfier_and_dimention_2():
    bestClassfier = ''
    bestDimention = '0'
    curAccuracy = 0.0
    dimention = range(500,3100,200)
    classifierMethodList=[BernoulliNB(alpha=0.1),MultinomialNB(alpha=0.1),LogisticRegression(intercept_scaling=0.1),NuSVC(probability=True),KNeighborsClassifier(n_neighbors=6,p=1)]#,MLPClassifier()
    for d in dimention:
        train_set_pos, train_set_neg, test_fea, test_tag=get_trainset_testset_testtag(int(d))
        trainset,test,tag_test=get_dev_train_test_data(train_set_pos,train_set_neg)
        classifierAccList=[]
        for classifierMethod in classifierMethodList:
            accuracyScore=get_accuracy_score(classifierMethod,trainset,test,tag_test)
            classifierAccList.append(accuracyScore)
            if accuracyScore>curAccuracy:
                curAccuracy=accuracyScore
                bestClassfier=classifierMethod
                bestDimention=d
        classifierNameList=['BernoulliNB()','MultinomialNB()','LogisticRegression()','NuSVC()','KNeighborsClassifier()']#,'MLPClassifier()
        f = open('D:/ReviewHelpfulnessPrediction\BuildedClassifier/' + 'classifierDimenAcc.txt', 'a')
        for pos in range(len(classifierAccList)):
            f.write(str(classifierNameList[pos])+'\t'+str(d)+'\t'+str(classifierAccList[pos])+'\n')
        f.close()
        print 'dimension is',int(d)
        for pos in range(len(classifierNameList)):
            print classifierNameList[pos],'accuracy is:',classifierAccList[pos]
    return bestClassfier,bestDimention,curAccuracy

def get_best_parm_of_classifier():
    bestClassfier = ''
    bestDimention = '0'
    curAccuracy = 0.0
    bestParm=0.0
    #dimention = ['500',700, '1000','1300', '1500','1700', '2000','2200', '2500', '3000']
    dimention=range(500,3000,200)
    classifierMethod='KNeighborsClassifier()'
    for d in dimention:
        train_set_pos, train_set_neg, test_fea, test_tag=get_trainset_testset_testtag(int(d))
        trainset,test,tag_test=get_dev_train_test_data(train_set_pos,train_set_neg)
        classifierAccList=[]
        classifierMethodList=[]
        for alphaValue in range(1,3):
            #alphaValue=float(alphaValue)/10
            accuracyScore=get_accuracy_score(KNeighborsClassifier(n_neighbors=6,p=alphaValue),trainset,test,tag_test)
            classifierMethodList.append(KNeighborsClassifier(n_neighbors=6,p=alphaValue))
            classifierAccList.append(accuracyScore)
            if accuracyScore>curAccuracy:
                curAccuracy=accuracyScore
                bestClassfier=KNeighborsClassifier(n_neighbors=6,p=alphaValue)
                bestDimention=d
                bestParm=alphaValue
        f = open('D:/ReviewHelpfulnessPrediction\BuildedClassifier/' +classifierMethod+ 'classifierDimenAcc.txt', 'a')
        for pos in range(len(classifierAccList)):
            f.write(str(classifierMethodList[pos])+'\t'+str(d)+'\t'+str(classifierAccList[pos])+'\n')
        f.close()
        print 'dimension is',int(d)
        for pos in range(len(classifierMethodList)):
            print classifierMethodList[pos],'accuracy is:',classifierAccList[pos]
    print 'best parm is',bestParm
    return bestClassfier,bestDimention,curAccuracy


bestClassfier,bestDimention,bestAccuracy=get_best_classfier_and_dimention_2()
print str(bestClassfier),bestDimention,bestAccuracy
'''存储最佳分类器 最优维度 相应精度'''
'''D:/ReviewHelpfulnessPrediction\BuildedClassifier/'+'bestClassifierDimenAcc.txt'''
def storeClassifierDimenAcc(classifier,dimen,acc):
    f=open('D:/ReviewHelpfulnessPrediction\BuildedClassifier/'+'bestClassifierDimenAcc.txt','w')
    f.write(classifier+'$'+dimen+'$'+acc+'\n');
    f.close()

storeClassifierDimenAcc(str(bestClassfier).decode('utf-8'),str(bestDimention).decode('utf-8'),str(bestAccuracy).decode('utf-8'))

'''存储分类器'''
def store_classifier(clf, trainset, filepath):
    classifier = SklearnClassifier(clf)
    classifier.train(trainset)
    # use pickle to store classifier
    pickle.dump(classifier, open(filepath,'w'))


trainSet=get_trainset(int(bestDimention)) #将所有数据作为训练数据
store_classifier(bestClassfier,trainSet,'D:/ReviewHelpfulnessPrediction\BuildedClassifier/'+str(bestClassfier)[0:15]+'.pkl')
'''根据测试集测试在最佳分类器以及最优特征维度下的分类精度'''
def getFinalClassifyAccuration(classifier,dimension):
    train_set_pos, train_set_neg, test_fea, test_tag = get_trainset_testset_testtag(int(dimension))
    train_set=train_set_pos+train_set_neg
    shuffle(train_set)
    print 'final classify accuracy is:',get_accuracy_score(classifier,train_set,test_fea,test_tag)

getFinalClassifyAccuration(bestClassfier,bestDimention)





