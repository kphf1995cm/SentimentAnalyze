#! /usr/bin/env python2.7
#coding=utf-8
''''''
'''基于词典的情感分析'''
'''
基于词典的情感分析大致步骤如下：
·分解文章段落
·分解段落中的句子
·分解句子中的词汇
·搜索情感词并标注和计数
·搜索情感词前的程度词，根据程度大小，赋予不同权值
·搜索情感词前的否定词，赋予反转权值（-1）
·计算句子的情感得分
·计算段落的情感得分
·计算文章的情感得分
·考虑到语句中的褒贬并非稳定分布，以上步骤对于积极和消极的情感词分开执行，最终的到两个分值，分别表示文本的正向情感值和负向情感值。
'''

import textProcessing as tp
import numpy as np
import time
import xlwt
import xlrd
from matplotlib import pyplot as plt
from matplotlib import animation

'''1 导入情感词典'''
'''导入情感词典'''
begin=time.clock()
dictDir='D:/ReviewHelpfulnessPrediction\SentimentDict'
posdict = tp.get_txt_data(dictDir+"/posdict.txt","lines")
negdict = tp.get_txt_data(dictDir+"/negdict.txt","lines")

'''导入形容词、副词、否定词等程度词字典'''
mostdict = tp.get_txt_data(dictDir+'/most.txt', 'lines')
verydict = tp.get_txt_data(dictDir+'/very.txt', 'lines')
moredict = tp.get_txt_data(dictDir+'/more.txt', 'lines')
ishdict = tp.get_txt_data(dictDir+'/ish.txt', 'lines')
insufficientdict = tp.get_txt_data(dictDir+'/insufficiently.txt', 'lines')
inversedict = tp.get_txt_data(dictDir+'/inverse.txt', 'lines')
end=time.clock()
print 'load dictionary time:',end-begin
'''2 基于字典的情感分析 基本功能'''

'''匹配程度词并设置权重'''
'''parm：word  当前情感词的前面词语 sentiment_value 当前情感词的情感值'''
def match(word, sentiment_value):
	if word in mostdict:
		sentiment_value *= 2.0
	elif word in verydict:
	    sentiment_value *= 1.5
	elif word in moredict:
	    sentiment_value *= 1.25
	elif word in ishdict:
	    sentiment_value *= 0.5
	elif word in insufficientdict:
	    sentiment_value *= 0.25
	elif word in inversedict:
	    sentiment_value *= -1
	return sentiment_value

'''将得分正数化 Example: [5, -2] →  [7, 0]; [-4, 8] →  [0, 12]'''
def transform_to_positive_num(poscount, negcount):
    pos_count = 0
    neg_count = 0
    if poscount < 0 and negcount >= 0:
        neg_count = negcount - poscount #bug
        pos_count = 0
    elif negcount < 0 and poscount >= 0:
        pos_count = poscount - negcount
        neg_count = 0
    elif poscount < 0 and negcount < 0:
        neg_count = -poscount
        pos_count = -negcount
    else:
        pos_count = poscount
        neg_count = negcount
    return [pos_count, neg_count]


'''3 计算评论的情感特征'''

'''计算单条评论的情感特征，单条评论可能还有多个句子 score_list=[[pos1,neg1],[pos2,neg2],]'''
'''返回 [PosSum, NegSum]'''
def sumup_sentence_sentiment_score(score_list):
	score_array = np.array(score_list) # Change list to a numpy array
	Pos = np.sum(score_array[:,0]) # Compute positive score
	Neg = np.sum(score_array[:,1])
	# AvgPos = np.mean(score_array[:,0]) # Compute review positive average score, average score = score/sentence number
	# AvgNeg = np.mean(score_array[:,1])
	# StdPos = np.std(score_array[:,0]) # Compute review positive standard deviation score
	# StdNeg = np.std(score_array[:,1])
	return [Pos, Neg]

# 代码有问题,它是按照情感词个数来计算的，它更强调的是位于后面的情感词
# 计算单条评论情感得分
# input：除了电池不给力 都很好
# output:[1.5, 0.0, 0.75, 0.0, 0.75, 0.0]
# test code:print(single_review_sentiment_score(review[1]))
'''计算单条评论的得分列表 '''
'''返回 [PosSum, NegSum]'''
def single_review_sentiment_score(review):
	single_review_senti_score = []
	cuted_review = tp.cut_sentence_2(review)# 将评论切割成句子

	for sent in cuted_review:
		seg_sent = tp.segmentation(sent, 'list')# 将句子做分词处理
		i = 0 # word position counter
		s = 0 # sentiment word position
		poscount = 0 # count a positive word
		negcount = 0 # count a negative word

		for word in seg_sent:
		    if word in posdict:
		        poscount += 1
		        for w in seg_sent[s:i]:
		           poscount = match(w, poscount)
		        s = i + 1 # a是什么

		    elif word in negdict:
		        negcount += 1
		        for w in seg_sent[s:i]:
		        	negcount = match(w, negcount)
		        s = i + 1 # a是什么

		    # Match "!" in the review, every "!" has a weight of +2 ！强调句子情感
		    elif word == "！".decode('utf8') or word == "!".decode('utf8'):
		        for w2 in seg_sent[::-1]:
		            if w2 in posdict:
		            	poscount += 2
		            	break
		            elif w2 in negdict:
		                negcount += 2
		                break                    
		    i += 1

		single_review_senti_score.append(transform_to_positive_num(poscount, negcount))
		#print(sumup_sentence_sentiment_score(single_review_senti_score))
	review_sentiment_score = sumup_sentence_sentiment_score(single_review_senti_score)

	return review_sentiment_score


