clear all
close all
clc
clear all
close all
clc
load('aim2.mat')
length_negative = 6499
%% PCA check
% find no change in 14 days
temp  = All_fill_norm{1}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))

location = find(temp_s==0)';
location_check = setdiff([1:3401],location)
location_p = location;
temp(location,:)
X = [All_fill_norm{1}(location,:),All_fill_norm{2}(location,:)]
[coeff,score,latent,tsquared,explained,mu]  = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
% [theta,rho] = cart2pol(score(:,1)-0.024,score(:,2)-0.039)
[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0256)
scatter(theta,rho)

data = X;
% Weight and Mean:
wt = 1./var(data);
mu = mean(data);
% PCA, W is coefficient and Y is the score
[W,Y,latent,tsquared,explained,mu]=pca(data);
% First observation of the centered data and its score
temp  = All_fill_norm{3}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))
location = find(temp_s==0)';
location_check = setdiff([1:length_negative ],location)
data =  [All_fill_norm{3}(location,:),All_fill_norm{4}(location,:)]
x1 = data-mu;
% According to the reconstruction rule, we should have x1=y1*W'
% therefore, y1 = x1/W'
y = x1/W'

[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0256)

polarhistogram(theta,30,'Normalization','probability')
hold on
[theta,rho] = cart2pol(y(:,1)+0.04,y(:,2)-0.0256)

polarhistogram(theta,30,'Normalization','probability')

%%
close all

%%%%%%%%%%%%%%

[x,centers] = hist(theta,70)
bar(centers,x)
hold on

[curvefit, goodness, output, convmsg] = fit(centers',x','gauss4');
plot(curvefit)
close all
polarhistogram(theta,30)
theta_d= rad2deg(theta)
for i = 1:length(theta)
    if theta_d(i)<0
        theta_d(i) = theta_d(i)+360;
    end

end

pca_1 = location(find(theta_d>15&theta_d<=80));
pca_2 = location(find(theta_d>80&theta_d<=175));
pca_3 = location(find(theta_d>175&theta_d<=260));
pca_4 = location(find(theta_d>260&theta_d<=300));
pca_5 = location(find(theta_d>300|theta_d<=15));

rat_1 = length(pca_1)/length_negative 
rat_2 =length(pca_2)/length_negative 
rat_3 =length(pca_3)/length_negative 
rat_4 =length(pca_4)/length_negative 
rat_5 =length(pca_5)/length_negative 
[rat_1;rat_2;rat_3;rat_4;rat_5]


a = setdiff([1:3401],location_p')
% a = [1:3401]
X = [slope_burst_min_7da{1}(a);slope_burst_min_7db{1}(a);dosage_All{1}(a)]'
[theta,rho,z] = cart2pol(X(:,1),X(:,2),X(:,3))
thetamin = theta;
X_rn = [slope_burst_min_7da{3}(location_check);slope_burst_min_7db{3}(location_check);dosage_All{3}(location_check)]'
[theta,rho,z] = cart2pol(X_rn(:,1),X_rn(:,2),X_rn(:,3))
thetamin_rn = theta;
scatter(theta,rho)
close all
polarhistogram(thetamin,30)
theta_d = [];
theta_min_d= rad2deg(theta)
for i = 1:length(theta)
    if theta_min_d(i)<0
        theta_min_d(i) = theta_min_d(i)+360;
    end

end

abmin7_1 = find(theta_min_d>170&theta_min_d<=200);
abmin7_2 = find(theta_min_d>200&theta_min_d<=250);
abmin7_3= find(theta_min_d>250&theta_min_d<=290);


X = [theta,rho]
h = histogram(theta)
X = [slope_burst_max_7da{1}(a);slope_burst_max_7db{1}(a)]'
X_rn = [slope_burst_max_7da{3}(location_check);slope_burst_max_7db{3}(location_check)]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
thetamax = theta;
[theta,rho] = cart2pol(X_rn(:,1),X_rn(:,2))
scatter(theta,rho)
thetamax_rn = theta
theta_d = [];
theta_max_d= rad2deg(theta)
for i = 1:length(theta)
    if theta_max_d(i)<0
        theta_max_d(i) = theta_max_d(i)+360;
    end

end

abmax7_1 = find(theta_max_d>10&theta_max_d<=65);
abmax7_2 = find(theta_max_d>65 & theta_max_d<=120);
abmax7_3 = find(theta_max_d>120&theta_max_d<=180);
abmax7_4= find(theta_max_d>180&theta_max_d<=270);
abmax7_5= find(theta_max_d>270|theta_max_d<=10);
x = [170,200,200,250,250,290]
y = [10,65,65,120,180,270,270,10]
count  = 0
an = location_check
for k = 1:2:5
    for q = 1:2:7
        if q == 7
        count  = count+length(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) | theta_max_d<=y(q+1)))
