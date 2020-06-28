# Ensemble Kernel Ridge Regression (KRR)

This set of codes implements Kernel Ridge Regression (KRR) algorithm (exact form) to classify data.
You should do some research on your own to understand the basic priciples on how KRR Works.

To get started, you should refer to 'TEST_KRR.m'.


#### Parameters
kernel: kernel   (See below)
kernel_param: kernel parameters   (See below)
lambda: Regularisation parameter   (Needs to be positive float)


#### Kernels
On this set of codes, we implemented 'RBF_kernel','lin_kernel','poly_kernel','wav_kernel' and'Chi_square' kernels.
Details can be found in 'kernel_matrix.m'.

You can use any kernel. 
kernel_param is different for different kernel used.
For example: for 'RBF_kernel', kernel_param is gamma (which is a positive float value).


#### Usage
The main function to train and test Kernel Ridge Regrtession is:

"""
[TestAcc,TrainingTime,TestingTime] = KRR_RBF(trainX,trainY,testX,testY,ModelParameters);
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
