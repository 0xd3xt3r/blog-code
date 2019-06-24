import math
from sklearn import datasets
iris = datasets.load_iris()
import operator

# we only take the first two features. We could avoid this ugly
# slicing by using a two-dim dataset
X = iris.data[:, :2]
y = iris.target

class KnnBase(object):
    def __init__(self, k, weights=None, debug=False):
        self.k = k
        self.weights = weights
        self.debug = debug

    def euclidean_distance(self, data_point1, data_point2):
        if len(data_point1) != len(data_point2) :
            raise ValueError('feature length not matching')
        else:
            distance = 0
            for x in range(len(data_point1)):
                distance += pow((data_point1[x] - data_point2[x]), 2)
            return math.sqrt(distance)
    def fit(self, train_feature, train_label):
        self.train_feature = train_feature
        self.train_label = train_label

    def get_neighbors(self, train_set_data_points, test_feature_data_point, k):
    	distances = []
    	length = len(test_feature_data_point)-1
    	for index in range(len(train_set_data_points)):
    		dist = self.euclidean_distance(test_feature_data_point, train_set_data_points[index])
    		distances.append((train_set_data_points[index], dist, index))
    	distances.sort(key=operator.itemgetter(1))
    	neighbors = []
    	for index in range(k):
    		neighbors.append(distances[index][2])
    	return neighbors

class KnnRegression(KnnBase):

    def predict(self, test_feature_data_point):
        nearest_data_point_index = self.get_neighbors(self.train_feature, test_feature_data_point, self.k)
        total_val = 0.0
        # calculate the sum of all the label values
        for index in nearest_data_point_index:
            total_val += self.train_set_data_points[index]

        return total_val/self.k

class KnnClassifier(KnnBase):

    def predict(self, test_feature_data_point):
        # get the index of all nearest neighbouring data points
        nearest_data_point_index = self.get_neighbors(self.train_feature, test_feature_data_point, self.k)
        vote_counter = {}
        # to count votes for each class initialize all class with zero votes
        if self.debug:
            print('Nearest Data point index ', nearest_data_point_index)
        for label in set(self.train_label):
            vote_counter[label] = 0
        # add count to class that are present in the nearest neighbors data points
        for class_index in nearest_data_point_index:
            closest_lable = self.train_label[class_index]
            vote_counter[closest_lable] += 1
            if self.debug:
                print('Nearest data point count', vote_counter)
        # return the class that has most votes
        return max(vote_counter.items(), key = operator.itemgetter(1))[0]

def get_accuracy(y, y_pred):
	cnt = (y == y_pred).sum()
	return round(cnt/len(y), 2)

def get_rmse(y, y_pred):
    '''Root Mean Square Error
    https://en.wikipedia.org/wiki/Root-mean-square_deviation
    '''
    mse = np.mean((y - y_pred)**2)
    return np.sqrt(mse)

def get_mape(y, y_pred):
    '''Mean Absolute Percent Error
    https://en.wikipedia.org/wiki/Mean_absolute_percentage_error
    '''
    perc_err = (100*(y - y_pred))/y
    return np.mean(abs(perc_err))
