import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import silhouette_score

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_scatter_plot(x, y, c_x, c_y, Y_d, n_cluster, main_cmap=None):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    name = 'Customer Groups for n = ' + str(n_cluster)
    plt.title(name)
    plt.scatter(x, y, c=Y_d.labels_.astype(float), cmap=main_cmap)
    plt.scatter(c_x, c_y, s=100, c='cyan', label='Centroids')
    plt.xticks(rotation=45)
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.tight_layout()
    graph = get_graph()
    return graph


def get_elbow_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.plot(x, y, color='#722f59')
    plt.scatter(x, y)
    plt.title('Elbow Graph', fontweight='bold')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.tight_layout()
    graph = get_graph()
    return graph


def get_bar_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    plt.title('Silhouette Score', fontweight='bold')
    plt.bar(x, y, align='center', color='#722f59', width=0.5)
    plt.xticks(x, list(parameters))
    plt.xlabel('Number of Clusters')
    plt.ylabel('Score')
    plt.tight_layout()
    graph = get_graph()
    return graph

def process_data(csv_dataframe, user_ncluster):
    customer_data = csv_dataframe
    string_columns = []
    for key, value in dict(customer_data.dtypes).items():
        if value == "object":
            string_columns.append(key)
    missing_value_dict = dict(customer_data.isnull().sum())
    for key, val in missing_value_dict.items():
        if val != 0:
            customer_data[key].mode()
            customer_data[key] = customer_data[key].fillna(customer_data[key].mode()[0])

    # One Hot encoding
    # Performing One Hot Encoding for all Attributes
    customer_data_new = pd.get_dummies(customer_data, columns=string_columns, prefix="New")
    extension_list = []
    for i in range(1, customer_data_new.shape[1]):
        extension_list.append(i)

    # Choosing 1 to length of new-list columns
    X = customer_data_new.iloc[:, extension_list].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    pca_2 = PCA(n_components=2)
    X_scaled = pca_2.fit_transform(X)

    # candidate values for our number of cluster
    global parameters, silhouette_scores, inertia_list
    parameters = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    # instantiating ParameterGrid, pass number of clusters as input
    parameter_grid = ParameterGrid({'n_clusters': parameters})
    best_score = -1
    kmeans_model = KMeans()  # instantiating KMeans model
    silhouette_scores = []
    inertia_list = []
    # evaluation based on silhouette_score
    for p in parameter_grid:
        kmeans_model.set_params(**p)  # set current hyper parameter
        kmeans_model.fit(X_scaled)  # fit model on dataset, this will find clusters based on parameter p
        ss = silhouette_score(X_scaled, kmeans_model.labels_)  # calculate silhouette_score
        silhouette_scores += [ss]  # store all the scores
        inertia_list.append(kmeans_model.inertia_)
        # check p which has the best score
        if ss > best_score:
            best_score = ss
            best_grid = p
    # plotting silhouette score
    silhouette_score_graph = get_bar_plot(range(parameters[0],len(silhouette_scores)+parameters[0]), list(silhouette_scores))
    elbow_graph = get_elbow_plot(range(parameters[0],len(inertia_list)+parameters[0]), list(inertia_list))
    if user_ncluster<1:
        n_cluster = best_grid['n_clusters']
    else:
        n_cluster = user_ncluster

    main_kmeans = KMeans(n_clusters=n_cluster)
    Y = main_kmeans.fit(X_scaled)
    labels = main_kmeans.labels_
    cluster_graph = get_scatter_plot(X_scaled[:, 0], X_scaled[:, 1], main_kmeans.cluster_centers_[:, 0], main_kmeans.cluster_centers_[:, 1], Y, n_cluster, "plasma")

    graph_item = [0 for i in range(len(parameters))]
    for j in range(len(parameters)):
        kmeans = KMeans(n_clusters=parameters[j])
        Y = kmeans.fit(X_scaled)
        graph_item[j] = get_scatter_plot(X_scaled[:, 0], X_scaled[:, 1], kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], Y, parameters[j])
    graph_list = [silhouette_score_graph, cluster_graph, elbow_graph, labels, graph_item]
    return graph_list
