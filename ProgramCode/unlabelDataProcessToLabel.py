#! /usr/bin/env python2.7
#coding=utf-8
''''''
'''
功能：处理原始数据（未标记数据），便于更快速地进行人工标记以及合并标记数据
去除不含情感词语的客观句
删除重复评论，避免重复标注
将不同excel文件的标注数据合并到一起
合并后标记数据默认保存在D:/ReviewHelpfulnessPrediction\LabelReviewData 目录下
积极消极标记数据 posNegLabelData.xls
主客观标记数据 subObjLabelData.xls
鉴黄标记数据 eroNorLabelData.xls
'''

import textProcessing as tp
import numpy as np
import time
import xlwt
import xlrd
import chardet
import os

'''导入情感词典'''
dictDir='D:/ReviewHelpfulnessPrediction\SentimentDict'
posdict = tp.get_txt_data(dictDir+"/posdict.txt","lines")
negdict = tp.get_txt_data(dictDir+"/negdict.txt","lines")

'''过滤器 过滤掉不含主观情感的语句 客观语句'''

'''构建情感词典 这里只简单地分为积极和消极'''
sentiment_dict=posdict+negdict

'''判断单条评论是否为具备情感倾向语句 如果评论里有一个词位于情感词典中，则可认为该句具备情感倾向'''
def is_single_review_sentiment(review):
	cuted_review = tp.cut_sentence_2(review)# 将评论切割成句子
	for sent in cuted_review:
		seg_sent = tp.segmentation(sent, 'list')# 将句子做分词处理
		for word in seg_sent:
		    if word in  sentiment_dict:
		        return True
	return False

'''过滤掉不含情感词的客观评论'''
'''源数据为txt或log文件格式 目标数据也为txt文件格式'''
def filt_objective_sentence(srcpath,para,dstpath):
	begin=time.clock()
	raw_data=tp.get_txt_data(srcpath,para)
	f = open(dstpath, 'w')
	count=0
	for x in raw_data:
		if is_single_review_sentiment(x)==True:
			f.write(x.encode('utf-8') + '\n')
			count+=1
	f.close()
	end=time.clock()
	print 'filt objective reviews time:',end-begin,'handle review num:',len(raw_data),'subjective review num:',count
	return count
#filt_objective_sentence('D:/crambData\crambData3/430909.txt','lines','D:/ReviewHelpfulnessPrediction\BulletData/430909.txt')

'''删除已过滤的重复评论'''
'''源数据格式为txt文件，将评论保存在excel文件中 格式为 评论：出现次数'''
'''注意excel表格最多能保存65536行'''
def remove_duplicate_comment(srcpath,para,excelpath):
	begin = time.clock()
	raw_data = tp.get_txt_data(srcpath, para)
	review_diff_set={}
	pre_count=len(raw_data)
	cur_count=0
	for x in raw_data:
		if review_diff_set.has_key(x)==False:
			review_diff_set[x]=1
			cur_count+=1
		else:
			review_diff_set[x]+=1
	excel_file = xlwt.Workbook(encoding='utf-8')
	sheet_name = 'label_data'
	sheet_pos = 1
	excel_sheet = excel_file.add_sheet(sheet_name + str(sheet_pos))
	row_pos = 0
	excel_sheet.write(row_pos, 0, 'review_data')
	excel_sheet.write(row_pos, 1, 'review_count')
	excel_sheet.write(row_pos, 2, 'is_subjective')
	excel_sheet.write(row_pos, 3, 'sentiment_tendency')
	excel_sheet.write(row_pos, 4, 'is_erotic')
	excel_sheet.write(row_pos, 5, 'key_words')
	row_pos += 1
	for w,c in review_diff_set.iteritems():
		if row_pos == 65536:
			sheet_pos += 1
			excel_sheet = excel_file.add_sheet(sheet_name + str(sheet_pos))
			row_pos = 0
			excel_sheet.write(row_pos, 0, 'review_data')
			excel_sheet.write(row_pos, 1, 'review_count')
			row_pos += 1
		excel_sheet.write(row_pos, 0, w)
		excel_sheet.write(row_pos, 1, str(c))
		row_pos += 1
	excel_file.save(excelpath)
	end=time.clock()
	print 'remove same reviews time:', end - begin, 'handle review num:',pre_count,'different review num:',cur_count
	return pre_count,cur_count
#remove_duplicate_comment('D:/ReviewHelpfulnessPrediction\BulletData/430909.txt','lines','D:/ReviewHelpfulnessPrediction\LabelReviewData/430909.xls')

