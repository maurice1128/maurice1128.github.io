% Generate the 3D Bivariate Histogram
hist3([thetamax, thetamin], 'CDataMode', 'auto', 'FaceColor', 'interp', 'Nbins', [50, 50]);

% Set the colormap to something professional and high-contrast
colormap(parula); % 'parula' or 'viridis' are excellent for publications
colorbar; % Add a color bar to indicate frequency density

% Labels and Title
title('Bivariate Angular Distribution of Methadone Dosage Dynamics', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('\theta_{max} (Maximum Slope Angle)', 'FontSize', 12);
ylabel('\theta_{min} (Minimum Slope Angle)', 'FontSize', 12);
zlabel('Frequency (UDS Events)', 'FontSize', 12);

% Formatting the Axes
grid on;
set(gca, 'FontSize', 10); % Set base font size for ticks

% Adjusting the View
% A 3D view is good, but sometimes a 2D top-down view (Heatmap style) 
% shows the "12 Clusters" more clearly.
view(3); % Change to view(2) if you want a top-down heatmap view

% Optional: Set axis limits if your angles are normalized (e.g., 0 to 2pi or 0 to 360)
% xlim([0 360]); ylim([0 360]);