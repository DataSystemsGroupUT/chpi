import pandas as pd 
import numpy as np
import os
import glob
import warnings
import time
from sklearn.cluster import KMeans
URL=os.path.join( os.getcwd(), 'datasets/iris.csv' )  
df=pd.read_csv(URL)
print(df.head())

N= 10
params_kmeans={
"n_clusters": np.random.uniform(2,40,N),
"init": ['k-means++','random'],
"max_iter": np.random.choice(np.arange(100, 501, 1), N),
"algorithm": ['auto' 'full', 'elkan'],
"n_init": np.random.choice(np.arange(2, 21, 1), N),
}


parameters ={
    'Kmeans':params_kmeans,
}

models = {
    'Kmeans': KMeans(),

}







def clusering_per_algorithm(path, algorithm):
    """ Fit diffrent model across many datasets

    Keyword Arguments:
        path {str} -- [description] (default: {""})
        algorithm {str} -- [description] (default: {"kmeans"})
    """
    warnings.filterwarnings("ignore")
    all_files = glob.glob(path + '*.csv')
    all_datasets = len(all_files)
    

    results = pd.DataFrame()
    start_all = time.perf_counter()

    for index, file in enumerate(all_files):
        print('Dataset {}({}) out of {} \n'.format(index + 1, file, all_datasets), flush=True)
        try:
            file_logs = clustering_per_dataset(file, algorithm, models, parameters)
            results = pd.concat([results, file_logs], axis=0)

            results.to_csv('{}_results.csv'.format(algorithm),
                            header=True,
                            index=False)
        except Exception as e:
            print('The following error occurred in case of the dataset {}: \n{}'.format(file, e))
    end_all = time.perf_counter()
    time_taken = (end_all - start_all) / 3600
    stdout.write("Performance data is collected! \n ")
    print('Total time: {} hours'.format(time_taken))


def clustering_per_dataset(file,algorithm, models,parameters):
    """
    Obtaining performance information for each random configuration on the given dataset for the specific clustering algorithm.

    Arguments:
        file {[str]} -- [description]
        algorithm {[type]} -- [description]
        models {[type]} -- [description]
        parameters {[type]} -- [description]
    """
    data = pd.read_csv(file,
                index_col=None,
                header=0,
                na_values='?')
    # making the column names lower case
    data.columns = map(str.lower, data.columns)          

    # removing an id column if exists
    if 'id' in data.columns:
        data = data.drop('id', 1)

    # remove columns with only NaN values
    empty_cols = ~data.isna().all()
    data = data.loc[:, empty_cols]

    # identifying numerical and categorical features
    cols = set(data.columns)
    num_cols = set(data._get_numeric_data().columns)
    categorical_cols = list(cols.difference(num_cols))

    # data imputation for categorical features
    categ_data = data[categorical_cols]
    data[categorical_cols] = categ_data.fillna(categ_data.mode().iloc[0])

    # defining the random configurations
    combinations = get_combinations(parameters, algorithm)

    # data imputation for numeric features
    if data.isna().values.any():

        imputation_types = ['mean', 'median', 'mode']

        final_logs = pd.DataFrame()
        
        imputed_data = data.copy()

        for index, num_imput_type in enumerate(imputation_types):
            print('{}'.format(num_imput_type))

            imputed_data[list(num_cols)] = numeric_impute(data, num_cols, num_imput_type)

            # logs per imputation method
            logs = get_logs(imputed_data, num_imput_type, algorithm,
                            file, combinations, models)

            final_logs = pd.concat([final_logs, logs], axis=0)

    else:
        num_imput_type = None

        final_logs = get_logs(data, num_imput_type, algorithm,
                            file, combinations, models)

    return final_logs


