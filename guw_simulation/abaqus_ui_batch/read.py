import gzip
import pickle
import matplotlib.pyplot as plt

path = 'D:\\GUW_clean_partitions\\GUW-NewMeshingTechnique\\guw_simulation\\bsp'
file_name = '{}\\{}.pkl.gz'.format(path, 'output_h')

with gzip.open(file_name, 'rb') as file:
    loaded_data = pickle.load(file, encoding='latin1')

for key in loaded_data.keys():
    print(loaded_data[key])
    data = loaded_data[key]
    print(data.shape)
    plt.plot(data[:, 0], data[:, 1])

plt.show()
