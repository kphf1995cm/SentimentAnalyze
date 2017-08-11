# SentimentAnalyze

1 环境配置
编译器：Python2.7.12
开发集成环境：Pycharm2017.1.5
相关库：nltk、sklearn、numpy、xlwt、wlrd、matplotlib


2 基于词典情感分析涉及模块
 1）textProcessing（文本预处理）
完成数据读取、中文分词、词性标注、句子切割、停用词过滤、格式转换等功能。
用户词典（用于中文分词）保存在D:/ReviewHelpfulnessPrediction/PreprocessingModule目录下，名称为userdict.txt ,可在里面增加一些新的词汇，每行的格式为：词语 词频。如果用户词典存储位置发生更改，则需要更改jieba.load_userdict(userDictPath)。
停用词默认保存在D:/ReviewHelpfulnessPrediction/PreprocessingModule目录下，名称为stopword.txt，用于seg_fil_excel、seg_fil_txt等函数中。
2）sentimentAnalyzeBasedDict 
完成情感得分计算、情感曲线绘制等功能。
情感、程度词词典默认保存在D:/ReviewHelpfulnessPrediction/SentimentDict目录下，可以在里面增加相应的新的词汇，如果存储目录发生更改，需要修改 dictDir的值。
sentiAnalyzeBaseDict()完成基于词典的情感分析工作，分析的文本数据默认保存在
D:/ReviewHelpfulnessPrediction/BulletData目录下。输入参数包括：原始数据名称、原始数据文件格式、窗口大小、积极边界、消极边界、情感得分边界。该函数会将预测的原始数据所属类别结果保存在D:/ReviewHelpfulnessPrediction/PredictClassRes目录下，绘制出的情感波动曲线图、类别成分占比图保存在D:/ReviewHelpfulnessPrediction/SentimentLineFig目录下，并且会输出异常语句所在的位置以及相应的异常语句。 



3 基于机器学习情感分析涉及模块
1）textProcessing（文本预处理）
完成数据读取、中文分词、词性标注、句子切割、停用词过滤、格式转换等功能。
用户词典（用于中文分词）保存在D:/ReviewHelpfulnessPrediction/PreprocessingModule目录下，名称为userdict.txt ,可在里面增加一些新的词汇，每行的格式为：词语 词频。如果用户词典存储位置发生更改，则需要更改jieba.load_userdict(userDictPath)。
停用词默认保存在D:/ReviewHelpfulnessPrediction/PreprocessingModule目录下，名称为stopword.txt，用于seg_fil_excel、seg_fil_txt等函数中。
2）unlabelDataProcessToLabel
完成客观语句过滤、重复评论删除、已标记数据的检查与错误处理、标记数据合并等功能。
情感词典默认保存在D:/ReviewHelpfulnessPrediction/SentimentDict目录下，标记数据默认保存在D:/ReviewHelpfulnessPrediction/LabelReviewData目录下。
3）selectBestClassifier
完成最佳分类器的选择、最佳特征维度选择的功能。
已标记的训练数据保存在D:/ReviewHelpfulnessPrediction/LabelReviewData目录下，如果改变，需要修改posNegDir、pos_review、neg_review的值。情感停用词保存在D:/ReviewHelpfulnessPrediction/PreprocessingModule/sentiment_stopword.txt文件路径下。构建的分类器保存在D: /ReviewHelpfulnessPrediction/BuildedClassifier目录下，挑选出的最佳分类器名称以及最佳特征维度保存在D: /ReviewHelpfulnessPrediction/BuildedClassifier/bestClassifierDimenAcc文件路径下。
4）predictDataPosNegProbility
完成预测未知数据所属分类功能。
已标记的训练数据保存在D:/ReviewHelpfulnessPrediction/LabelReviewData目录下，如果改变，需要修改create_word_bigram_scores()函数。
sentiAnalyzeBaseML()完成基于机器学习的情感分析工作，分析的文本数据默认保存在D:/ReviewHelpfulnessPrediction/BulletData目录下。输入参数包括：原始数据名称、原始数据文件格式、窗口大小、积极边界、消极边界、情感得分边界。该函数会将预测的原始数据所属类别结果保存在D:/ReviewHelpfulnessPrediction/PredictClassRes目录下，绘制出的情感波动曲线图、类别成分占比图保存在D:/ReviewHelpfulnessPrediction/SentimentLineFig目录下，并且会输出异常语句所在的位置以及相应的异常语句。 
