function [gbest,gbestval,fitcount]= CPSO_func(fhd,Max_Gen,Max_FES,Particle_Number,Dimension,VRmin,VRmax,varargin)
%[gbest,gbestval,fitcount]= PSO_func('f8',3500,200000,30,30,-5.12,5.12)
rand('state',sum(100*clock));
me=Max_Gen;
ps=Particle_Number;
D=Dimension;
fi=[1.49 1.49];   %acceleration constants
groupnum=D;
iwt=0.9-(1:me).*(0.5./me);
if length(VRmin)==1
    VRmin=repmat(VRmin,1,D);
    VRmax=repmat(VRmax,1,D);
end
mv=(VRmax-VRmin);mv1=mv;
VRmin=repmat(VRmin,ps,1);
VRmax=repmat(VRmax,ps,1);
Vmin=repmat(-mv,ps,1);
Vmax=-Vmin;
pos=VRmin+(VRmax-VRmin).*rand(ps,D);
vel=zeros(ps,D);
pos1=VRmin+(VRmax-VRmin).*rand(ps,D);pbest1=[];pbestval1=[];gbest1=[];gbestid1=[];e1=[];
vel1=zeros(ps,D);
for j=1:ps
    e(j,1)=feval(fhd,pos(j,:),varargin{:});
    e1(j,1)=feval(fhd,pos1(j,:),varargin{:});
end

pbest=pos;pbest1=pos1;
pbestval=e;pbestval1=e1;  %initialize the pbest and the pbest's fitness value
[gbestval,gbestid]=min(pbestval);
gbest=pbest(gbestid,:);%initialize the gbest and the gbest's fitness value
gbestrep=repmat(gbest,ps,1);
[gbestval1,gbestid1]=min(pbestval1);
gbest1=pbest1(gbestid1,:);%initialize the gbest and the gbest's fitness value
gbestrep1=repmat(gbest1,ps,1);
gbestid1=repmat(gbestid1,1,groupnum);
pbestval1=repmat(pbestval1,1,groupnum);
e1=repmat(e1,1,groupnum);
tr(1)=gbestval;
cnt=0;
fitcount=0;
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rc=randperm(D);rc=sort(rc);
tmp=round(D/groupnum);
particle_num(1,:)=rc(1:tmp);
for j=1:groupnum-1
particle_num(j,:)=rc((j*tmp-tmp+1):(j*tmp));
end
particle_num(groupnum,:)=rc((D-tmp+1):D);
for j=1:groupnum
group_l=length(particle_num(groupnum,:));
group_d(j,:)=particle_num(j,:);
end
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for i=2:me

for j=1:groupnum

    for k=1:ps    
       
    pos1_temp=gbest1;
    pos1_temp(group_d(j,:))=pos1(k,group_d(j,:));
%     if (sum(pos1(k,group_d(j,:))>VRmax(k,group_d(j,:)))+sum(pos1(k,group_d(j,:))<VRmin(k,group_d(j,:))))==0;
    e1(k,j)=feval(fhd,pos1_temp,varargin{:});