'''txt 转 excel'''
def change_txt_to_excel(srcpath,para,excelpath):
	begin = time.clock()
	raw_data = tp.get_txt_data(srcpath, para)
	excel_file = xlwt.Workbook(encoding='utf-8')
	sheet_name = 'label_data'
	sheet_pos = 1
	excel_sheet = excel_file.add_sheet(sheet_name + str(sheet_pos))
	row_pos = 0
	excel_sheet.write(row_pos, 0, 'review_data')
	excel_sheet.write(row_pos, 1, 'review_count')
	excel_sheet.write(row_pos, 2, 'is_subjective')
	excel_sheet.write(row_pos, 3, 'sentiment_tendency')
	excel_sheet.write(row_pos, 4, 'is_erotic')
	excel_sheet.write(row_pos, 5, 'key_words')
	row_pos += 1
	for w in raw_data:
		if row_pos == 65536:
			sheet_pos += 1
			excel_sheet = excel_file.add_sheet(sheet_name + str(sheet_pos))
			row_pos = 0
			excel_sheet.write(row_pos, 0, 'review_data')
			excel_sheet.write(row_pos, 1, 'review_count')
			row_pos += 1
		excel_sheet.write(row_pos, 0, w)
		excel_sheet.write(row_pos, 1, str(1))
		row_pos += 1
	excel_file.save(excelpath)
	end = time.clock()
	print 'remove same reviews time:', end - begin, 'handle review num:', len(raw_data)

#change_txt_to_excel('D:/crambData\crambData7/output3.txt','lines','D:/ReviewHelpfulnessPrediction\LabelReviewData/wms.xls')

'''检查标记数据 看看是否出现格式错误，如出现，显示出现错误的行数,并返回正确标记的数据'''
''''''
'''将标记数据按照主客观 积消极 鉴黄 分类存储在labelDataDir目录下speName下'''
def save_label_data_to_spe_name(labelDataPath,labelDataDir,speName):
	begin=time.clock()
	table = xlrd.open_workbook(labelDataPath)
	sheet = table.sheets()[0]
	labelDataNum=sheet.nrows
	errorRow = []  # 错误行
	subjectiveSubDataItem = []  # 主观数据项
	subjectiveObjDataItem = []  # 客观数据项
	sentimentPosDataItem = []  # 积极数据项
	sentimentNegDataItem = []  # 消极数据项
	eroticEroDataItem = []  # 鉴黄
	eroticNorDataItem = []
	srcDataColPos = 0
	subjectiveColPos = 2
	sentimentColPos = 3
	eroticColPos = 4
	excelData = []
	labelRowNum=labelDataNum
	for rowPos in range(1, labelRowNum):
		excelData.append(sheet.row_values(rowPos))
	for rowPos in range(0, labelRowNum - 1):
		if excelData[rowPos][subjectiveColPos] == 1:
			if excelData[rowPos][sentimentColPos] == 0:
				sentimentNegDataItem.append(excelData[rowPos][srcDataColPos])
			elif excelData[rowPos][sentimentColPos] == 1:
				sentimentPosDataItem.append(excelData[rowPos][srcDataColPos])
			else:
				errorRow.append([rowPos + 2, 'sentiment_tendency value error'])
			subjectiveSubDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][subjectiveColPos] == 0:
			subjectiveObjDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			errorRow.append([rowPos + 2, 'is_subjective value error'])
		if excelData[rowPos][eroticColPos] == 1:
			eroticEroDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][eroticColPos] == 0:
			eroticNorDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			errorRow.append([rowPos + 2, 'is_erotic value error'])
	for x in errorRow:
		print x
	print 'subjective and objective num:', len(subjectiveSubDataItem), len(subjectiveObjDataItem)
	print 'postive and negtive num:', len(sentimentPosDataItem), len(sentimentNegDataItem)
	print 'erotic and normal num:', len(eroticEroDataItem), len(eroticNorDataItem)
	colPos = 0
	'''存储主客观标注的数据'''
	subObjFile = xlwt.Workbook(encoding='utf-8')
	subjectiveSheet = subObjFile.add_sheet('subjective_data')
	for rowPos in range(len(subjectiveSubDataItem)):
		subjectiveSheet.write(rowPos, colPos, subjectiveSubDataItem[rowPos])
	objectiveSheet = subObjFile.add_sheet('objective_data')
	for rowPos in range(len(subjectiveObjDataItem)):
		objectiveSheet.write(rowPos, colPos, subjectiveObjDataItem[rowPos])
	subObjFile.save(labelDataDir + '/' +speName+ 'subObjLabelData.xls')

	'''存储积消极标注的数据'''
	posNegFile = xlwt.Workbook(encoding='utf-8')
	postiveSheet = posNegFile.add_sheet('postive_data')
	for rowPos in range(len(sentimentPosDataItem)):
		postiveSheet.write(rowPos, colPos, sentimentPosDataItem[rowPos])
	negtiveSheet = posNegFile.add_sheet('negtive_data')
	for rowPos in range(len(sentimentNegDataItem)):
		negtiveSheet.write(rowPos, colPos, sentimentNegDataItem[rowPos])
	posNegFile.save(labelDataDir + '/' +speName+  'posNegLabelData.xls')

	'''存储鉴黄标注数据'''
	eroNorFile=xlwt.Workbook(encoding='utf-8')
	eroticSheet=eroNorFile.add_sheet('erotic_data')
	for rowPos in range(len(eroticEroDataItem)):
		eroticSheet.write(rowPos,colPos,eroticEroDataItem[rowPos])
	normalSheet=eroNorFile.add_sheet('normal_data')
	for rowPos in range(len(eroticNorDataItem)):
		normalSheet.write(rowPos,colPos,eroticNorDataItem[rowPos])
	eroNorFile.save(labelDataDir + '/' +speName+  'eroNorLabelData.xls')
	end=time.clock()
	print 'insepect label data is:',end-begin,'handle data num is:',labelDataNum
