
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


class Scenario_Analyse:
    """ Creates a object containing the base scenarios and some logic to compute a Cluster analysis to get a set of reduced sceanrios """

    def __init__(self, K:int = 9, epsilon:float = 0.0001, N:int = 10000) -> None:
        
        # Initialize with default parameters for scenario analysis
        ''' Target number Of Scenarios (K>1)'''
        self._K = K
        ''' epsilon ... minimum allowed expected frequency (integer value) '''
        self._epsilon = epsilon         

        self._N = N

        # Define scenarios and their probabilities
        self._demand_supply = np.array([
            [6400, 8000, 12000],
            [600, 1000, 1200],
            [2800, 4000, 8000],
            [300, 500, 600],
            [862.5, 1725, 3450]
        ])
        self._p = np.array([
            [0.4, 0.35, 0.25],
            [0.25, 0.35, 0.4],
            [0.4, 0.3, 0.3],
            [0.3, 0.4, 0.3],
            [0.5, 0.15, 0.35]
        ])

        #Create lists for scenarios and their probabilities 
        self.create_base_scenarios_and_p()

        #Create dataset W 
        self.create_vector_W()

        #Compute K-means Clustering and create the set of reduced scenarios
        self.apply_K_means_Clustering()

    def __str__(self):
        ''' Print the base scenarios, their probabilities and the reduced scenarios with their probabilities '''

        # maybe use pretty print library to print the output in a more readable way
        output = "Base Scenarios:\n"
        output += str(self._base_scenarios) + "\n"
        output += "Probabilities of Base Scenarios:\n"
        output += str(self._p_base_scenarios) + "\n"
        output += "Reduced Scenarios:\n"
        output += str(self._reduced_scenarios) + "\n"
        output += "Probabilities of Reduced Scenarios:\n"
        output += str(self._p_reduced_scenarios) + "\n"
        return output





    def create_base_scenarios_and_p(self) -> None: 
        ''' Create all possible scenarios dependent from the demand and supply and the probabilities '''

        #Create empty lists for scenarios and the belonging probability
        self._base_scenarios = []
        self._p_base_scenarios = []

        # Iterate through all combinations of demand and supply levels.
        for i in range(len(self._demand_supply[0])):
            for j in range(len(self._demand_supply[1])):
                for k in range(len(self._demand_supply[2])):
                    for l in range(len(self._demand_supply[3])):
                        for m in range(len(self._demand_supply[4])):
                            
                            #Creation of scenario as a list 
                            scenario = [self._demand_supply[0][i],self._demand_supply[1][j], self._demand_supply[2][k], self._demand_supply[3][l], self._demand_supply[4][m]]
                            self._base_scenarios.append(scenario)

                            #Calculate the probility of this scenario (round to 4 decimals to avoid floats when multiplying with 10000)
                            prob_scenario = round(self._p [0][i] * self._p [1][j] * self._p [2][k] * self._p [3][l] * self._p [4][m],4)
                            self._p_base_scenarios.append(prob_scenario)


    def create_vector_W(self) -> None:
        ''' Creates dataset W which is poulated by scenarios from original _base_scenarios vector, each sceanrio can be 
            present multiple timnes dependent on the probability!
        '''

        ''' W is a dataset with m fields, corresponding to the m number of components in a scenario vector. '''
        self.W = []  # Initialize the dataset W.
        
        # Loop through each scenario in the original _base_scenarios vector.
        for i in range(len(self._base_scenarios)): 
            
            # Calculate the frequency of the current scenario based on its probability.
            f_scenario = round(self._N * self._p_base_scenarios[i])

            #print(f'{i}, f_scenario: {self._N} * {self._p_base_scenarios[i]} = {f_scenario}')

             # Check if the frequency meets a certain threshold (epsilon).
            if(f_scenario >= self._epsilon): 

                '''With epsilon = 0.0001, epsilon has no influence on the overall process!!!
                # Add a comment regarding the impact of epsilon when it equals 0.0001. ''' 

                # Repeat the current scenario according to its frequency.
                for j in range(f_scenario):
                    
                    #Add scenario to dataset
                    self.W.append(self._base_scenarios[i])
        
        # Convert the dataset W to a NumPy array.
        self.W = np.array(self.W)

    def normalize_dataset(self, data:np.array) -> np.array:
        """
            Normalize the dataset and return it as a NumPy array.
        """

        # Normalize each feature across all vectors
        self.mean_data = np.mean(data, axis=0)
        self.std_data = np.std(data, axis=0)

        # Avoid division by zero
        self.std_data[self.std_data == 0] = 1

        # Applying the normalization
        normalized_data = (data - self.mean_data) / self.std_data

        return normalized_data
    

    def denormalize_dataset(self, data:np.array) -> np.array:
        """
        Denormalizes the data by applying the inverse of the earlier normalization process.
        
        Normalization typically transforms data to have a mean of zero and a standard deviation
        of one. This function reverses that process by using the stored mean and standard deviation
        values to transform the normalized data back to its original scale.

        Args:
        data (np.array): A numpy array containing normalized data.

        Returns:
        np.array: A numpy array containing denormalized data, which restores the original scale of values.
        """

        # Applying the denormalization formula: original_value = normalized_value * std + mean
        denormalized_data = data * self.std_data + self.mean_data

        return denormalized_data
    

    def apply_K_means_Clustering(self) -> None:
        """
        Applies K-means clustering to the scenario dataset to identify clusters that summarize the scenarios.

        This method performs the following steps:
        1. Normalize the dataset `W` containing all scenarios.
        2. Apply the K-means clustering algorithm to the normalized data, with the number of clusters (`K`) defined in the class.
        3. Use the resulting cluster centers to represent reduced scenarios, which are denormalized to reflect their actual scales.
        4. Calculate the sizes of each cluster, which represent how many scenarios fall into each cluster.
        5. Compute the probabilities for each reduced scenario based on the cluster sizes relative to the total number of scenarios.

        The clustering helps reduce the complexity of scenario analysis by representing multiple similar scenarios with a single 'average' scenario, thus simplifying further analysis or decision-making processes.

        """

        # Normalize the dataset W to prepare for clustering.
        data = self.normalize_dataset(self.W)

        # Create a K-means clustering model with specified number of clusters and a fixed random state for reproducibility.
        kmeans = KMeans(n_clusters=self._K, random_state=0, n_init='auto')
        
        # Fit the K-means model on the normalized data.
        kmeans.fit(data)

        # Round the denormalized cluster centers to form the reduced scenarios.
        self._reduced_scenarios = np.round(self.denormalize_dataset(np.array(kmeans.cluster_centers_)))

        # Calculate the size of each cluster to understand the distribution of scenarios across clusters.
        self._sizes_reduced_scenarios = np.bincount(kmeans.labels_)

        # Compute probabilities of each cluster by normalizing the cluster sizes.
        self._p_reduced_scenarios = [round(cluster_size / len(self.W), 4) for cluster_size in self._sizes_reduced_scenarios]

    # Getter methods for private variables
    def get_len_W(self) -> int: 
        return len(self.W)
    
    def get_len_base_scenarios(self) -> int: 
        return len(self._base_scenarios)
    
    def get_K(self) -> int:
        return self._K

    def get_epsilon(self) -> float:
        return self._epsilon

    def get_N(self):
        return self._N

    def get_demand_supply(self) -> list[list[int]]:
        return self._demand_supply

    def get_probabilities(self) -> list[list[float]]:
        return self._p

    def get_base_scenarios(self) -> list[list[int]]:
        return self._base_scenarios

    def get_base_scenario_probabilities(self) -> list[list[float]]:
        return self._p_base_scenarios

    def get_reduced_scenarios(self) -> list[list[int]]:
        return self._reduced_scenarios

    def get_sizes_reduced_scenarios(self) -> list[int]:
        return self._sizes_reduced_scenarios

    def get_reduced_scenarios_probabilities(self) -> list[float]:
        return self._p_reduced_scenarios
    

#### TEST ####
#S = Scenario_Analyse()

#print(S.get_reduced_scenarios())
#print(S.get_reduced_scenarios_probabilities())
