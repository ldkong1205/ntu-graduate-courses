# Ensemble Deep Random Vector Functional Link (edRVFL)

This set of codes implements Ensemble Deep Random Vector Functional Link (edRVFL) algorithm to classify data.
You should do some research on your own to understand the basic priciples on how edRVFL Works.

To get started, you should refer to 'TEST_RVFL.m'.


#### Parameters
L: Number of layers   (Needs to be positive integer)
N: Number of neurons   (Needs to be positive integer)
C: Regularisation parameter   (Needs to be positive float)
scale: Scale of randomisation   (Needs to be positive float)
Activation: Activation function   (Shown below)


#### Activation Function
On this set of codes, we implemented edRVFL with 'sigmoid' or 'relu' activation function.

If you wish to try with different activation function, you can replace the following codes in BOTH files (MRVFLtrain.m and MRVFLpredict.m):
"""
% Activation function
switch lower(act_fun)
    case "relu"
        A1 = relu(A1);
    case "sigmoid"
        A1 = sigmoid(A1);
    otherwise
        error("Not Implemented");
end
"""

#### Usage
The main function to train and test Ensemble Deep Random Vector Functional Link is:

"""
[Model,TrainAcc,TestAcc,TrainingTime,TestingTime] = MRVFL(trainX,trainY,testX,testY,ModelParameters);
"""

Inputs:
trainX                Training data
trainY                Training labels
testX                 Testing data
testY                 Testing labels
ModelParameters       Model parameters

Outputs:
Model             Trained model
TrainAcc          Training Accuracy
TestAcc           Testing Accuracy
TrainingTime      Time taken for training
TestingTime       Time taken for testing