'''存储关键字 关键字类型为;unicode'''
def save_key_words(subObjKeyWords,posNegKeyWords,eroNorKeyWords,savePath):
	if len(subObjKeyWords)>0:
		f=open(savePath+'SubObjKeyWords.txt','w')
		for x in subObjKeyWords:
			if isinstance(x,unicode)==True:
				f.write(x.encode('utf-8')+'\n')
			else:
				f.write(str(int(x))+'\n')
		f.close()
	if len(posNegKeyWords)>0:
		f=open(savePath+'PosNegKeyWords.txt','w')
		for x in posNegKeyWords:
			if isinstance(x,unicode)==True:
				f.write(x.encode('utf-8')+'\n')
			else:
				f.write(str(int(x))+'\n')
		f.close()
	if len(eroNorKeyWords)>0:
		f=open(savePath+'EroNorKeyWords.txt','w')
		for x in eroNorKeyWords:
			if isinstance(x,unicode)==True:
				f.write(x.encode('utf-8')+'\n')
			else:
				f.write(str(int(x))+'\n')
		f.close()
'''提取标记数据中关键词'''
def extract_keyword_from_spe_name_labeldata_2(labelDataPath, labelDataDir,keyWordDir,speName):
	begin=time.clock()
	table = xlrd.open_workbook(labelDataPath)
	sheet = table.sheets()[0]
	labelDataNum=sheet.nrows
	errorRow = []  # 错误行
	subjectiveSubDataItem = []  # 主观数据项
	subjectiveObjDataItem = []  # 客观数据项
	sentimentPosDataItem = []  # 积极数据项
	sentimentNegDataItem = []  # 消极数据项
	eroticEroDataItem = []  # 鉴黄
	eroticNorDataItem = []
	subObjKeyWords=[]
	posNegKeyWords=[]
	eroNorKeyWords=[]
	srcDataColPos = 0
	subjectiveColPos = 2
	sentimentColPos = 3
	eroticColPos = 4
	keyWordPos=5
	excelData = []
	labelRowNum=labelDataNum
	for rowPos in range(1, labelRowNum):
		excelData.append(sheet.row_values(rowPos))
	for rowPos in range(0, labelRowNum - 1):
		subErrorFlag=False
		posErrorFlag=False
		eroErrorFlag=False
		if excelData[rowPos][subjectiveColPos] == 1:
			if excelData[rowPos][sentimentColPos] == 0:
				sentimentNegDataItem.append(excelData[rowPos][srcDataColPos])
			elif excelData[rowPos][sentimentColPos] == 1:
				sentimentPosDataItem.append(excelData[rowPos][srcDataColPos])
			else:
				posErrorFlag=True
				errorRow.append([rowPos + 2, 'sentiment_tendency value error'])
			subjectiveSubDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][subjectiveColPos] == 0:
			subjectiveObjDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			subErrorFlag=True
			errorRow.append([rowPos + 2, 'is_subjective value error'])
		if excelData[rowPos][eroticColPos] == 1:
			eroticEroDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][eroticColPos] == 0:
			eroticNorDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			errorRow.append([rowPos + 2, 'is_erotic value error'])
			eroErrorFlag=True
		if excelData[rowPos][keyWordPos]!='':
			print excelData[rowPos][keyWordPos]
			keyWords=excelData[rowPos][keyWordPos]
			if subErrorFlag==False:
				subObjKeyWords.append(keyWords)
			if excelData[rowPos][subjectiveColPos]==1 and posErrorFlag==False:
				posNegKeyWords.append(keyWords)
			if eroErrorFlag==False and excelData[rowPos][eroticColPos]==1:
				eroNorKeyWords.append(keyWords)
	print 'subjective and objective num:', len(subjectiveSubDataItem), len(subjectiveObjDataItem)
	print 'postive and negtive num:', len(sentimentPosDataItem), len(sentimentNegDataItem)
	print 'erotic and normal num:', len(eroticEroDataItem), len(eroticNorDataItem)
	colPos = 0
	'''存储主客观标注的数据'''
	subObjFile = xlwt.Workbook(encoding='utf-8')
	subjectiveSheet = subObjFile.add_sheet('subjective_data')
	for rowPos in range(len(subjectiveSubDataItem)):
		subjectiveSheet.write(rowPos, colPos, subjectiveSubDataItem[rowPos])
	objectiveSheet = subObjFile.add_sheet('objective_data')
	for rowPos in range(len(subjectiveObjDataItem)):
		objectiveSheet.write(rowPos, colPos, subjectiveObjDataItem[rowPos])
	subObjFile.save(labelDataDir + '/' +speName+ 'subObjLabelData.xls')

	'''存储积消极标注的数据'''
	posNegFile = xlwt.Workbook(encoding='utf-8')
	postiveSheet = posNegFile.add_sheet('postive_data')
	for rowPos in range(len(sentimentPosDataItem)):
		postiveSheet.write(rowPos, colPos, sentimentPosDataItem[rowPos])
	negtiveSheet = posNegFile.add_sheet('negtive_data')
	for rowPos in range(len(sentimentNegDataItem)):
		negtiveSheet.write(rowPos, colPos, sentimentNegDataItem[rowPos])
	posNegFile.save(labelDataDir + '/' +speName+  'posNegLabelData.xls')

	'''存储鉴黄标注数据'''
	eroNorFile=xlwt.Workbook(encoding='utf-8')
	eroticSheet=eroNorFile.add_sheet('erotic_data')
	for rowPos in range(len(eroticEroDataItem)):
		eroticSheet.write(rowPos,colPos,eroticEroDataItem[rowPos])
	normalSheet=eroNorFile.add_sheet('normal_data')
	for rowPos in range(len(eroticNorDataItem)):
		normalSheet.write(rowPos,colPos,eroticNorDataItem[rowPos])
	eroNorFile.save(labelDataDir + '/' +speName+  'eroNorLabelData.xls')
	end=time.clock()
	print 'insepect label data is:',end-begin,'handle data num is:',labelDataNum
	save_key_words(subObjKeyWords,posNegKeyWords,eroNorKeyWords,keyWordDir+'/'+speName)
	return errorRow

