% script to generate trusted values to be used with GSW

disp('SA:');
SA = [34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324];
disp(SA);

disp('CT:');
CT = [28.8099, 28.4392, 22.7862, 10.2262,  6.8272,  4.3236];
disp(CT);

disp('p:');
p = [10.0, 50.0, 125.0, 250.0, 600.0, 1000.0];
disp(p);

disp('p_ref:');
p_ref = 0.0;
disp(p_ref);

disp('dynamic height:');
dh = gsw_geo_strf_dyn_height(SA, CT, p, p_ref);
disp(dh);