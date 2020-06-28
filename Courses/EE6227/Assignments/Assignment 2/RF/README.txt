# Random Forests

This set of codes implements Random Forests algorithm to classify data.
You should do some research on your own to understand the basic priciples on how Random Forests Works.

To get started, you should refer to 'TEST_RF.m'.


#### Parameters
nTree: Number of trees   (Needs to be positive integer)
mtry: Number of features in a subset   (Needs to be positive integer)


#### Usage
The main function to train and test Random Forests is:

"""
[TestAcc,TrainingTime,TestingTime,Model] = RF(trainX,trainY,testX,testY,ModelParameters);
"""

Inputs:
trainX                Training data
trainY                Training labels
testX                 Testing data
testY                 Testing labels
ModelParameters       Model parameters

Outputs:
TestAcc           Testing Accuracy
TrainingTime      Time taken for training
TestingTime       Time taken for testing
Model             Trained model
