from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt

in_x = np.linspace(500, 1000, num=101, endpoint=True)
in_y = np.cos(-in_x**2/9.0)
# print("%s" % in_y)

f2 = interp1d(in_x, in_y, kind='cubic', bounds_error=False, fill_value=-1)

out_x = np.linspace(0, 1000, num=10001, endpoint=True)
out_y = f2(out_x)
# print("%s" % x)

plt.plot(in_x, in_y, 'o', out_x, out_y, '--')
plt.show()