def extract_keyword_from_spe_name_labeldata(labelDataPath, labelDataDir,keyWordDir,speName):
	begin=time.clock()
	table = xlrd.open_workbook(labelDataPath)
	sheet = table.sheets()[0]
	labelDataNum=sheet.nrows
	errorRow = []  # 错误行
	subjectiveSubDataItem = []  # 主观数据项
	subjectiveObjDataItem = []  # 客观数据项
	sentimentPosDataItem = []  # 积极数据项
	sentimentNegDataItem = []  # 消极数据项
	eroticEroDataItem = []  # 鉴黄
	eroticNorDataItem = []
	subObjKeyWords=[]
	posNegKeyWords=[]
	eroNorKeyWords=[]
	srcDataColPos = 0
	subjectiveColPos = 2
	sentimentColPos = 3
	eroticColPos = 4
	keyWordPos=5
	excelData = []
	labelRowNum = labelDataNum
	for rowPos in range(1, labelRowNum):
		excelData.append(sheet.row_values(rowPos))
	for rowPos in range(0, labelRowNum - 1):
		subErrorFlag=False
		posErrorFlag=False
		eroErrorFlag=False
		if excelData[rowPos][subjectiveColPos] == 1:
			if excelData[rowPos][sentimentColPos] == 0:
				sentimentNegDataItem.append(excelData[rowPos][srcDataColPos])
			elif excelData[rowPos][sentimentColPos] == 1:
				sentimentPosDataItem.append(excelData[rowPos][srcDataColPos])
			else:
				posErrorFlag=True
				errorRow.append([rowPos + 2, 'sentiment_tendency value error'])
			subjectiveSubDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][subjectiveColPos] == 0:
			subjectiveObjDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			subErrorFlag=True
			errorRow.append([rowPos + 2, 'is_subjective value error'])
		if excelData[rowPos][eroticColPos] == 1:
			eroticEroDataItem.append(excelData[rowPos][srcDataColPos])
		elif excelData[rowPos][eroticColPos] == 0:
			eroticNorDataItem.append(excelData[rowPos][srcDataColPos])
		else:
			errorRow.append([rowPos + 2, 'is_erotic value error'])
			eroErrorFlag=True
		if excelData[rowPos][keyWordPos]!='':
			print excelData[rowPos][keyWordPos]
			keyWords=excelData[rowPos][keyWordPos]
			if subErrorFlag==False:
				if isinstance(keyWords,unicode)==True:
					keyWordList=keyWords.split(' ')
					for k in keyWordList:
						subObjKeyWords.append(k)
				else:
					subObjKeyWords.append(str(int(keyWords)))
			if excelData[rowPos][subjectiveColPos]==1 and posErrorFlag==False:
				if isinstance(keyWords,unicode)==True:
					keyWordList=keyWords.split(' ')
					for k in keyWordList:
						posNegKeyWords.append(k)
				else:
					posNegKeyWords.append(str(int(keyWords)))
			if eroErrorFlag==False and excelData[rowPos][eroticColPos]==1:
				if isinstance(keyWords,unicode)==True:
					keyWordList=keyWords.split(' ')
					for k in keyWordList:
						eroNorKeyWords.append(k)
				else:
					eroNorKeyWords.append(str(int(keyWords)))
	print 'subjective and objective num:', len(subjectiveSubDataItem), len(subjectiveObjDataItem)
	print 'postive and negtive num:', len(sentimentPosDataItem), len(sentimentNegDataItem)
	print 'erotic and normal num:', len(eroticEroDataItem), len(eroticNorDataItem)
	colPos = 0
	'''存储主客观标注的数据'''
	subObjFile = xlwt.Workbook(encoding='utf-8')
	subjectiveSheet = subObjFile.add_sheet('subjective_data')
	for rowPos in range(len(subjectiveSubDataItem)):
		subjectiveSheet.write(rowPos, colPos, subjectiveSubDataItem[rowPos])
	objectiveSheet = subObjFile.add_sheet('objective_data')
	for rowPos in range(len(subjectiveObjDataItem)):
		objectiveSheet.write(rowPos, colPos, subjectiveObjDataItem[rowPos])
	subObjFile.save(labelDataDir + '/' +speName+ 'subObjLabelData.xls')

	'''存储积消极标注的数据'''
	posNegFile = xlwt.Workbook(encoding='utf-8')
	postiveSheet = posNegFile.add_sheet('postive_data')
	for rowPos in range(len(sentimentPosDataItem)):
		postiveSheet.write(rowPos, colPos, sentimentPosDataItem[rowPos])
	negtiveSheet = posNegFile.add_sheet('negtive_data')
	for rowPos in range(len(sentimentNegDataItem)):
		negtiveSheet.write(rowPos, colPos, sentimentNegDataItem[rowPos])
	posNegFile.save(labelDataDir + '/' +speName+  'posNegLabelData.xls')

	'''存储鉴黄标注数据'''
	eroNorFile=xlwt.Workbook(encoding='utf-8')
	eroticSheet=eroNorFile.add_sheet('erotic_data')
	for rowPos in range(len(eroticEroDataItem)):
		eroticSheet.write(rowPos,colPos,eroticEroDataItem[rowPos])
	normalSheet=eroNorFile.add_sheet('normal_data')
	for rowPos in range(len(eroticNorDataItem)):
		normalSheet.write(rowPos,colPos,eroticNorDataItem[rowPos])
	eroNorFile.save(labelDataDir + '/' +speName+  'eroNorLabelData.xls')
	end=time.clock()
	print 'insepect label data is:',end-begin,'handle data num is:',labelDataNum
	save_key_words(subObjKeyWords,posNegKeyWords,eroNorKeyWords,keyWordDir+'/'+speName)
	return errorRow