def get_logs(data, num_imput_type, algorithm, file, combinations, models):
    """
    Gathers the performance data for each random configuration 
    on the given dataset for the specified ML algorithm
    
    Inputs:
            data - (DataFrame) dataset, where the last column 
                               contains the response variable 
            num_imput_type - (str or None) imputation type that takes 
                              one of the following values
                              {'mean', 'median', 'mode', None}
            
            algorithm - (str) takes one of the following options
                        {RandomForest, AdaBoost, ExtraTrees, 
                         SVM, GradientBoosting}
            file - (str) name of the dataset
            
            combinations - (DataFrame) contains the random configurations
                            of the given algorithm
            
            models - (dict) key: algorithm, 
                            value: the class of the algorithms
            
    Outputs: 
            logs - (DataFrame) performance data
            
    """
    # excluding the response variable
    X = data.iloc[:, :-1]

    # selecting the response variable
    y = data.iloc[:, -1]

    # one-hot encoding
    X = pd.get_dummies(X)

    le = LabelEncoder()
    y = le.fit_transform(y)

    num_labels = len(np.unique(y))

    # binarizing the labels for some of the metrics
    # in case of more than 2 labels
    if num_labels > 2:
        multilabel = True
        lb = LabelBinarizer()
        lb.fit(y)
        y_sparse = lb.transform(y)
    else:
        multilabel = False

    # scaling the input in case of SVM algorithm
    if algorithm == 'SVM':
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        scaled = True
    else:
        scaled = False

    # setting the number of folds of the Cross-Validation
    k = 10
    kf = StratifiedKFold(n_splits=k, shuffle=True)

    logs = combinations.copy()
    n_comb = logs.shape[0]
    logs.insert(loc=0, column='dataset', value=file)
    logs['imputation'] = num_imput_type

    for index in range(n_comb):
        print('{}/{}'.format(index + 1, n_comb))
        
        params = dict(zip(combinations.columns,
                      list(combinations.iloc[index,:])))
        
        model = models[algorithm]
        model.set_params(**params)

        i = 0

        cv_train_time = np.zeros(k)
        cv_test_time = np.zeros(k)
        acc_tr = np.zeros(k)
        accuracy = np.zeros(k)
        f1 = np.zeros(k)
        recall = np.zeros(k)
        precision = np.zeros(k)
        auc = np.zeros(k)

        for train_index, test_index in kf.split(X, y):
            stdout.write("\rCV {}/{}".format(i+1, k))

            if not scaled:
                X_train, X_test = X.iloc[train_index, :], X.iloc[test_index, :]
            else:
                X_train, X_test = X[train_index, :], X[test_index, :]
            
            y_train, y_test = y[train_index], y[test_index]

            start_tr = time.perf_counter()
            model.fit(X_train, y_train)
            end_tr = time.perf_counter()
            train_time = end_tr - start_tr

            predictions_tr = model.predict(X_train)
            acc_tr[i] = accuracy_score(y_train, predictions_tr)
            start_ts = time.perf_counter()
            predictions = model.predict(X_test)
            end_ts = time.perf_counter()
            test_time = end_ts - start_ts
            cv_train_time[i] = train_time
            cv_test_time[i] = test_time
            accuracy[i] = accuracy_score(y_test, predictions)

            if multilabel:
                y_true = y_sparse[test_index, :]
                predictions = lb.transform(predictions)
            else:
                y_true = y_test

            f1[i], recall[i], precision[i], auc[i] = other_metrics(y_true,
                                                                   predictions,
                                                                   multilabel)
            i += 1

            stdout.flush()

        logs.loc[index, "Mean_Train_time"] = np.mean(cv_train_time)
        logs.loc[index, "Std_Train_time"] = np.std(cv_train_time)
        logs.loc[index, "Mean_Test_time"] = np.mean(cv_test_time)
        logs.loc[index, "Std_Test_time"] = np.std(cv_test_time)
        logs.loc[index, 'CV_accuracy_train'] = np.mean(acc_tr)
        logs.loc[index, 'CV_accuracy'] = np.mean(accuracy)
        logs.loc[index, 'CV_f1_score'] = np.mean(f1)
        logs.loc[index, 'CV_recall'] = np.mean(recall)
        logs.loc[index, 'CV_precision'] = np.mean(precision)
        logs.loc[index, 'CV_auc'] = np.mean(auc)
        logs.loc[index, 'Std_accuracy_train'] = np.std(acc_tr)
        logs.loc[index, 'Std_accuracy'] = np.std(accuracy)
        logs.loc[index, 'Std_f1_score'] = np.std(f1)
        logs.loc[index, 'Std_recall'] = np.std(recall)
        logs.loc[index, 'Std_precision'] = np.std(precision)
        logs.loc[index, 'Std_auc'] = np.std(auc)

        print('\n')

    return logs


def get_combinations(parameters, algorithm):
    """
    Creates a DataFrame of the random configurations
    of the given algorithm
    
    Inputs:
            parameters - (dict) key: algorithm
                                value: the configuration space of 
                                       the algorithm
            algorithm - (str) takes one of the following options
                        {RandomForest, AdaBoost, ExtraTrees, 
                         SVM, GradientBoosting}
            
    Outputs: 
            combinations - (DataFrame) realizations of the 
                            random configurations
            
    """
    param_grid = parameters[algorithm]
    combinations = pd.DataFrame(param_grid)
    return combinations


def other_metrics(y_true, predictions, multilabel):
    """
    Treating the case of multiple labels for 
    computing performance measures suitable for 
    binary labels
    
    Inputs:
            y_true - (array or sparse matrix) true values of the 
                      labels
            predictions - (array or sparse matrix) predicted values of the 
                      labels 
            multilabel - (boolean) specifies if there are 
                          multiple labels (True)
    Outputs: 
            f1, recall, precision, auc - (float) performace metrics
            
    """
    
    if multilabel:
        f1 = f1_score(y_true, predictions, average='micro')
        recall = recall_score(y_true, predictions, average='micro')
        precision = precision_score(y_true, predictions, average='micro')
        auc = roc_auc_score(y_true, predictions, average='micro')
    else:
        f1 = f1_score(y_true, predictions)
        recall = recall_score(y_true, predictions)
        precision = precision_score(y_true, predictions)
        auc = roc_auc_score(y_true, predictions)

    return f1, recall, precision, auc


def numeric_impute(data, num_cols, method):
    """
    Performs numerical data imputaion based 
    on the given method
    
    Inputs:
            data - (DataFrame) dataset with missing 
                     numeric values 
            num_cols - (set) numeric column names
            method - (str) imputation type that takes 
                              one of the following values
                              {'mean', 'median', 'mode'}
            
    Outputs: 
            output - (DataFrame) dataset with imputed missing values 
            
    """
    num_data = data[list(num_cols)]
    if method == 'mode':
        output = num_data.fillna(getattr(num_data, method)().iloc[0])
    else:
        output = num_data.fillna(getattr(num_data, method)())
    return output