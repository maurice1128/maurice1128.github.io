%% Plot all Negative & Postive

clear all
clc
close all


load('aim_plot.mat')
%% code
All_fill_norm_truen_pd =All_fill_norm{3}(real_negative,:)
All_fill_norm_truen_ds = All_fill_norm{4}(real_negative,:)

 %% Plot
aim_option_n = aim_option_n
name = {'pca 1';'pca 2';'pca 3';'pca 4';'pca 5';'7d 1';'7d 2';'7d 3';'7d 4';'7d 5';'7d 6';'7d 7';'7d 8';'7d 9';'7d 10';'7d 11';'7d 12'}
num = 0
All_fill_norm_truen_pd =All_fill_norm{3}(real_negative,:)
All_fill_norm_truen_ds = All_fill_norm{4}(real_negative,:)
for special = 1:17
aim_n =aim_option_n{special}
aim_p = aim_option_p{special}
for i = 1:length(aim_n )
    temp_n  = aim_n (i)
    if special >5
plot(All_fill_norm_truen_pd(temp_n,22:36),'--','LineWidth',1)
hold on

    elseif special <=5
        subplot(2,1,1)
        plot(All_fill_norm_truen_pd(temp_n,1:57),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm_truen_ds(temp_n,1:57),'--','LineWidth',1)
        
    
    end
hold on
end

for i = 1:length(aim_p )
    temp_p  = aim_p (i)
    if special >5
plot(All_fill_norm{1}(temp_p,22:36),'--','LineWidth',1)

    elseif special <=5
        subplot(2,1,1)
        plot(All_fill_norm{1}(temp_p,1:57),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm{2}(temp_p,1:57),'--','LineWidth',1)
        
    
    end
hold on
end


std(All_fill_norm_truen_pd(aim_n,22:36))
if special>5
    mean_temp  = [All_fill_norm_truen_pd(aim_n,22:36);All_fill_norm{1}(aim_p,22:36)]
    plot(mean(mean_temp ),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim_n,22:36)),std(All_fill_norm{1}(aim_n,22:36)),'LineWidth',2)
    xline(8);
elseif special <=5
    mean_temp = [All_fill_norm_truen_pd(aim_n,:);All_fill_norm{1}(aim_p,:)]
    subplot(2,1,1)
    plot([mean(mean_temp)],'LineWidth',2)
    %errorbar([1:57],[mean(All_fill_norm{1}(aim_n,:))],[std(All_fill_norm{1}(aim_n,:))],'LineWidth',2)
xline(29);
subplot(2,1,2)
mean_temp = [All_fill_norm_truen_ds(aim_n,:);All_fill_norm{2}(aim_p,:)]
 plot([mean(mean_temp)],'LineWidth',2)
 %errorbar([1:57],[mean(All_fill_norm{2}(aim_n,:))],[std(All_fill_norm{2}(aim_n,:))],'LineWidth',2)

end
title([name{special} ' Percentage : '  num2str(100*length(aim_n)/683) '%'])
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/cluster_28_7_ab_ver1_pnAll/' name{special} ' '  num2str(100*length(aim_n)/683) '%_s.png'])
close all
num = num+100*length(aim_n)/683
end
