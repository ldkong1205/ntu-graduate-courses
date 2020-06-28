function [label,confi,confiall]=oneVrestDecoding(Y,Ulabel)
Nsam=size(Y,1);
label=zeros(Nsam,1);
confi=zeros(Nsam,1);
confiall=zeros(size(Y));
for i=1:Nsam
 [val,idx]= max(Y(i,:));
 label(i)=Ulabel(idx);
 confi(i)=val/sum(Y(i,:));
 confiall(i,:)=Y(i,:)/sum(Y(i,:));
end
end