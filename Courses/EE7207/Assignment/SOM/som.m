x = load('data_train.mat');
x = x.data_train;
net = selforgmap([4 5]);
net = train(net,x);
view(net)
c = net(x);
classes = vec2ind(c);