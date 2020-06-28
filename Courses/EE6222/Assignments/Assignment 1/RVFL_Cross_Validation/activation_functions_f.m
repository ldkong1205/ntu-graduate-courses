function[ACC_CV_mean,ACC_CV_var]=activation_functions_f(dataset_name)

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
    
        %RVFL sigmoid
        Scale=2^S(s);
        option1.N=N;
        option1.C=2^C;
        option1.Scale=Scale;
        option1.Scalemode=3;
        option1.bias=1;
        option1.link=1;
        option1.ActivationFunction='sigmoid';
        
        % RVFL radbas
        option2.N=N;
        option2.C=2^C;
        option2.Scale=Scale;
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=1;
        option2.ActivationFunction= 'radbas';
       
        % RVFL sine
        option3.N=N;
        option3.C=2^C;
        option3.Scale=Scale;
        option3.Scalemode=3;
        option3.bias=1;
        option3.link=1;
        option3.ActivationFunction= 'sine';
        
        %RVFL sign
        option4.N=N;
        option4.C=2^C;
        option4.Scale=Scale;
        option4.Scalemode=3;
        option4.bias=1;
        option4.link=1;
        option4.ActivationFunction= 'sign';
        
        %RVFL hardlim
        option5.N=N;
        option5.C=2^C;
        option5.Scale=Scale;
        option5.Scalemode=3;
        option5.bias=1;
        option5.link=1;
        option5.ActivationFunction= 'hardlim';
        
        %RVFL sign
        option6.N=N;
        option6.C=2^C;
        option6.Scale=Scale;
        option6.Scalemode=3;
        option6.bias=1;
        option6.link=1;
        option6.ActivationFunction= 'tribas';
        
     [train_accuracy1,test_accuracy1]=RVFL_train_val(trainX,trainY,testX,testY,option1);
     [train_accuracy2,test_accuracy2]=RVFL_train_val(trainX,trainY,testX,testY,option2);  
     [train_accuracy3,test_accuracy3]=RVFL_train_val(trainX,trainY,testX,testY,option3);
     [train_accuracy4,test_accuracy4]=RVFL_train_val(trainX,trainY,testX,testY,option4); 
     [train_accuracy5,test_accuracy5]=RVFL_train_val(trainX,trainY,testX,testY,option5);
     [train_accuracy6,test_accuracy6]=RVFL_train_val(trainX,trainY,testX,testY,option6); 
     
     test_acc1(end+1)=test_accuracy1;
     test_acc2(end+1)=test_accuracy2;
     test_acc3(end+1)=test_accuracy3;
     test_acc4(end+1)=test_accuracy4;   
     test_acc5(end+1)=test_accuracy5;
     test_acc6(end+1)=test_accuracy6;  
     
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
   
     if test_accuracy3>MAX_acc(3);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(3)=test_accuracy3;
      Best_N(3)=N;
      Best_C(3)=C;
      Best_S(3)=Scale;
    end
 
   
     if test_accuracy4>MAX_acc(4);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(4)=test_accuracy4;
      Best_N(4)=N;
      Best_C(4)=C;
      Best_S(4)=Scale;
     end
     
     if test_accuracy5>MAX_acc(5);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(5)=test_accuracy5;
      Best_N(5)=N;
      Best_C(5)=C;
      Best_S(5)=Scale;
     end
     
     if test_accuracy6>MAX_acc(6);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
      MAX_acc(6)=test_accuracy6;
      Best_N(6)=N;
      Best_C(6)=C;
      Best_S(6)=Scale;
    end
 end
 end
end

test_acc1_mean = mean(test_acc1);
test_acc1_var =  var(test_acc1);
test_acc2_mean = mean(test_acc2);
test_acc2_var =  var(test_acc2);
test_acc3_mean = mean(test_acc3);
test_acc3_var =  var(test_acc3);
test_acc4_mean = mean(test_acc4);
test_acc4_var =  var(test_acc4);
test_acc5_mean = mean(test_acc5);
test_acc5_var =  var(test_acc5);
test_acc6_mean = mean(test_acc6);
test_acc6_var =  var(test_acc6);

%for datasets where training-testing partition is not available, performance vealuation is based on cross-validation.
run(strcat('./',dataset_name,'/',dataset_name,'_conxuntos_kfold','.m'));

ACC_CV_1 = zeros(4,1);
ACC_CV_2 = zeros(4,1);
ACC_CV_3 = zeros(4,1);
ACC_CV_4 = zeros(4,1);
ACC_CV_5 = zeros(4,1);
ACC_CV_6 = zeros(4,1);
ACC_CV_mean = zeros(6,1);
ACC_CV_var = zeros(6,1);
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
        option1.ActivationFunction='sigmoid';
        
        % RVFL radbas
        option2.N=Best_N(2);
        option2.C=2^Best_C(2);
        option2.Scale=Best_S(2);
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=1;
        option2.ActivationFunction= 'radbas';
       
        % RVFL sine
        option3.N=Best_N(3);
        option3.C=2^Best_C(3);
        option3.Scale=Best_S(3);
        option3.Scalemode=3;
        option3.bias=1;
        option3.link=1;
        option3.ActivationFunction= 'sine';
        
        %RVFL sign
        option4.N=Best_N(4);
        option4.C=2^Best_C(4);
        option4.Scale=Best_S(4);
        option4.Scalemode=3;
        option4.bias=1;
        option4.link=1;
        option4.ActivationFunction= 'sign';
        
        %RVFL hardlim
        option5.N=Best_N(5);
        option5.C=2^Best_C(5);
        option5.Scale=Best_S(5);
        option5.Scalemode=3;
        option5.bias=1;
        option5.link=1;
        option5.ActivationFunction= 'hardlim';
        
        %RVFL sign
        option6.N=Best_N(6);
        option6.C=2^Best_C(6);
        option6.Scale=Best_S(6);
        option6.Scalemode=3;
        option6.bias=1;
        option6.link=1;
        option6.ActivationFunction= 'tribas';
        
        % ACC_CV each row is the accuracy for one RVFL configuration. Each column is a single trial for evaluation.
        [train_accuracy1,ACC_CV_1(i)]=RVFL_train_val(trainX,trainY,testX,testY,option1);
        [train_accuracy2,ACC_CV_2(i)]=RVFL_train_val(trainX,trainY,testX,testY,option2);
        [train_accuracy3,ACC_CV_3(i)]=RVFL_train_val(trainX,trainY,testX,testY,option3);
        [train_accuracy4,ACC_CV_4(i)]=RVFL_train_val(trainX,trainY,testX,testY,option4);
		[train_accuracy5,ACC_CV_5(i)]=RVFL_train_val(trainX,trainY,testX,testY,option5);
		[train_accuracy6,ACC_CV_6(i)]=RVFL_train_val(trainX,trainY,testX,testY,option6);
  
     
end

ACC_CV_mean=[mean(ACC_CV_1),mean(ACC_CV_2),mean(ACC_CV_3),mean(ACC_CV_4),mean(ACC_CV_5),mean(ACC_CV_6)];
ACC_CV_var=[var(ACC_CV_1),var(ACC_CV_2),var(ACC_CV_3),var(ACC_CV_4),var(ACC_CV_5),var(ACC_CV_6)];

save(strcat(mfilename,'_',dataset_name));



