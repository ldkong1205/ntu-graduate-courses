function net= dRVFLtrain(input, target, structure)
% dRVFLtrain: Deep Random Vector Functional Link training function
%
%Output Parameters
%         net: structure that includes network parameters.
%         structure, numberofhiddenlayer, hiddenlayerweights,
%         hiddenlayerout, D, outputlayerweights
%
%Input Parameters
%         input: input data (each row represent different observations)
%         target: desired outputs
%         structure: hidden layer neuron numbers (exept first and last layers), for instance: [5, 10, 15, 20]
%         enhancementnodesneuronnumber: number of enhacement nodes (specific to RVFL nets)
%
% Example Usage
%         input=rand(3,5);
%         target=rand(3,1);
%         net=xdRVFLtrain(input, target, [5,5,5])
%             
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %                           TRAIN                              %
% %           Deep Random Vector Functional Link                 %
% %                                                              %
% %                    Apdullah Yayik, 2019                      %
% %                    apdullahyayik@gmail.com                   %
% %                                                              %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if isequal(size(target,1), size(input,1))==0
    error('Error: input and target sizes dismatch')
else
    target=targetCreate(target);
    [net.normparameters.minn, net.normparameters.maxx, input]=normD(input);
    structure=[size(input, 2), structure, size(target,1)];
    numberofhiddenlayer=size(structure, 2);
    hiddenlayerouts=input;
    net.hiddenlayerweights=cell(1,numberofhiddenlayer-1);
%     D=zeros(size(input,1), sum(structure));% init
    D=hiddenlayerouts;
    for p=1:numberofhiddenlayer-1
        net.hiddenlayerweights{1,p}=rand(structure(p),structure(p+1));
        hiddenlayerouts=logsig(hiddenlayerouts*net.hiddenlayerweights{1,p});      
        D=[D, hiddenlayerouts]; 
    end
    net.outputlayerweights=pinv(D)*target; 
end
end

 function target=targetCreate(trainlabel)
% creates target

 classnumber=length(unique(trainlabel));
    target=[];
    for p=1:classnumber
        target=[target trainlabel==unique(p)];
    end
 end   
 
function [minn, maxx, X]=normD(X)
% peforms linear normalization

sizeX=size(X);
minn=zeros(1, size(X,2));
maxx=zeros(1, size(X,2));
for i=1:sizeX(2)
    minn(i)=min(X(:,i));
    maxx(i)=max(X(:,i));
end
for ii=1:sizeX(1)
    for j=1:sizeX(2)
        X(ii,j)=(((X(ii,j)-minn(j))/(maxx(j)-minn(j))))*2-1;
    end
end
end
    
    
    
 
