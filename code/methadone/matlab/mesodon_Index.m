clear all
close all
clc
load('aim.mat')

%%
%可疑指數-5~5
aim = {{positive_pd};{positive_ds};{negative_pd};{negative_ds}};
Index_positive = [];
Index_negative = [];
for np = [1,3]
    pd = cell2mat(aim{np});
    ds = cell2mat(aim{np+1});
for i = 1:length(ds)
    i
    index = 0;
    location = -1;
    temp_pd = pd(i,:);
    temp_ds = ds(i,:);
    find(Index_negative == 0)


    %% 檢查驗尿前的沒來次數
    location = find(temp_pd(1:29)==-1)
     %一個禮拜內沒來可疑5，兩個禮拜內沒來2
    if max(location)>=22
    index = index+1
%     elseif max(location)>=15
%         index = index+2
    end



    

    location = find(temp_pd(1:57)==-1)
    trend_pd = temp_pd
    trend_pd(location) = [];
    trend_ds = temp_ds;
    trend_ds(location) = [];
   x = [1:57]
   x(location) = [];

    %% 檢查是否pd =ds->如果是14天前才開始的再算
%     count_eqpdds = 0
%     for k = 8:29
%         if temp_pd(k) ==temp_ds(k)& temp_pd~=-1
%             count_eqpdds = count_eqpdds+1
%         end
%     end
% 
% index = count_eqpdds;

%%  trend index
a = polyfit(x,trend_pd,1);
index = a(1)

index = std(trend_pd)

%% record data
%     
 if np==1 & max(temp_pd)<=100
    Index_positive = [Index_positive,index];
 elseif np==3 & max(temp_pd)<=100
    Index_negative = [Index_negative,index];
    end
end

end
Index_positive = Index_positive';
Index_negative = Index_negative';
close all
histogram(Index_negative,'Normalization','probability')
hold on
histogram(Index_positive,'Normalization','probability')
legend({'Negative','Positve'})
% close all
% subplot(2,1,1)
% histogram(Index_negative,'Normalization','probability')
% subplot(2,1,2)
% histogram(Index_positive,'Normalization','probability')


%%
location = find(Index_negative<0);
a = length(location)
location = find(Index_negative>0);
b = length(location)
result = [a/b];
location = find(Index_negative==0);
c = length(location)

location = find(Index_positive<0);
a = length(location)
location = find(Index_positive>0);
b = length(location)
location = find(Index_positive==0);
c = length(location)

result = [result;a/b]

b/c
a/c