'''计算全部评论的情感得分列表'''
'''返回 [[[pos,neg],[pos,neg],],[],]'''
def sentence_sentiment_score(dataset):
    cuted_review = []
    for cell in dataset:
        cuted_review.append(tp.cut_sentence_2(cell))

    all_review_count = []
    for review in cuted_review:
        single_review_count=[]
        if len(review)==0:#出现空行时
			single_review_count.append(transform_to_positive_num(0, 0))
        for sent in review:
            seg_sent = tp.segmentation(sent, 'list')
            i = 0 #word position counter
            a = 0 #sentiment word position
            poscount = 0 #count a pos word
            negcount = 0
            for word in seg_sent:
                if word in posdict:
                    poscount += 1                
                    for w in seg_sent[a:i]:
                       poscount = match(w, poscount)
                    a = i + 1

                elif word in negdict:
                    negcount += 1
                    for w in seg_sent[a:i]:
                    	negcount = match(w, negcount)
                    a = i + 1

                elif word == '！'.decode('utf8') or word == '!'.decode('utf8'):
                    for w2 in seg_sent[::-1]:
                        if w2 in posdict:
                        	poscount += 2
                        	break
                        elif w2 in negdict:
                            negcount += 2
                            break                    
                i += 1
                
            single_review_count.append(transform_to_positive_num(poscount, negcount)) #[[s1_score], [s2_score], ...]
        all_review_count.append(single_review_count) # [[[s11_score], [s12_score], ...], [[s21_score], [s22_score], ...], ...]

    return all_review_count

'''计算全部评论的特征列表'''
'''返回[[PosSum, NegSum],[],]'''
def all_review_sentiment_score(senti_score_list):
    score = []
    for review in senti_score_list:
        score_array = np.array(review)
        Pos = np.sum(score_array[:,0])
        Neg = np.sum(score_array[:,1])
        score.append([Pos, Neg])
    return score

'''返回所有评论的情感得分列表 形式如：[[PosSum, NegSum],[],]'''
def get_review_set_sentiement_score(review):
	start = time.clock()
	pos_neg_score_list = sentence_sentiment_score(review)
	sentiment_score_list =  all_review_sentiment_score(pos_neg_score_list)
	end = time.clock()
	print 'get sentiment score list time is:',end-start,'handle review num is:',len(review)
	return sentiment_score_list

def get_score(num):
    return float(num+1)/float(num+2)
'''pos_score/(pos_score+neg_score)'''
'''得到一句话的整体情感得分，取值在0至1之间 也可看做积极可能性 并将其存储到txt文件中 原始数据 情感得分'''
def get_sentiment_overall_score_to_txt(sentiment_score_list,review,dstpath):
	begin=time.clock()
	sentiment_overall_score=[]
	for x in sentiment_score_list:
		score=0.0
		if x[0]==x[1]:
			score=0.5
		elif x[0]==0 or x[1]==0:
			if x[0]==0:
				score=float((1-get_score(x[1])+1-get_score(x[1]+1)))/2.0
			else:
				score=float(get_score(x[0])+get_score(x[0]+1))/2.0
		else:
			score=float(x[0])/(float(x[0])+float(x[1]))
		sentiment_overall_score.append(score)
	dataItemNum=len(review)
	f=open(dstpath,'w')
	for pos in range(dataItemNum):
		f.write(review[pos].encode('utf-8')+'\t'+str(sentiment_overall_score[pos])+'\n')
	f.close()
	end=time.clock()
	print 'get overall score time is:',end-begin,'handle data item num is:',dataItemNum




	return sentiment_overall_score
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
'''绘制情感曲线图'''
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
    begin=time.clock()
    posProbilityLen=len(posProbility)
    posRatioList=[]
    negRatioList=[]
    sentimentValueList=[]
    strangeWordPos=[]
    if posProbility>windowSize:
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
    end=time.clock()
    print 'analyze sentiment value list time is:',end-begin
    return sentimentValueList,posRatioList,negRatioList,strangeWordPos
