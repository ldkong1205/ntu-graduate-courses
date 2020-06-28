function RETree = cartree_train(Data,Labels,Index,mtry)

minparent = 2;
method = 'c'; %c or g is same
minleaf = 1;


N = numel(Labels);
L = 2*ceil(N/minleaf)-1;
M = size(Data,2);

nodeDataIndx = cell(L,1);
nodeDataIndx{1} = 1 : N;

nodevar=cell(L,1);
nodep=cell(L,1);

nodeCutVar = zeros(L,1);
nodeCutValue = zeros(L,1);

nodeflags = zeros(L+1,1);

nodelabel = zeros(L,1);
childnode = zeros(L,1);

nodeflags(1) = 1;


switch lower(method)
    case {'c','g'}
        [unique_labels,~,Labels]= unique(Labels);
        max_label = numel(unique_labels);
    otherwise
        max_label= [];
end

current_node = 1;

while nodeflags(current_node) == 1;
    
    currentDataIndx = nodeDataIndx{current_node};
    free_node = find(nodeflags == 0,1);
    if  numel(unique(Labels(currentDataIndx)))==1
        switch lower(method)
            case {'c','g'}
                nodelabel(current_node) = unique_labels(Labels(currentDataIndx(1)));
            case 'r'
                nodelabel(current_node) = Labels(currentDataIndx(1));
        end
        nodeCutVar(current_node) = 0;
        nodeCutValue(current_node) = 0;
        nodevar{current_node}=0;
        nodep{current_node}=0;
    else
        if numel(currentDataIndx)>2*minparent
            
            node_var = randperm(M);
            node_var = node_var(1:mtry);
            
            
            X = Data(currentDataIndx,node_var);
            
            
            
            [bestCutVar,bestCutValue] =axis_parallel_cut(Labels(currentDataIndx),X,minleaf);
            
            if bestCutVar~=-1
                b=zeros(mtry+1,1);
                b(bestCutVar)=1;
                b(end)=bestCutValue;
            end
            
            
            
            if bestCutVar~=-1
                nodeCutVar(current_node) = bestCutVar;
                nodevar{current_node}=node_var;
                nodep{current_node}=b;
                D=X*b(1:end-1);
                nodeDataIndx{free_node} = currentDataIndx(D<=b(end));
                nodeDataIndx{free_node+1} = currentDataIndx(D>b(end));
                nodeflags(free_node:free_node + 1) = 1;
                childnode(current_node)=free_node;
            else
                switch lower(method)
                    case {'c' 'g'}
                        [~, leaf_label] = max(hist(Labels(currentDataIndx),1:max_label));
                        nodelabel(current_node)=unique_labels(leaf_label);
                    case 'r'
                        nodelabel(current_node)  = mean(Labels(currentDataIndx));
                end
                
            end
        else
            switch lower(method)
                case {'c' 'g'}
                    [~, leaf_label] = max(hist(Labels(currentDataIndx),1:max_label));
                    nodelabel(current_node)=unique_labels(leaf_label);
                case 'r'
                    nodelabel(current_node)  = mean(Labels(currentDataIndx));
            end
        end
    end
    current_node = current_node+1;
end


RETree.nodeDataIndex=  nodeDataIndx(1:current_node-1);
RETree.p=nodep(1:current_node-1);
RETree.node_var=nodevar(1:current_node-1);
RETree.nodeCutVar = nodeCutVar(1:current_node-1);
RETree.childnode = childnode(1:current_node-1);
RETree.nodelabel = nodelabel(1:current_node-1);
RETree.dataindex=Index;
end

