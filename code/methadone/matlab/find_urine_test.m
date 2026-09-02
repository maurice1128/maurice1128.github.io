clear all
close all
clc

name = []
temp = []
for i =1:538
name =[name list_sorted{i}{1,2}];
end


C = readcell("<LOCAL_DATA_PATH>","Sheet","初診","Range","C2:X11532");
data = C(:,[1,17,20,22]);