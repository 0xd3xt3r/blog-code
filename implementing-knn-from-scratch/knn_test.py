import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.preprocessing import MinMaxScaler
from knn import KnnClassifier, get_accuracy
# load the iris data set
iris = datasets.load_iris()
knn_iris_acc = []
X = iris.data
y = iris.target

scale = MinMaxScaler()
X = scale.fit_transform(X)
for k in range(2, len(iris.data)):
    clf = KnnClassifier(k)
    clf.fit(X, y)
    iris_pred = []
    for x in X:
        pred = clf.predict(x)
        iris_pred.append(pred)
    iris_target_pred = np.array(iris_pred)
    knn_iris_acc.append(get_accuracy(iris_target_pred, iris.target))

plt.plot(range(2,len(iris.data)), knn_iris_acc)
plt.xlabel('Number of neighbours')
plt.ylabel('Accuracy')
plt.grid()
plt.show()