'''得到情感积极可能性平均子 数据可能会越界'''
def getMeanSentimentValue(posProbility):
    begin=time.clock()
    sentimentValue=0
    for x in posProbility:
        sentimentValue+=x
    end=time.clock()
    print 'calculate mean sentiment postive probility time is:',end-begin
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
'''得到基于词典情感分析精度'''
def getAccuracy(sentimentValueList,labelClass):
	diffNum=0
	for pos in range(len(sentimentValueList)):
		if sentimentValueList[pos]>0.5 and labelClass[pos]!=1:
			diffNum+=1
		if sentimentValueList[pos]<0.5 and labelClass[pos]!=0:
			diffNum+=1
	return 1-float(diffNum)/float(len(sentimentValueList))
'''测试下标记数据精度'''
def testLabelDataAcc():
	begin=time.clock()
	'''获得原始数据路径'''
	reviewDataSetDir = 'D:/ReviewHelpfulnessPrediction\LabelReviewData'
	reviewDataSetName = 'posNegLabelData'
	reviewDataSetFileType = '.xls'
	dataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
	'''获得目标数据路径'''
	dstSavePath = reviewDataSetDir + '/' + reviewDataSetName + 'BasedDictSentimentScore.txt'
	'''获得原始数据'''
	posreview = tp.get_excel_data(dataSetPath,1,1,"data")
	negreview = tp.get_excel_data(dataSetPath, 2, 1, "data")
	review=posreview+negreview
	'''得到每句评论[[PosSum, NegSum],[],]'''
	sentiment_score_list = get_review_set_sentiement_score(review)
	'''得到每句评论的整体得分'''
	sentiment_overall_score = get_sentiment_overall_score_to_txt(sentiment_score_list, review, dstSavePath)
	labelClass=[]
	for pos in range(len(posreview)):
		labelClass.append(1)
	for pos in range(len(negreview)):
		labelClass.append(0)
	# for pos in range(len(sentiment_overall_score)):
	# 	print sentiment_score_list[pos],sentiment_overall_score[pos],labelClass[pos]
	print 'sentiment Analyze Based Dictionary Accuracy:',getAccuracy(sentiment_overall_score,labelClass),'data item num:',len(review)
'''基于字典情感分析 时间性能：'''
'''参数：原始数据名称 原始数据文件格式 窗口大小 积极边界 消极边界 情感得分边界'''
'''sentiment Analyze based dict running time: 146.88193332 handle review num: 87642'''

def sentiAnalyzeBaseDict(reviewDataSetName,reviewDataSetFileType,windowSize,posBounder,negBounder,sentScoreBounder,timeInterval=20):
	begin=time.clock()
	'''获得原始数据路径'''
	reviewDataSetDir = 'D:/ReviewHelpfulnessPrediction\BulletData'
	saveResPath='D:/ReviewHelpfulnessPrediction/PredictClassRes'
	dataSetPath = reviewDataSetDir + '/' + reviewDataSetName + reviewDataSetFileType
	figDir = 'D:/ReviewHelpfulnessPrediction\SentimentLineFig'
	'''获得目标数据路径'''
	dstSavePath = saveResPath + '/' + reviewDataSetName + 'BasedDictSentimentScore.txt'
	'''获得原始数据'''
	review = tp.get_txt_data(dataSetPath, "lines")
	'''得到每句评论[[PosSum, NegSum],[],]'''
	sentiment_score_list = get_review_set_sentiement_score(review)
	'''得到每句评论的整体得分'''
	sentiment_overall_score = get_sentiment_overall_score_to_txt(sentiment_score_list, review, dstSavePath)
	'''分析评论情感得分数据 按照窗口迭代 获得 情感值 积极比率 消极比率 异常话语位置'''
	# posBounder=0.6
	# negBounder=0.4
	sentimentValueList, posRatioList, negRatioList, strangeWordPos = analyzeSentimentProList(sentiment_overall_score,
																							 windowSize, posBounder, negBounder, sentScoreBounder)
	'''合并重叠区间'''
	finalStrangeWordPos = unionStrangeWordPos(strangeWordPos)
	'''获得平均情感值'''
	meanSentPosPro = getMeanSentimentValue(sentiment_overall_score)
	print 'mean sentiment postive probility', meanSentPosPro
	overallPosRatio=getOverallPosRatio(sentiment_overall_score,posBounder)
	overallNegRatio=getOverallNegRatio(sentiment_overall_score,negBounder)
	'''输出异常话语位置'''
	outputStrangeWordPosInTxt(finalStrangeWordPos, dstSavePath)
	'''绘制情感曲线图'''
	drawSentimentLine(sentimentValueList,figDir+'/'+reviewDataSetName+'SentCurveDA.png')
	drawPosNegRatioPie(overallPosRatio,overallNegRatio,figDir+'/'+reviewDataSetName+'PosNegRatioDA.png')
	'''输出异常话语'''
	outputStrangeWords(finalStrangeWordPos, review)
	'''绘制情感波动动态图'''
	#drawSentimentChangeLine(sentimentValueList, timeInterval, windowSize, -30, 30)
	end=time.clock()
	print 'sentiment Analyze based dict running time:',end-begin,'handle review num:',len(review)

sentiAnalyzeBaseDict('lsj','.log',100,0.6,0.4,-8)
#testLabelDataAcc()











