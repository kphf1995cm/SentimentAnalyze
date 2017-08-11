import selectBestClassifier
import unlabelDataProcessToLabel

# save_label_data_to_spe_name('D:/ReviewHelpfulnessPrediction\LabelReviewData/label_review_count_data.xls', 1400,
# 				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','lsj')
# save_label_data_to_spe_name('D:/ReviewHelpfulnessPrediction\LabelReviewData/pdd_label_data.xls', 200,
# 				 'D:/ReviewHelpfulnessPrediction\LabelReviewData','pdd')
unlabelDataProcessToLabel.save_label_data_to_spe_name('D:/ReviewHelpfulnessPrediction\LabelReviewData/label_review_count_data.xls', 100,'D:/ReviewHelpfulnessPrediction\LabelReviewData','llsj')
selectBestClassifier.handleSelectClfWork()