       % constellation size = 2^modOrd
x = [0:1:52];
p = raylpdf(x,2);
figure;
plot(x,p)