xy{q,k} = an(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) | theta_max_d<=y(q+1)))
        else
             count  = count+length(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))
xy{q,k} = an(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))

        end
    end
end

close all
polarhistogram(thetamax,30)
scatter3(thetamax,thetamin,freq_All{1}(a),'.')
hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar
xlim([-pi,pi])
ylim([-pi,pi])
thetamax_rn(end+1) = 3;
thetamin_rn(end+1) = 3;
hist3([thetamax_rn,thetamin_rn],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])

colorbar
xlim([-pi,pi])
ylim([-pi,pi])
 polarhistogram(thetamax,20,'Normalization','probability')
 hold on
 polarhistogram(thetamax_rn,20,'Normalization','probability')
h = polarhistogram(thetamin,30,'Normalization','probability')
hold on
a = polarhistogram(thetamin_rn,30,'Normalization','probability')
a = h
% scatter(thetamax,thetamin)

location_record = [pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}']
%location_record = [xy{1,1},xy{1,3},xy{1,5},xy{1,7},xy{3,1},xy{3,3},xy{3,5},xy{3,7},xy{5,1},xy{5,3},xy{5,5},xy{5,7}]

%%
aim_option = {pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}'}
aim_option = [length(pca_1)/(length_negative );length(pca_2)/(length_negative );length(pca_3)/(length_negative );length(pca_4)/(length_negative );length(pca_5)/(length_negative );length(xy{1,1}')/(length_negative );length(xy{1,3}')/(length_negative );length(xy{1,5}')/(length_negative );length(xy{3,1}')/(length_negative );length(xy{3,3}')/(length_negative );length(xy{3,5}')/(length_negative );length(xy{5,1}')/(length_negative );length(xy{5,3}')/(length_negative );length(xy{5,5}')/(length_negative );length(xy{7,1}')/(length_negative );length(xy{7,3}')/(length_negative );length(xy{7,5}')/(length_negative )]
pn_percent_record = [pn_percent_record,aim_option]
pn_percent_record(:,3) = pn_percent_record(:,1)./pn_percent_record(:,2)

aim_option_n = aim_option
%save('aim_plot.mat','aim_option_n','real_negative','-append')
%% Plot
aim_option = {pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}'}
name = {'pca 1';'pca 2';'pca 3';'pca 4';'pca 5';'7d 1';'7d 2';'7d 3';'7d 4';'7d 5';'7d 6';'7d 7';'7d 8';'7d 9';'7d 10';'7d 11';'7d 12'}
num = 0
All_fill_norm_truen_pd =All_fill_norm{3}(:,:)
All_fill_norm_truen_ds = All_fill_norm{4}(:,:)
for special = 1:17
aim =aim_option{special}
for i = 1:length(aim )
    temp  = aim (i)
    if special >5
plot(All_fill_norm_truen_pd(temp,22:36),'--','LineWidth',1)

    elseif special <=5
        subplot(2,1,1)
        plot(All_fill_norm_truen_pd(temp,1:57),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm_truen_ds(temp,1:57),'--','LineWidth',1)
        
    
    end
hold on
end
std(All_fill_norm_truen_pd(aim,22:36))
if special>5
    plot(mean(All_fill_norm_truen_pd(aim,22:36)),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim,22:36)),std(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    xline(8);
elseif special <=5
    subplot(2,1,1)
    plot([mean(All_fill_norm_truen_pd(aim,:))],'LineWidth',2)
    %errorbar([1:57],[mean(All_fill_norm{1}(aim,:))],[std(All_fill_norm{1}(aim,:))],'LineWidth',2)
xline(29);
subplot(2,1,2)
 plot([mean(All_fill_norm_truen_ds(aim,:))],'LineWidth',2)
 %errorbar([1:57],[mean(All_fill_norm{2}(aim,:))],[std(All_fill_norm{2}(aim,:))],'LineWidth',2)

end
title([name{special} ' Percentage : '  num2str(100*length(aim)/length_negative ) '%'])
% saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/cluster_28_7_ab_ver1_falsenegative/' name{special} ' '  num2str(100*length(aim)/length_negative ) '%_s.png'])
close all
num = num+100*length(aim)/length_negative 
end


