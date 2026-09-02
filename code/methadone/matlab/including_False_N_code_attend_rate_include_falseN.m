clear all
clc
close all

load('aim2.mat')



Positive = All_raw_fix{1}(:,22:29)
Negative = All_raw_fix{3}(:,22:29)
%%
temp = [];
record_p = [];
for i  = 1:length(Positive)
temp = find(Positive(i,:) ==-1)
record_p = [record_p;length(temp)];
end
temp = [];
record_n = [];
for i  = 1:length(Negative)
temp = find(Negative(i,:) ==-1)
record_n = [record_n;length(temp)];
end
histogram(record_p,'Normalization','probability')
hold on
histogram(record_n,'Normalization','probability')

%%
temp = [];
record_p = [];
for i  = 1:length(Positive)
temp = find(Positive(i,:) ==-1)
if length(temp)==0
record_p = [record_p;1];
else
record_p = [record_p;0]; 
end
end
temp = [];
record_n = [];
for i  = 1:length(Negative)
temp = find(Negative(i,:) ==-1)
if length(temp)==0
record_n = [record_n;1];
else
record_n = [record_n;0];  
end

end
close all
subplot(1,2,1)
histogram(record_p,'Normalization','probability')
subplot(1,2,2)
histogram(record_n,'Normalization','probability')




