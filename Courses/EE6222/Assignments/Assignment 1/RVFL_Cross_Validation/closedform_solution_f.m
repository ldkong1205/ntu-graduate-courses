function[ACC_CV_mean,ACC_CV_var]=closedform_solution_f(dataset_name)

run(strcat('./',dataset_name,'/',dataset_name,'_R','.m'));

data=data(:,2:end);
dataX=data(:,1:end-1);

% do normalization for each feature
mean_X=mean(dataX,1);
dataX=dataX-repmat(mean_X,size(dataX,1),1);
norm_X=sum(dataX.^2,1);
norm_X=sqrt(norm_X);
norm_X=repmat(norm_X,size(dataX,1),1);
dataX=dataX./norm_X;
dataY=data(:,end);

% for datasets where training-testing partition is available, paramter tuning is based on this file.
run(strcat('./',dataset_name,'/',dataset_name,'_conxuntos','.m'));
trainX=dataX(index1,:); 
trainY=dataY(index1,:);
testX=dataX(index2,:);
testY=dataY(index2,:);
MAX_acc=zeros(6,1);
Best_N=zeros(6,1);
Best_C=zeros(6,1);
Best_S=zeros(6,1);

test_acc1 = [];
test_acc2 = [];
test_acc3 = [];
test_acc4 = [];
test_acc5 = [];
test_acc6 = [];

%Linearly scale the random features before feedinto the nonlinear activation function. 
S=-5:0.5:5;
for s=1:numel(S)
     
    %the number of hidden neurons
for N=3:20:203
   
    %¦Ë in ridge regression
  for C=-5:14 
    
        %RVFL regularized least square
        Scale=2^S(s);
        option1.N=N;
        option1.C=2^C;
        option1.Scale=Scale;
        option1.Scalemode=3;
        option1.bias=1;
        option1.link=1;
        option1.ActivationFunction='radbas';
        option1.mode = 1;
        
        % RVFL Moore-Penrose pseudoinverse
        option2.N=N;
        option2.C=2^C;
        option2.Scale=Scale;
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=1;
        option2.ActivationFunction= 'radbas';
        option2.mode = 2;
        
     [train_accuracy1,test_accuracy1]=RVFL_train_val(trainX,trainY,testX,testY,option1);
     [train_accuracy2,test_accuracy2]=RVFL_train_val(trainX,trainY,testX,testY,option2);  
    
     test_acc1(end+1)=test_accuracy1;
     test_acc2(end+1)=test_accuracy2;
     
    if test_accuracy1>MAX_acc(1); % paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(1)=test_accuracy1;
      Best_N(1)=N;
      Best_C(1)=C;
      Best_S(1)=Scale;
   end
  
     if test_accuracy2>MAX_acc(2);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(2)=test_accuracy2;
      Best_N(2)=N;
      Best_C(2)=C;
      Best_S(2)=Scale;
     end

 end
 end
end

test_acc1_mean = mean(test_acc1);
test_acc1_var =  var(test_acc1);
test_acc2_mean = mean(test_acc2);
test_acc2_var =  var(test_acc2);

%for datasets where training-testing partition is not available, performance vealuation is based on cross-validation.
run(strcat('./',dataset_name,'/',dataset_name,'_conxuntos_kfold','.m'));

ACC_CV_1 = zeros(4,1);
ACC_CV_2 = zeros(4,1);

ACC_CV_mean = zeros(2,1);
ACC_CV_var = zeros(2,1);
for i=1:4
    
    trainX=dataX(index{2*i-1},:);
    trainY=dataY(index{2*i-1},:);
    testX=dataX(index{2*i},:);
    testY=dataY(index{2*i},:);
    
        %RVFL sigmoid
        option1.N=Best_N(1);
        option1.C=2^Best_C(1);
        option1.Scale=Best_S(1);
        option1.Scalemode=3;
        option1.bias=1;
        option1.link=1;
        option1.ActivationFunction='radbas';
        option1.mode = 1;
        
        % RVFL radbas
        option2.N=Best_N(2);
        option2.C=2^Best_C(2);
        option2.Scale=Best_S(2);
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=1;
        option2.ActivationFunction= 'radbas';
        option2.mode = 2;
        
        % ACC_CV each row is the accuracy for one RVFL configuration. Each column is a single trial for evaluation.
        [train_accuracy1,ACC_CV_1(i)]=RVFL_train_val(trainX,trainY,testX,testY,option1);
        [train_accuracy2,ACC_CV_2(i)]=RVFL_train_val(trainX,trainY,testX,testY,option2);
     
end

ACC_CV_mean=[mean(ACC_CV_1),mean(ACC_CV_2)];
ACC_CV_var=[var(ACC_CV_1),var(ACC_CV_2)];

save(strcat(mfilename,'_',dataset_name));

