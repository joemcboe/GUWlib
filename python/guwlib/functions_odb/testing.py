import numpy as np
import matplotlib.pyplot as plt

# Load the npz file

my_file = 'C:\\Users\\joern\\Documents\\GitLab\\GUW\\python\\results\\small\\lc_0_lc1\\small_lc_0_lc1.npz'

data = np.load(my_file)

# Access individual arrays using keys
for key in data.keys():
    print(key)
    for i in [1, 2, 3]:
        plt.plot(data[key][0, :], data[key][i, :])
    plt.show()

# Close the file after loading the data
data.close()
