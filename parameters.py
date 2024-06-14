# We will create a class that will generate the parameters for the model
from scenario_reduction import *
import json

### Script for generating data fpr our model
class Parameters:
    ''' Class to generate the parameters for the model'''

    def __init__(self, json_file_path: str):
        ''' Constructor for this class.
        :param file_path: path to the file with the datafile (txt file)
        '''

        self.json_file_path = json_file_path
        self.__loadData()
        self.__createSets()
        self.__createScenarioReduction()
        self._mappingFtoM = self.__create_mappingFtoM()


    def __loadData(self) -> None:
        ''' Load the data from the json file and assign the values to the class variables
        '''

        with open(self.json_file_path, 'r') as json_file:
            data = json.load(json_file)
            
            # Zuweisen der Werte zu Klassenvariablen
            self._T_No = data['T_No']
            self._F_No = data['F_No']
            self._P_No = data['F_No']
            self._FT_No = data['FT_No']
            self._MP_No = data['MP_No']
            self._CT_No = data['CT_No']
            self._L_No = data['L_No']
            self._hl = data['T_No'] - 1
            self._fty = data['fty']
            self._cty = data['cty']
            self._fpr = data['fpr']
            self._fy = data['fy']
            self._rsc = data['rsc']
            self._roc = data['roc']
            self._el = data['el']
            self._tau = data['tau']
            self._i_0 = data['i_0']
            self._i_0_f = data['i_0_f']
            self._tl_min = data['tl_min']
            self._tl_max = data['tl_max']
            self._r0 = data['r0']
            self._r_max = data['r_max']
            self._dmax = data['dmax']
            self._cmin = data['cmin']
            self._cmax = data['cmax']
            self._alpha = data['alpha']
            self._ost = data['ost']
            self._wp = data['wp']
            self._el_min = data['el_min']
            self._el_max = data['el_max']
            self._is_ = data['is']
            self._omega_fw = data['omega_fw']
            self._omega_dc = data['omega_dc']
            self._rr = data['rr']
            self._r = data['r']
            self._re = data['re']
            self._imax = data['imax']
            self._zmax = data['zmax']
            self._sc = data['sc']
            self._beta = data['beta']
            self._sigma = data['sigma']
            self._iwip0 = data['iwip0']
            self._tc = data['tc']
            self._sco = data['sco']
            self._K = data['K']
            self._epsilon = data['epsilon']
            self._N = data['N']
            self._demand_supply = data['demand_supply']
            self._probabilies = data['probabilies']

    def __createSets(self) -> None:
        ''' 
        Create the sets for the model to run the necessary loops
        '''
        self._T = range(self._T_No)
        self._F = range(self._F_No)
        self._FT = range(self._FT_No)
        self._MP = range(self._MP_No)
        self._CT = range(self._CT_No)
        self._L = range(self._L_No)
        self._S = range(self._K)
        self._P = range(self._P_No)


    def __create_dp(self) -> list[list[list[list[int]]]]:
        ''' Creation of demand in each scenario for each time point for each family type to each location
        '''

        # Create a list for the demand of each family
        demand = []

        for s in self._S:
            scenario_demand = []
            for f in self._F:
                family_demand = []
                overall_demand = self._SRA.reduced_scenarios[s][f]
                share = (overall_demand // len(self._L))
                last_share = (share + overall_demand % len(self._L))
                #share = round((overall_demand // len(self._L)) / self._T_No)
                #last_share = round((share + overall_demand % len(self._L))/ self._T_No)
                for l in self._L:
                    location_demand = []
                    for t in self._T:

                        if(l == self._L[-1]):
                            location_demand.append(share)
                        else: 
                            location_demand.append(last_share)

                    family_demand .append(location_demand)
                scenario_demand .append(family_demand )
            demand.append(scenario_demand)

        return demand
    
    def __create_dri(self) -> list[list[int]]:
        ''' Raw milk daily input on day t under scenario s
        '''

        milk_input = []

        for s in self._S:
            scenario_milk_input = []
            milk = self._SRA.reduced_scenarios[s][-1]
            #milk_share = round(milk / self._T_No)
            for t in self._T:
                scenario_milk_input.append(milk)

            milk_input.append(scenario_milk_input) 
        
        return milk_input

    def __createScenarioReduction(self) -> None:
        ''' Create the scenario reduction object '''

        self._SRA = Scenario_Analyse(self._demand_supply, self._probabilies, self._K, self._epsilon, self._N)
        
        self._dp = self.__create_dp()
        self._rho =  self._SRA.reduced_scenarios_probabilities
        self._dri = self.__create_dri()

    def __create_mappingFtoM(self) -> list[int]: 
        ''' Mapping of family f to plant m
        '''

        # plant 0 -> family 0 (Powdered Milk)
        # plant 1 -> family 1 (UHT Milk)
        # plant 2 -> family 2 (Yogurt)
        # plant 3 -> family 3 (Cheese)

        return [m for m in self._MP]
        
    
    ###### MANY PROPERTIES TO NOT CHANGE THE VALUES OF THE VARIABLES ######
    @property
    def hl(self):
        ''' Time span of optimization horizon '''
        return self._hl

    @property
    def fty(self):
        ''' The type (Fresh or Dry) of family f 
        dry (not refrigerated) for products of the UHT and Powdered Milk families; and fresh (refrigerated), for
        products of the Yogurt and Cheese families

        Dry = 0
        Fresh = 1
        '''

        return self._fty

    @property
    def cty(self):
        ''' Campaign type for production plant m -> Which work model is used in manufacturing plant m 
        
            0 = Lengthbased
            1 = Shiftbased
        '''

        return self._cty

    @property
    def fpr(self):
        ''' The family produced by manufacturing plant m 
            UHT and Powdered Milk, Yogurt, Cheese
            Differnece between production plants of Powedered Milk and Rest !!!
        '''
        
        return self._fpr

    @property
    def fy(self):
        ''' Family f production yield for  a unit of processed raw milk 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._fy

    @property
    def rsc(self):
        ''' Raw milk third supplier cost '''

        return self._rsc

    @property
    def roc(self):
        ''' Raw milk over stock cost per volume unit 
            NOTHING MENTIONED - ASSUMPTION, THAT IT IS THREE TIMES THE NORMAL PRICE!
        '''

        return self._roc

    @property
    def el(self):
        ''' Export lot size in metric tons of family f 
            Lot size is 25 metric ton
        '''

        return self._el

    @property
    def tau(self):
        ''' Transportation time from factory to distribution center in days
        '''

        return self._tau

    @property
    def i_0(self):
        ''' Family f Initial inventory at location l.e
        '''

        return self._i_0

    @property
    def i_0_f(self):
        ''' Family f Initial inventory at FW
        '''

        return self._i_0_f

    @property
    def tl_min(self):
        ''' Minimum  truckload capacity, respectively.
        '''

        return self._tl_min

    @property
    def tl_max(self):
        '''  Maximum truckload capacity, respectively.
        '''

        return self._tl_max

    @property
    def r0(self):
        ''' Raw milk initial inventory.
        '''

        return self._r0

    @property
    def r_max(self):
        ''' Maximum raw milk inventory.
        '''

        return self._r_max

    @property
    def dmax(self):
        ''' Maximum campaign length (in days) for plant m. 

        Only one value given for Length-Based Campaign --> Assumnption that shift based campaign are unlimited!
        '''

        return self._dmax

    @property
    def cmin(self):
        ''' Minimum daily production capacity at manufacturing plant m 
            Assumption about minimum that it is 0!
            # assumption update: it cannot be 0, because cmin is a divisor in a constraint, so that would lead to division by zero
        '''

        return self._cmin

    @property
    def cmax(self):
        ''' Maximum daily production capacity at manufacturing plant m 
            Assumption about maximum, but already given! 
            # assumption update: 3 times maximimum number of shifts
        '''

        return self._cmax

    @property
    def alpha(self):
        ''' Setup time in periods for production plant m 
            Assunmption, that setup is only needed for Powdered Milk!
        '''

        return self._alpha

    @property
    def ost(self):
        ''' Remaining days to finish an ongoing setup task at manufacturing plant m 
            Assumption no ongoing setup tasks at manufacturing plant m
        '''

        return self._ost

    @property
    def wp(self):
        ''' m: manufacturing plant, 
            t: time (days), 
            sigma: process time for family produced in manufacturing plant m
            Assumption no ongoing setup tasks at manufacturing plant m
        '''

        return self._wp

    @property
    def el_min(self):
        ''' F: lots of family f to be exported; here: Minimum number
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._el_min

    @property
    def el_max(self):
        ''' F: lots of family f to be exported; here: Maximum number
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._el_max

    @property
    def is_(self):
        ''' M: maximum portion of total capacity that can be left
            idle during a production campaign  at manufacturing plant m with [0,1) value#
        '''

        return self._is_

    @property
    def omega_fw(self):
        ''' factory warehouse shelf-life of products of family f
            UHT and Powdered Milk, Yogurt, Cheese
            100 as a high number for long time span
        '''

        return self._omega_fw

    @property
    def omega_dc(self):
        ''' distribution center shelf-life of products of family f
            UHT and Powdered Milk, Yogurt, Cheese
            100 as a high number for long time span
        '''

        return self._omega_dc

    @property
    def rr(self):
        ''' revenue from reduced price selling of products of family f over stock (distressed sales) 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._rr

    @property
    def r(self):
        ''' revenue from selling one ton of family f in any distribution center of the Supply Chain 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._r

    @property
    def re(self):
        ''' revenue from exporting a batch of family f 
            UHT and Powdered Milk, Yogurt, Cheese
            only for powdered milk! 
        '''

        return self._re

    @property
    def imax(self):
        ''' Maximum storage capacities at location l for fresh and dry product families i 
        '''

        return self._imax

    @property
    def zmax(self):
        ''' For shift-based production, maximum shifts, otherwise 1
            Retrieved from paper
        '''

        return self._zmax

    @property
    def sc(self):
        ''' Production capacity of the manufacturing plant m per work shift in metric tons
            Retrieved from paper
            0 for lenghtbased production plants
        '''

        return self._sc

    @property
    def beta(self):
        ''' Deterioration coefficient for products manufactured at factory m 
        '''

        return self._beta

    @property
    def sigma(self):
        ''' Process time in periods for the family produced at manufacturing plant m

            List for availability of product lines 
            Powdered Milk: Need to be quality tested -> 1 day 
            UHT Milk: Nothing mentioned -> 0 day
            Yogurt: Nothing mentioned -> 0 day
            Cheese: Ripening phase -> 4 days
        '''

        return self._sigma

    @property
    def iwip0(self):
        ''' Inventory of work-in-progress from previous planning horizon at manufacturing plant m
        '''

        return self._iwip0

    @property
    def tc(self):
        ''' Transportation costs from the production complex to the distribution center l 
        
            Names Of Distribution Centers:
            ["DC-SAL", "DC-CBA", "DC-CTE","DC-POS","DC-RAF","DC-MZA", "DC-ROS", "DC_NQN", "DC-BUE"]
        '''

        return self._tc

    @property
    def sco(self):
        ''' Setup costs in Monetary Units
        '''

        return self._sco

    
    @property
    def SRA(self):
        ''' Scenario Reduction Analysis Instance with all data and results
        '''

        return self._SRA

    @property
    def dp(self):
        ''' Family demand for distribution center l on day t under scenario s.
        '''

        return self._dp

    @property
    def rho(self):
        ''' The probability of scenario s.
        '''

        return self._rho

    @property
    def dri(self):
        ''' Raw milk daily input on day t under scenario s
        '''

        return self._dri

    @property
    def T(self):
        ''' Range for time span of optimization horizon
        '''

        return self._T

    @property
    def F(self):
        ''' Range for product family types 
        '''
        
        return self._F

    @property
    def FT(self):
        ''' Range for family types, fresh or dry 
        '''

        return self._FT

    @property
    def MP(self):
        ''' Range for manufacturing plants
        '''

        return self._MP

    @property
    def CT(self):
        ''' Range for production camp. types. length or shift based
        '''

        return self._CT

    @property
    def L(self):
        ''' Range for distribution centers
        '''

        return self._L

    @property
    def S(self):
        ''' Range for reduced scenarios
        '''

        return self._S
    
    
    @property
    def mappingFtoM(self):
        ''' Mapping of family to manufacturing plant
        '''

        return self._mappingFtoM
    
    ###### TRICKS FOR RETURNING PRODUCT DATA INSTEAD OF FAMILY TYPES ###### 

    @property
    def P(self):
        ''' Range for products
        '''

        return self._F

    @property
    def ls(self):
        ''' Product p export lot size, expressed in metric tons.
        '''
        return self._el

    @property
    def id0(self):
        ''' Product p initial inventory at any location l ∈ L∪ < {FW}.
        '''
        return self._i_0

    @property
    def dpd (self):
        ''' Product p demand for distribution center l on day t under scenario s.
        '''
        return self._dp
    
