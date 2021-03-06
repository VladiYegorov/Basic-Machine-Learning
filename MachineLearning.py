import numpy as np
import matplotlib.pyplot as plt
import gzip

import Helper as hp
import KNearestNeighbors as knn
import Perceptron as per
import SoftSVM_qp as svm_qp
import SoftSVM_sgd as svm_sgd
import CrossValidation as cv
import NaiveBayes as nb

#input for Naive Bayes learning and testing
input_csv_train = 'csv_data/iris.csv'
input_csv_test = 'csv_data/iris.csv'

#input for KNN, Perceptron and SVM learning and testing
input_mnist_data_train = 'mnist/train-images-idx3-ubyte.gz'
input_mnist_labels_train = 'mnist/train-labels-idx1-ubyte.gz'
input_mnist_data_test = 'mnist/t10k-images-idx3-ubyte.gz'
input_mnist_labels_test = 'mnist/t10k-labels-idx1-ubyte.gz'

#mnist variables
image_mnist_size = 28
num_mnist_images = 1000
num_mnist_test = 100

#cross validation variables
kFold_CV_Active = False
num_fold = 5

#parameters for classifiers
#tries all the list with cross validation
#default: the middle (len(classifierParam)//2)
kSet = [2,3,5]
maxUpdatesSet = [25,50,100]
softSVMconstSet = [1,5,10] 

#make mnist data binary.
twoNumOnly = False
num1 = 3    ## 1
num2 = 6    ## -1    

#load the necessary input files 
def loadDataAndLabels(size, alldata, classifierName = 'default'):
    #loading csv file from "csv_data" folder
    if classfierName == 'naiveBayes':
        dataset = hp.load_csv(alldata)
        labels = [x for x in np.array(dataset).T[-1]]
        data = [row[:-1] for row in dataset]
        return (data,labels)

    #loading mnist files from "mnist" folder
    Xtrain = gzip.open(alldata[0],'r')
    Ytrain = gzip.open(alldata[1],'r')
    Xtrain.read(16)
    imageBuf = Xtrain.read(image_mnist_size * image_mnist_size * size)
    data = np.frombuffer(imageBuf, dtype=np.uint8).astype(np.float32)
    data = data.reshape(size, image_mnist_size * image_mnist_size)
    Ytrain.read(8) 
    labelBuf = Ytrain.read(size)
    labels = np.frombuffer(labelBuf, dtype=np.uint8).astype(np.int64)
    
    #making mnist binary if needed
    if twoNumOnly == True:
        return hp.makeBinaryData(data,labels,num1,num2)

    return (data,labels)

#prepare the training data for the classfier and construct the classfier
def prepClassfier(classfier, predictFunc, classfierParam, classfierName = 'default', doCV = kFold_CV_Active):
    dataAndLabels = loadDataAndLabels(num_mnist_images,input_csv_train if classfierName == 'naiveBayes' else (input_mnist_data_train,input_mnist_labels_train),classfierName)
    if doCV == True:
        return cv.crossValidation(np.array(dataAndLabels[0]),np.array(dataAndLabels[1]),classfier,predictFunc,classfierParam,num_fold)
    return classfier(np.array(dataAndLabels[0]),np.array(dataAndLabels[1]),classfierParam[len(classfierParam)//2])

#preparing the testing data for the predictor and analyse the results
def prediction(classfier, predictFunc, classfierName = 'default'):
    dataAndLabels = loadDataAndLabels(num_mnist_test,input_csv_test if classfierName == 'naiveBayes' else (input_mnist_data_test,input_mnist_labels_test),classfierName)
    result = predictFunc(classfier,np.array(dataAndLabels[0]))
    analysis(np.array(dataAndLabels[1]),result)

def analysis(real_values, predicted_values):
    correct = 0
    total = 0
    for real, predicted in zip(real_values, predicted_values):
        total += 1
        if predicted == real:
            correct += 1
    print("The correct precentage is: ",1.*(correct/total)*100)
    print("correct: ",correct,", total: ",total)
    print()
    
def main():
    print("KNN:")
    classfier1 = prepClassfier(knn.learnknn,knn.predictknn,kSet,classfierName='knn')
    result1 = prediction(classfier1,knn.predictknn,'knn')

    print("Perceptron:")
    classfier2 = prepClassfier(per.perceptron,per.predictPerceptron,maxUpdatesSet,classfierName='perceptron')
    result2 = prediction(classfier2,per.predictPerceptron,'perceptron')

    print("softSVM-Quadratic Program:")
    classfier3 = prepClassfier(svm_qp.softSVM,svm_qp.predictSoftSVM,softSVMconstSet,classfierName='softSVM-qp')
    result3 = prediction(classfier3,svm_qp.predictSoftSVM,'softSVM-qp')

    print("softSVM-Stochastic Gradient Descent:")
    classfier4 = prepClassfier(svm_sgd.softSVM,svm_sgd.predictSoftSVM,softSVMconstSet,classfierName='softSVM')
    result4 = prediction(classfier4,svm_sgd.predictSoftSVM,'softSVM')

    print("Naive Bayes:")
    classfier5 = prepClassfier(nb.naiveBayes,nb.predictNB,[None],classfierName='naiveBayes')
    result5 = prediction(classfier5,nb.predictNB,'naiveBayes')

if __name__ == "__main__":
    main()
    
