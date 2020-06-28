function x = l2_weights(A,b,C,Nsample)

if size(A,2)<Nsample
   x = (eye(size(A,2))/C+A'*A) \ A'*b;
else
    x = A'*((eye(size(A,1))/C+A*A') \ b);
end


end
% toc

