# -*- coding: utf-8 -*-
"""p2s2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/103DST7Bu6eQfJ34VmyCy9wqTEsMiKxKI
"""

import numpy as np 
import gzip
import matplotlib.pyplot as plt

## Handle the necessary imports


## Function to read the data from the compressed files
def read_data():
    train_images = gzip.open('train-images-idx3-ubyte.gz','r')
    train_labels = gzip.open('train-labels-idx1-ubyte.gz','r')
    image_size = 28
    num_images = 60000
    train_images.read(16)
    buffer = train_images.read(image_size * image_size * num_images)
    data_train_image = np.frombuffer(buffer, dtype=np.uint8).astype(np.float32)
    data_train_image = data_train_image.reshape(num_images, image_size, image_size, 1)
    y = [] 
    train_labels.read(8)
    for i in range(num_images):   
        buf = train_labels.read(1)
        labels = np.frombuffer(buf, dtype=np.uint8).astype(np.int64)
        y.append(labels[0])
    y = np.array(y)
    X = []
    for i in data_train_image:
        xi = np.asarray(i).squeeze()
        X.append(xi.flatten())
    X = np.array(X)
    return X, y

## Function to get subset of data with labels 2 and 9
def get_subset(X, y):
    indices = np.where((y == 2) | (y == 9))
    X_subset = X[indices]
    y_subset = y[indices]
    return X_subset, y_subset

## In case you need the whole data, use this:
X, y = read_data()

## In case you need the subset of data with classes 2 and 9 use this:
X_subset, y_subset = get_subset(X, y)

np.save("train_images_subset.npy", X_subset)
np.save("train_labels_subset.npy", y_subset)

np.save("train_images.npy", X)
np.save("train_labels.npy", y)

X,Y=read_data()
print("Input shape X: " +str(X_subset.shape),"Input shape Y: "+str(y_subset.shape))

#diaplaying random example from dataset
img_dim=int(np.sqrt(X_subset.shape[1]))
def display_example():
    ind = np.random.randint(X_subset.shape[0]) #random index
    img = X_subset[ind].reshape(img_dim,img_dim)
    print(img)
    print("Number is:", y_subset[ind])
    plt.imshow(img)
display_example()

def normalize_X(data):
    mean = np.mean(data, axis=1, keepdims=True)

    std = np.std(data, axis=1, keepdims=True)
    normalized_data = (data - mean)/std
    return normalized_data

X=normalize_X(X_subset)

Y=np.floor(y_subset/5)  #to represent 2 as 0 and 9 as 1; can be obtained by dividing values of y with the point midway between both classes
shuffler = np.random.permutation(X.shape[0]) #shuffling dataset
X = X[shuffler]
Y = Y[shuffler]

X_train=X[:int(X.shape[0]*0.8),:].T      #0.8 to obtain 80:20 train:test ratio
Y_train=Y.reshape(Y.shape[0],1)[:int(Y.shape[0]*0.8),:].T
X_test=X[int(X.shape[0]*0.8):,:].T
Y_test=Y.reshape(Y.shape[0],1)[int(Y.shape[0]*0.8):,:].T
print("Shape of X_train: "+str(X_train.shape))
print("Shape of Y_train: "+str(Y_train.shape))
print("Shape of X_test: "+str(X_test.shape))
print("Shape of y_test: "+str(Y_test.shape))

def sigmoid(z):
    s = 1/(1+np.exp(-z))
    return s

def initialize_zero_parameters(dim):

    w = np.zeros((dim,1))
    b = 0
    
    return w, b

"""# Ridge/L2 regularization"""

def compute_cost(a3, Y):
    m = Y.shape[1]
    cost = np.sum(((- np.log(a3))*Y + (-np.log(1-a3))*(1-Y)))/m
    return cost
def compute_cost_with_l2_regularization(A3, Y, w, lambd):
    m = Y.shape[1]
    original_cost = compute_cost(A3, Y)
    ridge_regularization_cost = lambd/(2*m)*(np.sum(np.square(w)))
    cost = original_cost + ridge_regularization_cost  
    return cost

def forward_and_backward_propagate_l2(w, b, X, Y,lambd):  
    m = X.shape[1]
    
    # forward propagation
    A = sigmoid(np.dot(w.T,X) + b)              # computing activation
    cost=compute_cost_with_l2_regularization(A, Y, w, lambd)
    # bacward propagation
    dw = 1./m * np.dot(X,(A-Y).T) + (lambd/m)*w
    db = (np.sum(A-Y))/m


    cost = np.squeeze(cost)

    
    grads = {"dw": dw,
             "db": db}
    
    return grads, cost

def iteration_l2(w, b, X, Y, num_iterations, learning_rate, lambd):
    costs = []
    
    for i in range(num_iterations):
        grads, cost = forward_and_backward_propagate_l2(w, b, X, Y,lambd)

        dw = grads["dw"]
        db = grads["db"]
        
        # updation
 
        w = w - (learning_rate*dw)
        b = b - (learning_rate*db)

        # Record the costs
        #if i % 15 == 0:
        costs.append(cost)
    
    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, costs

def prediction(w, b, X):
    m = X.shape[1]
    Y_prediction = np.zeros((1,m))
    w = w.reshape(X.shape[0], 1)
    
    # predicting wheter image is 2 or 9
    A = sigmoid(np.dot(w.T,X) + b)           
    Y_prediction = (A >= 0.5) * 1.0    
    return Y_prediction

