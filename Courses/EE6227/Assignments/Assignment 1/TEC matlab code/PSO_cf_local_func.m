function [gbest,gbestval,fitcount]= PSO_cf_local_func(fhd,Max_Gen,Max_FES,Particle_Number,Dimension,VRmin,VRmax,varargin)
%[gbest,gbestval,fitcount]= PSO_local_func('f8',3500,200000,30,30,-5.12,5.12)
rand('state',sum(100*clock));
me=Max_Gen;
ps=Particle_Number;
D=Dimension;
cc=[1.49445 1.49445];   %acceleration constants
w=0.729;


column_num=5;row_num=ps/column_num;
for i=1:ps
    r=ceil(i/column_num);
    c=i-(r-1)*column_num;
    neighbor(i,:)=[(((r-1)>0).*(r-1)+((r-1)==0).*(row_num)-1)*column_num+c,...
                  (((r+1)<=row_num).*(r+1)+((r+1)>row_num).*1-1)*column_num+c,...
                  (r-1)*column_num+(((c-1)>0).*(c-1)+((c-1)==0).*column_num),...
                  (r-1)*column_num+(((c+1)<=column_num).*(c+1)+((c+1)>column_num).*1)];
end
if length(VRmin)==1
    VRmin=repmat(VRmin,1,D);
    VRmax=repmat(VRmax,1,D);
end
mv=0.5.*(VRmax-VRmin);
VRmin=repmat(VRmin,ps,1);
VRmax=repmat(VRmax,ps,1);
Vmin=repmat(-mv,ps,1);
Vmax=-Vmin;
pos=VRmin+(VRmax-VRmin).*rand(ps,D);
for i=1:ps;
e(i,1)=feval(fhd,pos(i,:),varargin{:});
end

fitcount=ps;
vel=Vmin+2.*Vmax.*rand(ps,D);%initialize the velocity of the particles
pbest=pos;
pbestval=e; %initialize the pbest and the pbest's fitness value
[gbestval,gbestid]=min(pbestval);
gbest=pbest(gbestid,:);%initialize the gbest and the gbest's fitness value
gbestrep=repmat(gbest,ps,1);
g_res(1)=gbestval;

for i=2:me

    for k=1:ps
    [tmp,tmpid]=min(pbestval(neighbor(k,:)));
%     aa(k,:)=cc(1).*rand(1,D).*(pbest(k,:)-pos(k,:))+cc(2).*rand(1,D).*(gbestrep(k,:)-pos(k,:));
    aa(k,:)=cc(1).*rand(1,D).*(pbest(k,:)-pos(k,:))+cc(2).*rand(1,D).*(pbest(neighbor(k,tmpid),:)-pos(k,:));
    vel(k,:)=w.*vel(k,:)+aa(k,:); 
    vel(k,:)=(vel(k,:)>mv).*mv+(vel(k,:)<=mv).*vel(k,:); 
    vel(k,:)=(vel(k,:)<(-mv)).*(-mv)+(vel(k,:)>=(-mv)).*vel(k,:);
    pos(k,:)=pos(k,:)+vel(k,:); 
%     pos(k,:)=((pos(k,:)>=VRmin(1,:))&(pos(k,:)<=VRmax(1,:))).*pos(k,:)...
%         +(pos(k,:)<VRmin(1,:)).*(VRmin(1,:)+0.25.*(VRmax(1,:)-VRmin(1,:)).*rand(1,D))+(pos(k,:)>VRmax(1,:)).*(VRmax(1,:)-0.25.*(VRmax(1,:)-VRmin(1,:)).*rand(1,D));
%     if (sum(pos(k,:)>VRmax(k,:))+sum(pos(k,:)<VRmin(k,:)))==0;
%     pos(k,:)=((pos(k,:)<=VRmax(1,:))&(pos(k,:)>=VRmin(1,:))).*pos(k,:)+(1-(pos(k,:)<=VRmax(1,:))&(pos(k,:)>=VRmin(1,:))).*(VRmin(1,:)+(VRmax(1,:)-VRmin(1,:)).*rand(1,D));
    e(k,1)=feval(fhd,pos(k,:),varargin{:});
    fitcount=fitcount+1;
    tmp=(pbestval(k)<e(k));
    temp=repmat(tmp,1,D);
    pbest(k,:)=temp.*pbest(k,:)+(1-temp).*pos(k,:);
    pbestval(k)=tmp.*pbestval(k)+(1-tmp).*e(k);%update the pbest
    if pbestval(k)<gbestval
    gbest=pbest(k,:);
    gbestval=pbestval(k);
    gbestrep=repmat(gbest,ps,1);%update the gbest
    end
    end
%     end

%     if mod(i,50)==0,
%     plot(pos(:,D-1),pos(:,D),'b*');
%     hold on
%     plot(gbest(D-1),gbest(D),'r*');   
%     hold off
% %     axis([VRmin(1,D-1),VRmax(1,D-1),VRmin(1,D),VRmax(1,D)])
%     title(['PSO: ',num2str(i),' generations, Gbestval=',num2str(gbestval)]);  
%     drawnow
%     end
%     
if gbestval<=1e-5
    break;
end

if fitcount>=Max_FES
    break;
end

end


