
from pprint import pprint
import random

### RANODM NUMBER GENERATOR 

# Create an instance of the Random class
rng = random.Random()

# Seed the random number generator for reproducibility
rng.seed(42)

from gurobipy import *
from gurobipy import GRB
import csv
import csv
import pandas as pd



### Script for generating data fpr our model
class Parameters_FirstStage:

    def __init__(self, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        ''' Constructor for this class.
        :param T: list of time periods
        :param F: list of families
        :param S: list of scenarios
        :param FT: list of family types
        :param MP: list of manufacturing plants
        :param CT: list of production campaign types
        :param L: list of locations (Distribution Centers)
        '''

        #First definition of parameters and call for implementing them
        self.hl = self.create_hl(T)
        self.fty = self.create_fty()
        self.cty = self.create_cty()
        self.fpr = self.create_fpr()
        self.fy = self.create_fy()
        self.rsc = self.create_rsc()
        self.roc = self.create_roc()
        self.el = self.create_el()
        self.tau = self.create_tau()
        self.i0 = self.create_i_0(F, L) 
        self.i0_2 = self.create_i0_ft(F, T)        # not in the paper
        self.tl_min = self.create_tl_min()
        self.tl_max = self.create_tl_max()
        self.r0 = self.create_r0()
        self.r_max = self.create_r_max()
        self.dmax = self.create_dmax()
        self.cmin = self.create_cmin()
        self.cmax = self.create_cmax()
        self.alpha = self.create_alpha()
        self.ost = self.create_ost(MP)
        self.wp = self.create_wp(MP, T)
        self.el_min = self.create_el_min()
        self.el_max = self.create_el_max()
        self.is_ = self.create_is(MP)
        self.omega_fw = self.create_omega_fw()
        self.omega_dc = self.create_omega_dc()
        self.rr = self.create_rr()
        self.r = self.create_r()
        self.re = self.create_re()
        self.imax = self.create_imax()
        self.zmax = self.create_zmax()
        self.sc = self.create_sc()
        self.beta = self.create_beta()
        self.sigma = self.create_sigma()
        self.iwip0 = self.create_iwip0(MP)
        self.tc = self.create_tc()
        self.sco = self.create_sco()
        # additional parameters
        self.names_DC = self.create_names_DC()
        self.ls = self.create_ls_f(F)
        self.ls = self.create_ls_p(MP)
        self.mappingFtoM = self.create_mappingfm()

    def create_hl(self, T) -> int:
        ''' Add description of the function here '''
        hl = T[-1]        # 30 days in the paper 

        return hl

    def create_fty(self) -> list[int]:
        ''' The type (Fresh or Dry) of family f 
        dry (not refrigerated) for products of the UHT and Powdered Milk families; and fresh (refrigerated), for
        products of the Yogurt and Cheese families

        Dry = 0
        Fresh = 1
        '''

        return [0,0,1,1]
        

    def create_cty(self) -> list[int]:
        ''' Campaign type for production plant m -> Which work model is used in manufacturing plant m 
        
            0 = Lengthbased
            1 = Shiftbased
        '''
        
        cty = [0,1,1,1]
        
        return cty

    def create_fpr(self) -> list[float]:
        ''' The family produced by manufacturing plant m 
            UHT and Powdered Milk, Yogurt, Cheese
            Differnece between production plants of Powedered Milk and Rest !!! '''
        
        return [110, 120, 150, 16.66]

    def create_fy(self) -> list[float]:
        ''' Family f production yield for  a unit of processed raw milk 
            UHT and Powdered Milk, Yogurt, Cheese'''
        
        return [0.975, 0.12, 0.9, 0.11]

    def create_rsc(self) -> int:
        ''' Raw milk third supplier cost '''
        # DEBUG INFO: if lower than 4, the model does not work
        
        #return 2            # in the paper 2 MU 
        return 6

    def create_roc(self) -> int:
        ''' Raw milk over stock cost per volume unit 
            NOTHING MENTIONED - ASSUMPTION, THAT IT IS THREE TIMES THE NORMAL PRICE!
        '''

        return self.rsc * rng.randint(3,3) 

    def create_el(self) -> list[int]:
        ''' Export lot size in metric tons of family f 
            Lot size is 25 metric ton
        '''
        return [25,25,25,25]
        
    def create_tau(self) -> list[int]:
        ''' Transportation time from factory to distribution center in days'''

        transport_time_factory_dc = [2,1,1,2,0,1,0,2,1]
        
        return transport_time_factory_dc

    def create_i_0(self, F, L) -> list[list[int]]:
        ''' Family f Initial inventory at location l.e '''

        intitial_inventory = []
        for f in F:
            family_inventory = []
            for l in L:
                family_inventory.append(rng.randint(0,10))

            intitial_inventory.append(family_inventory)

        return intitial_inventory
    
    def create_i0_ft(self, F, T) -> list[list[int]]:
        # notin the paper, but needed for the model
        ''' Family f Initial inventory at time t.e '''
        
        intitial_inventory = []
        for f in F:
            family_inventory = []
            for t in T:
                family_inventory.append(rng.randint(0,100))

            intitial_inventory.append(family_inventory)

        return intitial_inventory

    def create_tl_min(self) -> int:
        ''' Minimum  truckload capacity, respectively. '''

        tl_min = 4    
        return tl_min
    
    def create_tl_max(self) -> int:
        '''  Maximum truckload capacity, respectively. '''

        tl_max = 8    
        return tl_max

    def create_r0(self) -> int:
        ''' Raw milk initial inventory. '''

        initial_inventory = rng.randint(50,200)
        #initial_inventory = 200       # for debugging

        return initial_inventory

    def create_r_max(self) -> int:
        ''' Maximum raw milk inventory. '''

        maximum_inventory = rng.randint(1000,2000)
        #maximum_inventory = 20000000        # for debugging

        return maximum_inventory
        

    def create_dmax(self) -> list[int]:
        ''' Maximum campaign length (in days) for plant m. 

        Only one value given for Length-Based Campaign --> Assumnption that shift based campaign are unlimited!
        '''
        
        #return [30,15,30,30]
        return [40,15,40,40]

    def create_cmin(self) -> list[int]:
        ''' Minimum daily production capacity at manufacturing plant m 
            Assumption about minimum that it is 0!
            # assumption update: it cannot be 0, because cmin is a divisor in a constraint, so that would lead to division by zero
        '''
        
        return [1, 1, 1, 1]

    def create_cmax(self) -> list[float]:
        ''' Maximum daily production capacity at manufacturing plant m 
            Assumption about maximum, but already given! 
        '''
        #rng.randint()
        #return [110,120,150,16.66]
        return [110,120,150,16.66]#*500

    def create_alpha(self) -> list[int]:
        ''' Setup time in periods for production plant m 
            Assunmption, that setup is only needed for Powdered Milk!
        '''

        setup_time_days = rng.randint(0,3)

        return [0,setup_time_days,0,0]

    def create_ost(self, MP) -> list[int]:
        ''' Remaining days to finish an ongoing setup task at manufacturing plant m 
            Assumption no ongoing setup tasks at manufacturing plant m
            '''
        return [rng.randint(0,0) for m in MP]

    def create_wp(self, MP, T) -> list[list[int]]:
        ''' m: manufacturing plant, 
            t: time (days), 
            sigma: process time for family produced in manufacturing plant m
            Assumption no ongoing setup tasks at manufacturing plant m
        '''

        return [[rng.randint(0,0) for t in T ] for m in MP]

    def create_el_min(self) -> list[int]:
        ''' F: lots of family f to be exported; here: Minimum number
            UHT and Powdered Milk, Yogurt, Cheese
        '''
        return [0,25,0,0]


    def create_el_max(self) -> list[int]:
        ''' F: lots of family f to be exported; here: Maximum number
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return [0,120,0,0]


    def create_is(self, MP) -> list[float]:
        ''' M: maximum portion of total capacity that can be left idle during a production campaign  at manufacturing plant m with [0,1) value'''
        
        #return [rng.uniform(0,0.2) for m in MP]
        return [1 for m in MP]

    def create_omega_fw(self) -> list[int]:
        ''' factory warehouse shelf-life of products of family f
            UHT and Powdered Milk, Yogurt, Cheese
            100 as a high number for long time span
        '''

        #return [self.hl,self.hl,5,10]
        return [40, 40 ,5,10]


    def create_omega_dc(self) -> list[int]:
        ''' distribution center shelf-life of products of family f
            UHT and Powdered Milk, Yogurt, Cheese
            100 as a high number for long time span
        '''

        return [100,100,7,14]


    def create_rr(self) -> list[float]:
        ''' revenue from reduced price selling of products of family f over stock (distressed sales) 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return [1,  3.75, 0, 0]

    def create_r(self) -> list[float]:
        ''' revenue from selling one ton of family f in any distribution center of the Supply Chain 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return [3.425,  12.5, 5, 12]


    def create_re(self) -> list[int]:
        ''' revenue from exporting a batch of family f 
            UHT and Powdered Milk, Yogurt, Cheese
            only for powdered milk! 
        '''

        return [0,5,0,0]


    def create_imax(self) -> list[list[int]]:
        ''' Maximum storage capacities at location l for fresh and dry product families i '''

        # Fresh and Dry                  i
        max_storage_product_groups = [[12,10],      # l_1
                                      [68, 114],    
                                      [16, 35],
                                      [16,40],
                                      [9, 27],
                                      [31,54],
                                      [20, 81],
                                      [20,58],
                                      [58,195]]
        
        return list(map(list, zip(*max_storage_product_groups)))        # transpose the matrix [l,i] because we want to have [i, l]

    def create_zmax(self) -> list[int]:
        ''' For shift-based production, maximum shifts, otherwise 1
            Retrieved from paper
        '''

        zmax = [1,3,3,3]

        return zmax

    def create_sc(self) -> list[float]:
        ''' Production capacity of the manufacturing plant m per work shift in metric tons
            Retrieved from paper
            0 for lenghtbased production plants
        '''

        sc = [0,110,150,16.66]

        return sc

    def create_beta(self) -> list[float]:
        ''' Deterioration coefficient for products manufactured at factory m 
            Coeffeicient ranodmly selected from [0, 0.05]
        '''

        #List for deterioration coefficients
        # Powdered Milk, UHT Milk, Yogurt, Cheese
        beta = [0.1,0,0,0]

        return beta

    def create_sigma(self) -> list[int]:
        ''' Process time in periods for the family produced at manufacturing plant m

        List for availability of product lines 
        Powdered Milk: Need to be quality tested -> 1 day 
        UHT Milk: Nothing mentioned -> 0 day
        Yogurt: Nothing mentioned -> 0 day
        Cheese: Ripening phase -> 4 days'''

        # Powdered Milk, UHT Milk, Yogurt, Cheese

        sigma = [1,0,0,4]

        return sigma 

    def create_iwip0(self, MP) -> list[int]:
        ''' Inventory of work-in-progress from previous planning horizon at manufacturing plant m '''
        
        # No data given -> Assume there is nothing given

        iwip = [rng.randint(0,0) for m in MP]

        return iwip

    def create_tc(self) -> list[list[int]]:
        ''' Transportation costs from the production complex to the distribution center l 
        
        Names Of Distribution Centers:
        ["DC-SAL", "DC-CBA", "DC-CTE","DC-POS","DC-RAF","DC-MZA", "DC-ROS", "DC_NQN", "DC-BUE"]

        '''
                                                #   0   , 1         // Fresh and Dry
        transport_costs_product_group_matrix = [[15.641,13.034],
                                                [4.956, 4.13],
                                                [10.332,8.61],
                                                [14.818, 12.348],
                                                [0.067, 0.056],
                                                [14.364, 11.97],
                                                [4.032, 3.36],
                                                [21.638,18.032],
                                                [9.021,7.518]]
        
        # transport_costs_product_group_matrix = [[1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1],
        #                                         [1, 1]]
        
        return transport_costs_product_group_matrix

    def create_sco(self) -> int:
        ''' Setup costs in Monetary Units'''
        
        setup = 20 # unit is MU

        return setup
    
    # additional parameters

    def create_names_DC(self) -> list[str]: 
        """ Names of the distribution centers """

        return ["DC-SAL", "DC-CBA", "DC-CTE","DC-POS","DC-RAF","DC-MZA", "DC-ROS", "DC_NQN", "DC-BUE"]
    
    def create_ls_f(self, F) -> list:
        ''' Lot size for family f '''

        lot_size = [1 for f in range(len(F))]         # dummy values

        return lot_size
    
    def create_ls_p(self, MP) -> list:
        ''' Lot size for plant m '''


        lot_size = [1 for m in range(len(MP))]         # dummy values

        return lot_size
    
    
    def create_mappingfm(self) -> list:
        ''' Mapping of family f to plant m '''

        # plant 0 -> family 0 (Powdered Milk)
        # plant 1 -> family 1 (UHT Milk)
        # plant 2 -> family 2 (Yogurt)
        # plant 3 -> family 3 (Cheese)

        mapping = [0, 1, 2, 3]

        return mapping
    
### Script for generating data fpr our model
class Parameters_SecondStage:

    def __init__(self, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list, scenarios):
        ''' Constructor for this class.
        :param T: list of time periods
        :param F: list of families
        :param S: list of sites
        :param FT: list of family types
        :param MP: list of manufacturing plants
        :param CT: list of customer types
        :param L: list of locations (Distribution Centers)
        '''

        #First definition of parameters and call for implementing them
        self.dp = self.create_dp(S, F, L, T, scenarios)
        self.rho = self.create_rho(scenarios)
        self.dri = self.create_dri(S, T, scenarios)

    def create_dp(self, S, F, L, T, scenarios) -> list[list[list[list[int]]]]:
        ''' Family demand for distribution center l on day t under scenario s. '''

        # Create a list for the demand of each family
        overall_demand_old = 0
        share_old = 0
        last_share_old = 0

        demand = []
        for s in S:
            scenario_demand = []
            for f in F:
                family_demand = []
                overall_demand = scenarios.get_reduced_scenarios()[s][f]
                share = overall_demand // len(L)
                last_share = share + overall_demand % len(L)
                for l in L:
                    location_demand = []
                    for t in T:
                        #if(l == len(L)-1):
                        if(l == L[-1]):
                            location_demand.append(share)
                        else: 
                            location_demand.append(last_share)

                    family_demand .append(location_demand)
                scenario_demand .append(family_demand )
            demand.append(scenario_demand )
        
        # Save demand as CSV file
        with open('demand.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for s in range(len(S)):
                for f in range(len(F)):
                    for l in range(len(L)):
                        for t in range(len(T)):
                            writer.writerow([s, f, l, t, demand[s][f][l][t]])

        #print(f"Demand (S={len(S)}, F={len(F)}, L={len(L)}, T={len(T)} ): ")
        #pprint(demand, compact=True, width=200)
        return demand

    def create_rho(self, scenarios) -> list[float]:
        ''' The probability of scenario s.
        '''

        rho = []

        for prob in scenarios.get_reduced_scenarios_probabilities():
            rho.append(prob)

        return rho
        

    def create_dri(self, S, T, scenarios) -> list[list[int]]:
        ''' Raw milk daily input on day t under scenario s
        '''

        milk_input = []
        for s in S:
            scenario_milk_input = []
            for t in T:
                scenario_milk_input.append(scenarios.get_reduced_scenarios()[s][-1])

            milk_input.append(scenario_milk_input) 
        
        return milk_input

    def create_fpr(self) -> list[float]:
        ''' The family produced by manufacturing plant m 
            UHT and Powdered Milk, Yogurt, Cheese
            Differnece between production plants of Powedered Milk and Rest !!! '''
        
        return [110, 120, 150, 16.66]

 
        ''' Family f Initial inventory at location l.e '''
  

class DecisionVariables_FirstStage:

    def __init__(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        """    self.CreateDecisionVariables(model, T, F, S, FT, MP, CT, L)

    def CreateDecisionVariables(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        ''' Add description of the function here '''
    """
        self.EXI = model.addVar(vtype=GRB.CONTINUOUS, name="EXI")
        #self.ENB = model.addVar(lb=0, name="ENB")
        self.ENB = model.addVar( name="ENB")        # for debugging
        #self.TCOST = model.addVar(lb=0, name="TCOST")
        self.TCOST = model.addVar(name="TCOST")     # for debugging
        self.SN = model.addVar(lb=0, name="SN")
        self.RM = model.addVars(T, lb=0, name="RMt")
        self.IF = model.addVars(F, T, lb=0, name="IFf_t")
        self.FP = model.addVars(F, T, lb=0, name="FPf_t")
        self.V = model.addVars(F, L, T, lb=0, name="Vi_l_t")
        self.DV = model.addVars(F, L, T, lb=0, name="DVf_l_t")
        self.A = model.addVars(MP, T, lb=0, name="Am_t")
        self.MO = model.addVars(MP, T, lb=0, name="MOm_t")
        self.IWIP = model.addVars(MP, T, lb=0, name="IWIPm_t")
        self.Q = model.addVars(MP, T, lb=0, name="Qm_t")
        self.Z1 = model.addVars(MP, T, name="Z1m_t")
        self.Z2 = model.addVars(MP, T, name="Z2m_t")
        self.Aux = model.addVars(MP, T, lb=0, name="Auxm_t")

        #return model

class DecisionVariables_SecondStage:

    def __init__(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        self.SA = model.addVars(S, F, L, T, lb=0, name="SAs_f_l_t")
        self.SO = model.addVars(S, F, L, T, lb=0, name="SOs_f_l_t")
        self.OS = model.addVars(S, F, L, T, lb=0, name="OSs_f_l_t")
        self.RC = model.addVars(S, lb=0, name="RCs_s")
        self.RS = model.addVars(S, T, lb=0, name="RSs_t")
        self.RO = model.addVars(S, T, lb=0, name="ROs_t")
        self.RI = model.addVars(S, T, lb=0, name="RIs_t")
        self.ID = model.addVars(S, F, L, T, lb=0, name="IDs_f_l_t")

class BinaryVariables:

    def __init__(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        self.R1 = model.addVars(MP, T, vtype=GRB.BINARY, name="R1m_t")
        self.R2 = model.addVars(MP, T, vtype=GRB.BINARY, name="R2m_t")
        self.Y = model.addVars(MP, T, vtype=GRB.BINARY, name="Ym_t")



class IntegerVariables:

    def __init__(self, model, parameters_FirstStage, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):

        self.TR = model.addVars(FT, L, T, vtype=GRB.INTEGER, lb=0, name="TRi_l_t")
        self.E = model.addVars(F, T, vtype=GRB.INTEGER, lb=0, name="Ef_t")
        self.Z = model.addVars(MP, T, vtype=GRB.INTEGER, lb=0, name="Zm_t")

        for m in MP:
            for t in T:
                self.Z[(m, t)].ub = parameters_FirstStage.zmax[m]
        

