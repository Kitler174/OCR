# keras.datasets.mnist.load_data(path="mnist.npz")
# https://keras.io/api/datasets/mnist/
# https://learn.microsoft.com/pl-pl/azure/open-datasets/dataset-mnist?tabs=azureml-opendatasets

import keras
from  tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data/', one_hot=True)