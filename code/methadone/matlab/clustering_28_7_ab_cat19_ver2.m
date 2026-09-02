%% Clustering 28_7_ab_cat19 ver2
clear all
close all
clc
load('aim2.mat')
%save('variable.mat','All_fill_norm','All_raw_fix','Scattering_All','slope_All','slope_15d_All','freq_All','gap_All','dosage_All','slope_burst_max_All','slope_burst_min_All','slope_burst_max_15d','slope_burst_min_15d','slope_burst_sum_15d', 'gap_diff_All','freq_gap_summation','slope_burst_max_7da' ,'slope_burst_max_7db','slope_burst_min_7da','slope_burst_min_7db','slope_burst_sum_7da','slope_burst_sum_7db','freq_All_3', ...
%    'dosage_All_15d_MPD','dosage_All_15d_MDS','slope_15d_All','slope_burst_max_7da' , ...
%   'slope_burst_max_7db','slope_burst_min_7da', 'slope_burst_min_7db','slope_burst_sum_7da','slope_burst_sum_7db', ...
 %   'slope_burst_max_3da', 'slope_burst_max_3db' ,'slope_burst_min_3da' , 'slope_burst_min_3db','slope_burst_sum_3da','slope_burst_sum_3db' )


%% Analysis
temp  = All_fill_norm{1}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))

location = find(temp_s==0)';
location_check = setdiff([1:3401],location)
temp(location,:)
X = [All_fill_norm{1}(location,:),All_fill_norm{2}(location,:)]
[coeff,score,latent,tsquared,explained,mu] = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
title('主成分分析後降維數據')
xlabel('第一主成分')
ylabel('第二主成分')
ax = gca;
ax.FontSize = 12;
[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0256)
scatter(theta,rho)
polarhistogram(theta,30)
%%
histogram(theta,70)
title('主成分分析後降維數據')
xlabel('Theta (-pi - pi)')
ylabel('Number of sample')
ax = gca;
ax.FontSize = 12;
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




a = setdiff([1:3401],location')
% a = [1:3401]
X = [slope_burst_min_7da{1}(a);slope_burst_min_7db{1}(a);dosage_All{1}(a)]'


% scatter(X(:,1),X(:,2),'.')
% title('驗尿前後最小斜率關係圖')
% xlabel('驗尿後最小斜率 (百分比變化/天)')
% ylabel('驗尿前最小斜率 (百分比變化/天)')
% ax = gca;
% ax.FontSize = 12;


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
X = [slope_burst_max_7da{1}(a);slope_burst_max_7db{1}(a)]'
% scatter(X(:,1),X(:,2),'.')
% title('驗尿前後最大斜率關係圖')
% xlabel('驗尿後最大斜率 (百分比變化/天)')
% ylabel('驗尿前最大斜率 (百分比變化/天)')
% ax = gca;
% ax.FontSize = 12;

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(theta,rho)
thetamax = theta;
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
for k = 1:2:5
    for q = 1:2:7
        if q == 7
        count  = count+length(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) | theta_max_d<=y(q+1)))
xy{q,k} = a(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) | theta_max_d<=y(q+1)))
        else
             count  = count+length(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))
xy{q,k} = a(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))

        end
    end
end

close all
polarhistogram(thetamax,30)
scatter3(thetamax,thetamin,freq_All{1}(a),'.')
hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar
title('驗尿前後七天最大最小斜率極座標轉換後二元直方圖')
xlabel('Theta minimum (-pi - pi)')
ylabel('Theta maximum (-pi - pi)')
zlabel('Number of Sample')
ax = gca;
ax.FontSize = 12;
 polarhistogram(thetamax,20)
polarhistogram(thetamin,30)
% scatter(thetamax,thetamin)

location_record = [pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}']
%location_record = [xy{1,1},xy{1,3},xy{1,5},xy{1,7},xy{3,1},xy{3,3},xy{3,5},xy{3,7},xy{5,1},xy{5,3},xy{5,5},xy{5,7}]
positive_percent_record = [length(pca_1)/(length(temp));length(pca_2)/(length(temp));length(pca_3)/(length(temp));length(pca_4)/(length(temp));length(pca_5)/(length(temp));length(xy{1,1}')/(length(temp));length(xy{1,3}')/(length(temp));length(xy{1,5}')/(length(temp));length(xy{3,1}')/(length(temp));length(xy{3,3}')/(length(temp));length(xy{3,5}')/(length(temp));length(xy{5,1}')/(length(temp));length(xy{5,3}')/(length(temp));length(xy{5,5}')/(length(temp));length(xy{7,1}')/(length(temp));length(xy{7,3}')/(length(temp));length(xy{7,5}')/(length(temp))]
pn_percent_record =positive_percent_record

%% Plot
aim_option = {pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}'}
name = {'pca 1';'pca 2';'pca 3';'pca 4';'pca 5';'7d 1';'7d 2';'7d 3';'7d 4';'7d 5';'7d 6';'7d 7';'7d 8';'7d 9';'7d 10';'7d 11';'7d 12'}
num = 0

for special = 1:17
aim =aim_option{special}
for i = 1:length(aim )
    temp  = aim (i)
    if special >5
plot(All_fill_norm{1}(temp,22:36),'--','LineWidth',1)

    elseif special <=5
        subplot(2,1,1)
        plot(All_fill_norm{1}(temp,1:57),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm{2}(temp,1:57),'--','LineWidth',1)
        
    
    end
hold on
end
std(All_fill_norm{1}(aim,22:36))
if special>5
    plot(mean(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim,22:36)),std(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    xline(8);
elseif special <=5
    subplot(2,1,1)
    plot([mean(All_fill_norm{1}(aim,:))],'LineWidth',2)
    %errorbar([1:57],[mean(All_fill_norm{1}(aim,:))],[std(All_fill_norm{1}(aim,:))],'LineWidth',2)
xline(29);
subplot(2,1,2)
 plot([mean(All_fill_norm{2}(aim,:))],'LineWidth',2)
 %errorbar([1:57],[mean(All_fill_norm{2}(aim,:))],[std(All_fill_norm{2}(aim,:))],'LineWidth',2)

end
title([name{special} ' Percentage : '  num2str(100*length(aim)/3401) '%'])
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/cluster_28_7_ab_ver2/' name{special} ' '  num2str(100*length(aim)/3401) '%_s.png'])
close all
num = num+100*length(aim)/3401
end


