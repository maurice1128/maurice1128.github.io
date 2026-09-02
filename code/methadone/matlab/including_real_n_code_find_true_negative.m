%%
clear all
close all
clc
load('aim2.mat')
negative_header = All_fill_header{3};
negative_date = All_fill_date{3};
C = readcell("/Users/mauricewang/Desktop/mesodon_code/Excel/陪同驗尿的名單.xlsx","Sheet","有驗尿陪同的名單","Range","B2:D505");
dataID = C(:,[1]);
dataID = cell2mat(dataID);
data_date = [];
for i = 1:length(C)

data_date =[data_date;C{i,[2,3]}]
end


%%

location_patient = [];
for i  = 1:length(data_date)

start_d = data_date(i,1)
start_e = data_date(i,2)

location_patient = [location_patient,find(negative_header==dataID(i)& negative_date <=start_e&negative_date >start_d)]

end


negative_header(location_patient)
negative_date(location_patient)
real_negative = location_patient;
save("aim2.mat","real_negative",'-append')




%%
save('real_n_location.mat','real_negative')
