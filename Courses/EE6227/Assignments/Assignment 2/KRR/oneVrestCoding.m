function Y = oneVrestCoding(label,Uclass)

Nclass=numel(Uclass);
Nsam=numel(label);
Y=zeros(Nsam,Nclass);

for i=1:Nsam
 idx=find(Uclass==label(i));
 Y(i,idx)=1;
end

end


