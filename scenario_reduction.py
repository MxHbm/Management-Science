
#### TEST AREA ####

#Product families and Supply scenarios.
#UHT PM Yogurt Cheese Raw Milk

# Structure: [Product family][Supply Scenario i] 
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Product families and Supply scenarios
demand_supply = np.array([
    [6400, 8000, 12000],
    [600, 1000, 1200],
    [2800, 4000, 8000],
    [300, 500, 600],
    [862.5, 1725, 3450]
])

probs = np.array([
    [0.4, 0.35, 0.25],
    [0.25, 0.35, 0.4],
    [0.4, 0.3, 0.3],
    [0.3, 0.4, 0.3],
    [0.5, 0.15, 0.35]
])



scenarios = []
probs_scenarios = []

for i in range(len(demand_supply[0])):
    for j in range(len(demand_supply[1])):
        for k in range(len(demand_supply[2])):
            for l in range(len(demand_supply[3])):
                for m in range(len(demand_supply[4])):

                    scenario = [demand_supply[0][i],demand_supply[1][j], demand_supply[2][k], demand_supply[3][l], demand_supply[4][m]]
                    scenarios.append(scenario)

                    prob_scenario = round(probs[0][i] * probs[1][j] * probs[2][k] * probs[3][l] * probs[4][m],4) # rounded to three decimals to genrate integers when multiypling with N

                    probs_scenarios.append(prob_scenario)

                    #print(scenario)

# print(len(scenarios)) -> 243 CHECK!!! 

K = 9
epsilon = 0.0001
N = 10000
W = []

for i in range(len(scenarios)): 

    f_scenario = round(N * probs_scenarios[i])

    if(f_scenario >= epsilon): 

        ''' #MIt epsilon = 0.0001 hat epsilon überhaupt keinen Einfluss auf das Ganze !!! 
'''

        for j in range(f_scenario):

            W.append(np.array(scenarios[i]))

data = np.array(W)
print("Lenght of W: %d" %len(W))


# Convert list of vectors into a 2D array
data = np.array(W)

# Normalize each feature across all vectors
mean_data = np.mean(data, axis=0)
std_data = np.std(data, axis=0)

# Avoid division by zero
std_data[std_data == 0] = 1

# Applying the normalization
normalized_data = (data - mean_data) / std_data

# Display the normalized data
print("Normalized Data:")
print(normalized_data)

#### K-MEANS CLustering #####

# Creating the KMeans object
kmeans = KMeans(n_clusters=K, random_state=0)

# Fit data to kmeans
kmeans.fit(normalized_data)

#### ANALYZE EVERYTHING ####

# Coordinates of cluster centers
normalized_centroids = np.array(kmeans.cluster_centers_)
centroids = normalized_centroids * std_data + mean_data

# Get the cluster labels
labels = kmeans.labels_

# Count the number of data points in each cluster
cluster_sizes = np.bincount(labels)

#### PRINT STUFF #####

print("Centroids of clusters:")
print(centroids)

# Count the number of data points in each cluster
cluster_sizes = np.bincount(labels)

print("Cluster sizes:")
for i in range(K):
    print(f"Cluster {i}: {cluster_sizes[i]}")

print("Probabilities")
prob_cluster = []
num = 0
for cluster_size in cluster_sizes:

    prob = round(cluster_size/len(data),4)
    prob_cluster.append(prob)
    print(f"Cluster with Probability: {prob}")
    num += prob

print(num)