%     end
    fitcount=fitcount+1;
    tmp1=(pbestval1(k,j)<e1(k,j));
    temp1=repmat(tmp1,1,1);
    pbest1(k,group_d(j,:))=temp1.*pbest1(k,group_d(j,:))+(1-temp1).*pos1(k,group_d(j,:));
    pbestval1(k,j)=tmp1.*pbestval1(k,j)+(1-tmp1).*e1(k,j);%update the pbest

    if pbestval1(k,j)<gbestval1
    gbest1(group_d(j,:))=pbest1(k,group_d(j,:));
    gbestval1=pbestval1(k,j);
    gbestrep1=repmat(gbest1,ps,1);
    gbestid1(j)=k;
    end

    aa1(k,group_d(j,:))=fi(1).*rand(1,1).*(pbest1(k,group_d(j,:))-pos1(k,group_d(j,:)))+fi(2).*rand(1,1).*(gbestrep1(k,group_d(j,:))-pos1(k,group_d(j,:)));
    vel1(k,group_d(j,:))=iwt(i).*vel1(k,group_d(j,:))+aa1(k,group_d(j,:)); %update the vel1ocity for all the particles
    vel1(k,group_d(j,:))=(vel1(k,group_d(j,:))>mv1(group_d(j,:))).*mv1(group_d(j,:))+(vel1(k,group_d(j,:))<=mv1(group_d(j,:))).*vel1(k,group_d(j,:)); 
    vel1(k,group_d(j,:))=(vel1(k,group_d(j,:))<(-mv1(group_d(j,:)))).*(-mv1(group_d(j,:)))+(vel1(k,group_d(j,:))>=(-mv1(group_d(j,:)))).*vel1(k,group_d(j,:));%limit the vel1ocity
    pos1(k,group_d(j,:))=pos1(k,group_d(j,:))+vel1(k,group_d(j,:)); %update the pos1ition for all the particles
    pos1(k,group_d(j,:))=(pos1(k,group_d(j,:))>VRmax(k,group_d(j,:))).*VRmax(k,group_d(j,:))+(pos1(k,group_d(j,:))<=VRmax(k,group_d(j,:))).*pos1(k,group_d(j,:)); 
    pos1(k,group_d(j,:))=(pos1(k,group_d(j,:))<VRmin(k,group_d(j,:))).*VRmin(k,group_d(j,:))+(pos1(k,group_d(j,:))>=VRmin(k,group_d(j,:))).*pos1(k,group_d(j,:));
   
    end
end
    rc=randperm(ps);
    k=rc(1);
    if k==gbestid, k=rc(2); end
    pos(k,:)=gbest1;
    
    for k=1:ps
  
    e(k,1)=feval(fhd,pos(k,:),varargin{:});
    fitcount=fitcount+1;
    tmp=(pbestval(k)<e(k));
    temp=repmat(tmp,1,D);
    pbest(k,:)=temp.*pbest(k,:)+(1-temp).*pos(k,:);
    pbestval(k)=tmp.*pbestval(k)+(1-tmp).*e(k);%update the pbest

    if pbestval(k)<gbestval
    gbest=pbest(k,:);gbestid=k;
    gbestval=pbestval(k);
    gbestrep=repmat(gbest,ps,1);%update the gbest
    end
     
    aa(k,:)=fi(1).*rand(1,D).*(pbest(k,:)-pos(k,:))+fi(2).*rand(1,D).*(gbestrep(k,:)-pos(k,:));
    vel(k,:)=iwt(i).*vel(k,:)+aa(k,:); %update the velocity for all the particles
    vel(k,:)=(vel(k,:)>mv).*mv+(vel(k,:)<=mv).*vel(k,:); 
    vel(k,:)=(vel(k,:)<(-mv)).*(-mv)+(vel(k,:)>=(-mv)).*vel(k,:);%limit the velocity
    pos(k,:)=pos(k,:)+vel(k,:); %update the position for all the particles
    pos(k,:)=(pos(k,:)>VRmax(k,:)).*VRmax(k,:)+(pos(k,:)<=VRmax(k,:)).*pos(k,:); 
    pos(k,:)=(pos(k,:)<VRmin(k,:)).*VRmin(k,:)+(pos(k,:)>=VRmin(k,:)).*pos(k,:);

    end
   

    for j=1:groupnum
    rc=randperm(ps);
    k=rc(1);
    if k==gbestid1(j), k=rc(2); end
    pos1(k,group_d(j,:))=gbest(group_d(j,:));
    end

% if round(i/20)==i/20
%     plot(pos(:,D-1),pos(:,D),'b*');hold on;
%     for k=1:floor(D/2)
%         plot(gbest(:,2*k-1),gbest(:,2*k),'r*');
%     end
%     hold off
%     title(['PSO: ',num2str(i),' generations, Gbestval=',num2str(gbestval)]);  
%     axis([VRmin(1,D-1),VRmax(1,D-1),VRmin(1,D),VRmax(1,D)])
%     drawnow
% end

if fitcount>=Max_FES
    break;
end
end