# extract_keyword_from_spe_name_labeldata('D:/ReviewHelpfulnessPrediction\LabelReviewData/470673.xls', 1000,
#  				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','D:/ReviewHelpfulnessPrediction\KeyWords','470673Label')
# extract_keyword_from_spe_name_labeldata('D:/ReviewHelpfulnessPrediction\LabelReviewData/763137Raw.xls', 2000,
#  				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','D:/ReviewHelpfulnessPrediction\KeyWords','763137Label')
# extract_keyword_from_spe_name_labeldata('D:/ReviewHelpfulnessPrediction\LabelReviewData/label_review_count_data.xls', 2000,
#  				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','D:/ReviewHelpfulnessPrediction\KeyWords','lsj')
# extract_keyword_from_spe_name_labeldata('D:/ReviewHelpfulnessPrediction\LabelReviewData/pdd_label_data.xls', 1000,
#  				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','D:/ReviewHelpfulnessPrediction\KeyWords','pdd')
# extract_keyword_from_spe_name_labeldata('D:/ReviewHelpfulnessPrediction\LabelReviewData/wms.xls', 1500,
#  				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','D:/ReviewHelpfulnessPrediction\KeyWords','wms')

# save_label_data_to_spe_name('D:/ReviewHelpfulnessPrediction\LabelReviewData/pdd_label_data.xls', 200,
# 				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','pdd')
'''将多个主播房间标记数据合并在一起 按照主客观 积消极 鉴黄 分类合并'''
'''speNameList=['lsj','pdd']'''
def unionFewLabelData(labelDataDir,speNameList,dstDataDir):
	begin=time.clock()
	dataTypeList=['subObjLabelData.xls','posNegLabelData.xls','eroNorLabelData.xls']
	sheetNameList=[['subjective_data','objective_data'],['postive_data','negtive_data'],['erotic_data','normal_data']]
	posNegDataNum=[]
	for dataTypePos in range(len(dataTypeList)):
		posDataList=[]
		negDataList=[]
		for name in speNameList:
			labelDataPath=labelDataDir+'/'+name+dataTypeList[dataTypePos]
			print labelDataPath
			curPosData=tp.get_excel_data(labelDataPath,1,1,'data')
			curNegData=tp.get_excel_data(labelDataPath,2,1,'data')
			print len(curPosData),len(curNegData)
			for x in curPosData:
				posDataList.append(x)
			for x in curNegData:
				negDataList.append(x)
		workbook=xlwt.Workbook(encoding='utf-8')
		sheetNameOne=workbook.add_sheet(sheetNameList[dataTypePos][0])
		sheetNameTwo=workbook.add_sheet(sheetNameList[dataTypePos][1])
		print len(posDataList),len(negDataList)
		posNegDataNum.append(len(posDataList))
		posNegDataNum.append(len(negDataList))
		for rowPos in range(len(posDataList)):
			sheetNameOne.write(rowPos,0,posDataList[rowPos])
		for rowPos in range(len(negDataList)):
			sheetNameTwo.write(rowPos,0,negDataList[rowPos])
		workbook.save(dstDataDir+'/'+dataTypeList[dataTypePos])
	end=time.clock()
	print 'union label data time is:',end-begin
	return posNegDataNum

'''合并所有关键字'''
def unionKeyWords(keyWordDir,speNameList):
	begin = time.clock()
	dataTypeList = ['SubObjKeyWords.txt', 'PosNegKeyWords.txt', 'EroNorKeyWords.txt']
	allKeyWord=[]
	for dataTypePos in range(len(dataTypeList)):
		keyWords=set([])
		for name in speNameList:
			keyWordPath=keyWordDir+'/'+name+dataTypeList[dataTypePos]
			if os.path.exists(keyWordPath):
				f=open(keyWordPath,'r')
				rows=''.join(f.readlines()).split('\n')
				rows.pop(len(rows)-1)
				for x in rows:
					keyWords.add(x.decode('utf-8'))
		allKeyWord.append(keyWords)

	save_key_words(allKeyWord[0],allKeyWord[1],allKeyWord[2],keyWordDir+'/')


#unionFewLabelData('D:/ReviewHelpfulnessPrediction\LabelReviewData',['lsj','pdd','763137Label','wms','470673Label'])
#unionKeyWords('D:/ReviewHelpfulnessPrediction\KeyWords',['lsj','pdd','763137Label','wms','470673Label'])






