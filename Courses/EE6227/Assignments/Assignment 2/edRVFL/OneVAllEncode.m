function [YOut, classes] = OneVAllEncode(Yin,classes)

% Convert a column vector of class labels into a nSamp x nClass matrix 
% containing 1s and 0s, where Y(i,j) = 1 if j = y(i) and 0 otherwise.
if nargin < 2
    classes = unique(Yin);
end
nClass = numel(classes);
YOut = zeros(size(Yin,1),nClass);

for i = 1:nClass
   YOut(:,i) = Yin==classes(i);
end

end