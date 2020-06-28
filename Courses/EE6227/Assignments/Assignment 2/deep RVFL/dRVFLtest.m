function out=dRVFLtest(input,net)
% dRVFLtest: Deep Random Vector Functional Link testing function
%
%Output Parameters
%         y: actul output
%
%Input Parameters
%         net: structure that includes network parameters.
%         structure, numberofhiddenlayer, hiddenlayerweights,
%         hiddenlayerout, D, outputlayerweights
%
% Example Usage
%         input=rand(3,5);
%         target=rand(3,1);
%         net=dRVFLtrain(input, target, [5,5,5])
%         out=dRVFLtest(input, net)
%        % check target and y values
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %                           TEST                               %
% %            Deep Random Vector Functional Link                %
% %                                                              %
% %                  Apdullah Yayik, 2019                        %
% %                  apdullahyayik@gmail.com                     %
% %                                                              %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

input=normDadapt(input, net.normparameters.minn, net.normparameters.maxx);
hiddenlayeroutstest{1,1}=input;
Dtest=hiddenlayeroutstest{1,1};
numberofhiddenlayer=size(net.hiddenlayerweights, 2)+1;
for p=1:numberofhiddenlayer-1
    hiddenlayeroutstest{1,p+1}=logsig(hiddenlayeroutstest{1,p}*net.hiddenlayerweights{1,p});
    Dtest=[Dtest, hiddenlayeroutstest{1,p+1}];
end
y=Dtest*net.outputlayerweights;
out=outCreate(y);
end


function out=outCreate(y)
% create output

outtemp=[];
for p=1:size(y,1)
    outtemp=[outtemp; y(p,:)==max(y(p,:))];
end
clear y

out=zeros(size(outtemp,1), 1);
for pp=1:size(outtemp,2)
    out=out+outtemp(:,pp)*pp;
end
end

function X=normDadapt(X, minn, maxx)
% adapt norm

sizeX=size(X);
for ii=1:sizeX(1)
    for j=1:sizeX(2)
        X(ii,j)=(((X(ii,j)-minn(j))/(maxx(j)-minn(j))))*2-1;
    end
end
end