def model_l2(X_train, Y_train, X_test, Y_test, lambd,num_iterations, learning_rate = 0.5):
    
    # initializing parameters
    w, b = initialize_zero_parameters(X_train.shape[0])

    # Gradient descent
    parameters, grads, costs = iteration_l2(w, b, X_train, Y_train, num_iterations, learning_rate, lambd)
    
    # obtainig trained parameters
    w = parameters["w"]
    b = parameters["b"]
    
    # Predict test/train set examples
    Y_prediction_test = prediction(w, b, X_test)
    Y_prediction_train = prediction(w, b, X_train)


    # Print train/test Errors
    print("train accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_train - Y_train)) * 100))
    print("test accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_test - Y_test)) * 100))

    
    d = {"costs": costs,
         "Y_prediction_test": Y_prediction_test, 
         "Y_prediction_train" : Y_prediction_train, 
         "w" : w, 
         "b" : b,
         "learning_rate" : learning_rate,
         "num_iterations": num_iterations}
    
    return d

d_l2 = model_l2(X_train, Y_train, X_test,Y_test, 0.1,20, learning_rate = 0.5)

index = 80
plt.imshow(X_test[:,index].reshape((28, 28)))
a1=2 if Y_test[0,index]==0.0 else 9
a2=2 if d_l2["Y_prediction_test"][0,index]==0.0 else 9
print ("y = " + str(a1) + ", model's prediction is \"" + str(a2) +  "\" picture.")

costs = np.squeeze(d_l2['costs'])
plt.plot(costs)
plt.ylabel('cost')
plt.xlabel('iterations')
plt.show()

print("trained w parameter for ridge regularization:")
print(d_l2["w"])
print("trained b parameter for ridge regularization:")
print(d_l2["b"])

"""# Lasso/L1 regularization"""

def compute_cost_l1(a3, Y):
    m = Y.shape[1]
    cost = np.sum(((- np.log(a3))*Y + (-np.log(1-a3))*(1-Y)))/m
    return cost
def compute_cost_with_l1_regularization(A3, Y, w, lambd):
    m = Y.shape[1]
    original_cost = compute_cost_l1(A3, Y) 
    L1_regularization_cost = lambd/(2*m)*(np.sum(abs(w)))
    cost = original_cost + L1_regularization_cost
    
    return cost

def forward_and_backward_propagate_l1(w, b, X, Y,lambd):  
    m = X.shape[1]
    
    # forward propagation
    A = sigmoid(np.dot(w.T,X) + b)              # computing activation
    cost=compute_cost_with_l1_regularization(A, Y, w, lambd)
    # backward propagation
    dw = 1./m * np.dot(X,(A-Y).T) + (lambd/(2*m))
    db = (np.sum(A-Y))/m
    cost = np.squeeze(cost)
    grads = {"dw": dw,
             "db": db}
    
    return grads, cost

def iteration_l1(w, b, X, Y, num_iterations, learning_rate, lambd):
    costs = []
    
    for i in range(num_iterations):
        
        
        # Cost and gradient calculation
        grads, cost = forward_and_backward_propagate_l1(w, b, X, Y,lambd)

        dw = grads["dw"]
        db = grads["db"]
        
        # updation
 
        w = w - (learning_rate*dw)
        b = b - (learning_rate*db)

        # Record the costs
        if i % 5 == 0:
            costs.append(cost)
    
    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, costs

def model_l1(X_train, Y_train, X_test, Y_test, lambd,num_iterations, learning_rate = 0.01):
    
    # initializing parameters
    w, b = initialize_zero_parameters(X_train.shape[0])

    # Gradient descent
    parameters, grads, costs = iteration_l1(w, b, X_train, Y_train, num_iterations, learning_rate, lambd)
    
    # obtaining trained parameters
    w = parameters["w"]
    b = parameters["b"]
    
    # Predict test/train set examples
    Y_prediction_test = prediction(w, b, X_test)
    Y_prediction_train = prediction(w, b, X_train)


    # Print train/test Errors
    print("train accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_train - Y_train)) * 100))
    print("test accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_test - Y_test)) * 100))

    
    d = {"costs": costs,
         "Y_prediction_test": Y_prediction_test, 
         "Y_prediction_train" : Y_prediction_train, 
         "w" : w, 
         "b" : b,
         "learning_rate" : learning_rate,
         "num_iterations": num_iterations}
    
    return d

d_l1 = model_l1(X_train, Y_train, X_test,Y_test, 0.1,50, learning_rate = 0.01)

index = 70
plt.imshow(X_test[:,index].reshape((28, 28)))
a1=2 if Y_test[0,index]==0.0 else 9
a2=2 if d_l2["Y_prediction_test"][0,index]==0.0 else 9
print ("y = " + str(a1) + ", model's prediction is \"" + str(a2) +  "\" picture.")

costs = np.squeeze(d_l1['costs'])
plt.plot(costs)
plt.ylabel('cost')
plt.xlabel('iterations')
plt.show()

print("trained w parameter for lasso regularization:")
print(d_l1["w"])
print("trained b parameter for lasso regularization:")
print(d_l1["b"])