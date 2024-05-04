
#### TEST AREA ####

#Product families and Supply scenarios.
#UHT PM Yogurt Cheese Raw Milk

# Structure: [Product family][Supply Scenario i] 

demand_supply = [[6400, 8000, 12000],
                 [600, 1000, 1200],
                 [2800, 4000, 8000],
                 [300, 500, 600],
                 [862.5, 1725,3450]]

probs = [[0,4, 0.35, 0.25],
         [0.25, 0.35, 0.4],
         [0.4, 0.3, 0.3],
         [0.3,  0.4, 0.3],
         [0.5, 0.15, 0.35]]

scenarios = []
probs_sceanrios = []

for i in range(len(demand_supply[0])):
    for j in range(len(demand_supply[1])):
        for k in range(len(demand_supply[2])):
            for l in range(len(demand_supply[3])):
                for m in range(len(demand_supply[4])):

                    scenario = [demand_supply[0][i],demand_supply[1][j], demand_supply[2][k], demand_supply[3][l], demand_supply[4][m]]
                    scenarios.append(scenario)

                    prob_scenario = probs[0][i] * probs[1][j] * probs[2][k] * probs[3][l] * probs[4][m]

                    probs_sceanrios.append(prob_scenario)
