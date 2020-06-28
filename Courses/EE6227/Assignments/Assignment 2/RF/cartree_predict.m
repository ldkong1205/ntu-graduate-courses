function [tree_output,index] = cartree_predict(Data,RETree)
        M=size(Data,1); 
               
        tree_output=zeros(M,1);
        child_node=RETree.childnode;
        Node_var=RETree.node_var;
        
        Pca=RETree.p;

        Node_label=RETree.nodelabel;

    for i=1:M
        
        current_node = 1;
        while (child_node(current_node)~=0)
            
            cvar = Node_var{current_node};
            cp=Pca{current_node};
            X=Data(i,cvar)*cp(1:end-1);
            if X<cp(end)
               current_node = child_node(current_node);
            else
               current_node = child_node(current_node)+1;
            end
        end
            tree_output(i) = Node_label(current_node); 
            
             if nargout > 1
                 index(i)=current_node;
             end
     end
      if (size(Data,1) == size(tree_output,1)) 
      tree_output = tree_output';
      end