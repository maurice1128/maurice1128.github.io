name = string(All_fill_header{2}(:));

% 每個值出現次數
[u, ~, idx] = unique(name, 'stable');
cnt = accumarray(idx, 1);

T = table(u, cnt, 'VariableNames', {'Value','Count'});
T = sortrows(T, 'Count', 'descend');
disp(T);

% counts 的描述統計（這是「每個類別出現次數」的分布）
med_cnt = median(cnt);
q1_cnt  = prctile(cnt, 25);
q3_cnt  = prctile(cnt, 75);
min_cnt = min(cnt);
max_cnt = max(cnt);

fprintf('Count per unique value: median (IQR) = %.1f (%.1f–%.1f), min–max = %d–%d\n', ...
    med_cnt, q1_cnt, q3_cnt, min_cnt, max_cnt);
