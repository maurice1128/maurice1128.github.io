clear all
close all
clc
load('aim2.mat')


%% split data 8:2
% index_training = randperm(length_positive,round(length_positive *0.8))
% index_validating = setdiff([1:length_positive],index_training)
% All_fill_norm_positive_training =All_fill_norm
% All_fill_norm_positive_training{1} =All_fill_norm_positive_training{1}(index_training,:) 
% All_fill_norm_positive_training{2} = All_fill_norm_positive_training{2}(index_training,:) 
% All_fill_norm_positive_validation = All_fill_norm
% All_fill_norm_positive_validation{1} =All_fill_norm_positive_validation{1}(index_validating ,:) 
% All_fill_norm_positive_validation{2} = All_fill_norm_positive_validation{2}(index_validating ,:) 
% slope_burst_max_7da_training = slope_burst_max_7da
% slope_burst_max_7da_training{1} = slope_burst_max_7da_training{1}(index_training)
% slope_burst_max_7da_training{2} = slope_burst_max_7da_training{2}(index_training)
% slope_burst_max_7db_training = slope_burst_max_7db
% slope_burst_max_7db_training{1} = slope_burst_max_7db_training{1}(index_training)
% slope_burst_max_7db_training{2} = slope_burst_max_7db_training{2}(index_training)
% slope_burst_min_7da_training = slope_burst_min_7da
% slope_burst_min_7da_training{1} = slope_burst_min_7da_training{1}(index_training)
% slope_burst_min_7da_training{2} = slope_burst_min_7da_training{2}(index_training)
% slope_burst_min_7db_training = slope_burst_min_7db
% slope_burst_min_7db_training{1} = slope_burst_min_7db_training{1}(index_training)
% slope_burst_min_7db_training{2} = slope_burst_min_7db_training{2}(index_training)
% slope_burst_max_7da_validation = slope_burst_max_7da
% slope_burst_max_7da_validation{1} = slope_burst_max_7da_validation{1}(index_validating)
% slope_burst_max_7da_validation{2} = slope_burst_max_7da_validation{2}(index_validating)
% slope_burst_max_7db_validation = slope_burst_max_7db
% slope_burst_max_7db_validation{1} = slope_burst_max_7db_validation{1}(index_validating)
% slope_burst_max_7db_validation{2} = slope_burst_max_7db_validation{2}(index_validating)
% slope_burst_min_7da_validation = slope_burst_min_7da
% slope_burst_min_7da_validation{1} = slope_burst_min_7da_validation{1}(index_validating)
% slope_burst_min_7da_validation{2} = slope_burst_min_7da_validation{2}(index_validating)
% slope_burst_min_7db_validation = slope_burst_min_7db
% slope_burst_min_7db_validation{1} = slope_burst_min_7db_validation{1}(index_validating)
% slope_burst_min_7db_validation{2} = slope_burst_min_7db_validation{2}(index_validating)
% save('aim2.mat')



%% PCA check
% find no change in 14 days
length_negative = length(All_fill_norm{3}(:,22:36))
length_positive = length(All_fill_norm_positive_training{1}(:,22:36))
temp  = All_fill_norm_positive_training{1}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))

location = find(temp_s==0)';
location_check = setdiff([1:length_positive],location)
location_p = location;
temp(location,:)
X = [All_fill_norm_positive_training{1}(location,:),All_fill_norm_positive_training{2}(location,:)]
[coeff,score,latent,tsquared,explained,mu]  = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')

%[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0256)
[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0270)
scatter(theta,rho)
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

rat_1 = length(pca_1)/length_positive
rat_2 =length(pca_2)/length_positive
rat_3 =length(pca_3)/length_positive
rat_4 =length(pca_4)/length_positive
rat_5 =length(pca_5)/length_positive
[rat_1;rat_2;rat_3;rat_4;rat_5]


a = setdiff([1:length_positive],location_p')
X = [slope_burst_min_7da_training{1}(a);slope_burst_min_7db_training{1}(a);dosage_All{1}(a)]'
[theta,rho,z] = cart2pol(X(:,1),X(:,2),X(:,3))
thetamin = theta;

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
X = [slope_burst_max_7da_training{1}(a);slope_burst_max_7db_training{1}(a)]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
thetamax = theta;
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
All_fill_norm_truen_pd =All_fill_norm_positive_training{1}(:,:)
All_fill_norm_truen_ds = All_fill_norm_positive_training{2}(:,:)
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
title([name{special} ' Percentage : '  num2str(100*length(aim)/length_positive ) '%'])
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/clustering_28_7_ab_ver1_positive_splitdata_training/' name{special} ' '  num2str(100*length(aim)/length_positive ) '%_s.png'])
close all
num = num+100*length(aim)/length_negative 
end


