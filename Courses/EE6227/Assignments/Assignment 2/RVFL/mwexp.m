
%iris
clear all
load fisheriris.mat
trainlabel=[ones(1,40), 2*ones(1,40), 3*ones(1,40)]';
traindata=[meas(1:40,:); meas(51:90,:); meas(101:140,:)];

testlabel=[ones(1,10), 2*ones(1,10), 3*ones(1,10)]';
testdata=[meas(41:50,:); meas(91:100,:); meas(141:150,:)];

tic, net=RVFLtrain(traindata, trainlabel, 5);toc
y=RVFLtest(testdata, net);


%mnist
clear all
load mnist.mat
trainX=double(trainX);trainX=trainX(1:3000,:);
trainY=double(trainY);trainY=trainY(1:3000);

testX=double(testX);testX=testX(1:1000,:);
testY=double(testY);testY=testY(1:1000);

tic, net=RVFLtrain(trainX, trainY', 5);toc
y=RVFLtest(testX,net);





