% Create the Polar Histogram for Minimum Slopes
p_min = polarhistogram(thetamin, 30);

% Professional Styling (Consistent with thetamax)
p_min.FaceColor = [0.8500, 0.3250, 0.0980]; % Using a professional orange/red to distinguish from max
p_min.FaceAlpha = 0.6; 
p_min.EdgeColor = 'w'; % White edges for clarity

% Title - Specifying the theta_min feature
title({'Directional Distribution of Minimum Dosage Slopes (\theta_{min})', ...
       'Radial Axis: Frequency (UDS Events)'}, ...
      'FontSize', 13, 'FontWeight', 'bold');

% Format the Polar Axes
ax = gca;
ax.ThetaDir = 'clockwise'; 
ax.ThetaZeroLocation = 'top'; 
ax.FontSize = 10;
ax.GridAlpha = 0.3;

% Manual label for the radial axis
max_r = ax.RLim(2);
text(deg2rad(95), max_r * 0.7, 'Frequency', ...
    'FontSize', 10, 'FontWeight', 'bold', 'Rotation', -90);
shg