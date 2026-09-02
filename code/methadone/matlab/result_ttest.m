%%
clear all
clc
close all

percent_positive =0.050
percent_negative = 0.049


positive_result  =zeros(3401,1)
temp_p = ones(round(3401*percent_positive),1)
positive_result(1:length(temp_p),1) = temp_p

negative_result = zeros(683,1)
temp_n  = ones(round(683*percent_negative),1)
negative_result(1:length(temp_n),1) = temp_n
