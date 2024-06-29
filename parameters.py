# We will create a class that will generate the parameters for the model
from scenario_reduction import *
from typing import Any, List, Tuple, Set
import json

### Script for generating data fpr our model
class Parameters:
    ''' Class to generate the parameters for the model'''

    def __init__(self, json_file_path: str) -> None:
        ''' Constructor for this class.
        :param file_path: path to the file with the datafile (txt file)
        '''

        self.json_file_path = json_file_path

        if not hasattr(self, '_use_SRA'):
            self._use_SRA = None

        self.__loadData()
        self.__createSets()

        #CHeck if parameter decision was to use Scenario Reduction or to calculate the mean expected benefit
        if self._use_SRA:
            self.__createScenarioReduction()
            self._rho =  self._SRA.reduced_scenarios_probabilities
        else: 
            self._S = range(0, 1)
            self._rho = [1]

        # Create the demand for each family type or procduct based on the SRA  
        self._dp = self.__create_dp()
        self._dri = self.__create_dri()
        self._dpd = self.__create_dpd()

        # Create the sets of tupel combinations for controlling length based campaigns and setup times
        self.__create_big_phi()
        self.__create_big_theta()
        self.__create_big_omega()


    def __loadData(self) -> None:
        ''' Load the data from the json file and assign the values to the class variables
        '''

        with open(self.json_file_path, 'r') as json_file:
            data = json.load(json_file)
            
            # Zuweisen der Werte zu Klassenvariablen
            self._T_No = data['T_No']
            self._F_No = data['F_No']
            self._P_No = data['P_No']
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
            self._tc = data['tc']
            self._imax = data['imax']
            self._zmax = data['zmax']
            self._sc = data['sc']
            self._beta = data['beta']
            self._sigma = data['sigma']
            self._iwip0 = data['iwip0']
            self._sco = data['sco']
            if self._use_SRA is None:
                self._use_SRA = data['use_SRA']
            self._K = data['K']
            self._epsilon = data['epsilon']
            self._N = data['N']
            self._demand_supply = data['demand_supply']
            self._probabilies = data['probabilies']
            self._ls = data['ls']
            self._id0 = data['id0']
            self._r_p = data['r_p']
            self._re_p = data['re_p']
            self._fly = data['fly']
            self._ratio = data['ratio']
            self._id0_FW = data["id0_FW"]
            self._fty_p = data["fty_p"]
            self._rr_p = data["rr_p"]

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

    def __find_incompatible_tuples(self, t , k ) -> Set[Tuple[int, int]]:
        ''' Find for one tuple combination (t,k) all tuples (t_,k_), which would be producing together and are incompatible!
        '''

        starting_set = {t + i for i in range(k + self._alpha[0] + 1)}
        incompatible_tuples = set()
        for t_ in range(self._T_No):
            for k_ in range(self._dmax[0]):
                    new_set = {t_ + i_ for i_ in range(k_ + self._alpha[0] + 1)}
                    if starting_set & new_set:
                        incompatible_tuples.add((t_, k_))

        incompatible_tuples.remove((t,k))

        return incompatible_tuples

    def __create_big_omega(self)-> None:
        ''' Set of tuple combinations of Y[m,t,k], which have overlappting time periods and cant be used together
        '''
        self._big_omega = []
        
        for t in range(self._T_No):
            sub_list_incompatible_tuples = []
            for k in range(self.dmax[0]):
                incompatible_tuples = self.__find_incompatible_tuples(t,k)
                sub_list_incompatible_tuples.append(incompatible_tuples)

            self._big_omega.append(sub_list_incompatible_tuples)

    def __find_setup_tuples(self, t) -> Set[Tuple[int, int]]:
        ''' find for one time point t all tuple combinations (t_,k), which could be on setup
        '''

        setup_tuples = set()

        for t_ in range(self._T_No):
            for k in range(self._dmax[0]):
                if t in {num for num in range(t_ + k + 1, t_ + k + self._alpha[0] + 1)}:
                    setup_tuples.add((t_,k))

        return setup_tuples
    
    def __create_big_theta(self) -> None:
        ''' Set of each time point containnig infoirmation which production campaigns Y[m,t,k] could be on setup
        '''
        
        self._big_theta = []
        
        for t in range(self._T_No):
            setup_tuples = self.__find_setup_tuples(t)
            self._big_theta.append(setup_tuples)


    def __find_active_tuples(self,t) -> Set[Tuple[int, int]]:
        ''' FInd all tuples (t_,k) which are active producing in time point t
        '''    
        active_tuples = set()
        for t_ in range(self._T_No):
            for k in range(self._dmax[0]):
                if t_ <= t <= t_ + k:
                    active_tuples.add((t_,k))
        return active_tuples

    def __create_big_phi(self) -> None:
        ''' Create a set for eavh time point t with all active tuples (t_,k) which are producing at time point t
        '''
        self._big_phi = []
        
        for t in range(self._T_No):
            active_tuples = self.__find_active_tuples(t)
            self._big_phi.append(active_tuples)


    def __create_dp(self) -> list[list[list[list[int]]]]:
        ''' Creation of demand in each scenario for each time point for each family type to each location
            where the demand is the same for each location and each time point 
        '''

        # Create a list for the demand of each family
        demand = []

        for s in self._S:
            scenario_demand = []
            for f in self._F:
                family_demand = []
                if self._use_SRA:
                    overall_demand = self._SRA.reduced_scenarios[s][f]
                else: 
                    overall_demand = sum([self._demand_supply[f][i] * self._probabilies[f][i] for i in range(len(self._demand_supply[0]))])

                share = round((overall_demand / len(self._L)) / self._T_No)
                for l in self._L:
                    location_demand = []
                    for t in self._T:

                        location_demand.append(share)

                    family_demand .append(location_demand)
                scenario_demand .append(family_demand )
            demand.append(scenario_demand)

        return demand
    
    def __create_dri(self) -> list[list[int]]:
        ''' Raw milk daily input on day t under scenario s, same for each day t under teh scenario s
        '''

        milk_input = []

        for s in self._S:
            scenario_milk_input = []
            if self._use_SRA:
                milk = self._SRA.reduced_scenarios[s][-1]
            else: 
                milk = sum([self._demand_supply[-1][i] * self._probabilies[-1][i] for i in range(len(self._demand_supply[0]))])

            milk_share = round(milk / self._T_No)
            for t in self._T:
                scenario_milk_input.append(milk_share)

            milk_input.append(scenario_milk_input) 
        
        return milk_input

    def __createScenarioReduction(self) -> None:
        ''' Create the scenario reduction object '''

        self._SRA = Scenario_Analyse(self._demand_supply, self._probabilies, self._K, self._epsilon, self._N)
    

    def __create_dpd(self) -> list[list[list[list[int]]]]:
        ''' Create Demand for each product with ratios'''

        demand = []

        for s in self._S:
            scenario_demand = []
            for f in self._F:
                for ratio in self._ratio[f]:
                    product_demand = []

                    if self._use_SRA:
                        overall_demand = self._SRA.reduced_scenarios[s][f] * ratio
                    else: 
                        overall_demand = sum([self._demand_supply[f][i] * self._probabilies[f][i] for i in range(len(self._demand_supply[0]))]) * ratio

                    share = round(overall_demand / len(self._L) / self._T_No)
                    for l in self._L:
                        location_demand = []
                        for t in self._T:

                            location_demand.append(share)

                        product_demand .append(location_demand)
                    scenario_demand .append(product_demand )
                demand.append(scenario_demand)

        return demand
    
    ###### MANY PROPERTIES TO NOT CHANGE THE VALUES OF THE VARIABLES ######
    @property
    def hl(self) -> int:
        ''' Time span of optimization horizon '''
        return self._hl

    @property
    def fty(self) -> List[int]:
        ''' The type (Fresh or Dry) of family f 
        dry (not refrigerated) for products of the UHT and Powdered Milk families; and fresh (refrigerated), for
        products of the Yogurt and Cheese families

        Dry = 0
        Fresh = 1
        '''

        return self._fty

    @property
    def cty(self) -> List[int]:
        ''' Campaign type for production plant m -> Which work model is used in manufacturing plant m 
        
            0 = Lengthbased
            1 = Shiftbased
        '''

        return self._cty
    
    @property
    def big_omega(self) -> List[Set[Tuple[int, int]]]:
        ''' all possible cmapagign tuples whoch should be blocked for one tuple combination
        '''
        
        return self._big_omega
    
    @property
    def big_phi(self) -> List[Set[Tuple[int, int]]]:
        ''' all possible active campaign tuples for each time point t
        '''
        
        return self._big_phi
    
    @property
    def big_theta(self) -> List[Set[Tuple[int, int]]]:
        ''' all possible active campaign tuples which are causing setup times at time point t
        '''
        
        return self._big_theta

    @property
    def fpr(self) -> List[int]:
        ''' The family produced by manufacturing plant m 
            UHT and Powdered Milk, Yogurt, Cheese
            Differnece between production plants of Powedered Milk and Rest !!!
        '''
        
        return self._fpr

    @property
    def fy(self) -> List[float]:
        ''' Family f production yield for  a unit of processed raw milk 
            UHT and Powdered Milk, Yogurt, Cheese
        '''

        return self._fy

    @property
    def rsc(self) -> int:
        ''' Raw milk third supplier cost '''

        return self._rsc

    @property
    def roc(self) -> int:
        ''' Raw milk over stock cost per volume unit 
        '''

        return self._roc
    
    @property
    def use_SRA(self) -> bool:
        ''' Use of Scenario Reduction Analysis
        ''' 

        return self._use_SRA

    @property
    def el(self) -> List[int]:
        ''' Export lot size in metric tons of family f 
            Lot size is 25 metric ton
        '''

        return self._el

    @property
    def tau(self) -> List[int]:
        ''' Transportation time from factory to distribution center in days
        '''

        return self._tau

    @property
    def i_0(self) -> List[List[int]]:
        ''' Family f Initial inventory at location l.e
        '''

        return self._i_0

    @property
    def i_0_f(self) -> List[int]:
        ''' Family f Initial inventory at FW
        '''

        return self._i_0_f

    @property
    def tl_min(self) -> int:
        ''' Minimum  truckload capacity, respectively.
        '''

        return self._tl_min

    @property
    def tl_max(self) -> int:
        '''  Maximum truckload capacity, respectively.
        '''

        return self._tl_max

    @property
    def r0(self) -> int:
        ''' Raw milk initial inventory.
        '''

        return self._r0

    @property
    def r_max(self) -> int:
        ''' Maximum raw milk inventory.
        '''

        return self._r_max

    @property
    def dmax(self) -> List[int]:
        ''' Maximum campaign length (in days) for plant m. 

        Only one value given for Length-Based Campaign --> Assumnption that shift based campaign are unlimited!
        '''

        return self._dmax

    @property
    def cmin(self) ->  List[int]:
        ''' Minimum daily production capacity at manufacturing plant m 
            Assumption about minimum that it is 0!
            # assumption update: it cannot be 0, because cmin is a divisor in a constraint, so that would lead to division by zero
        '''

        return self._cmin

    @property
    def cmax(self) -> List[int]:
        ''' Maximum daily production capacity at manufacturing plant m 
            Assumption about maximum, but already given! 
            # assumption update: 3 times maximimum number of shifts
        '''

        return self._cmax

    @property
    def alpha(self) -> List[int]:
        ''' Setup time in periods for production plant m 
            Assunmption, that setup is only needed for Powdered Milk!
        '''

        return self._alpha

    @property
    def ost(self) -> List[int]:
        ''' Remaining days to finish an ongoing setup task at manufacturing plant m 
            Assumption no ongoing setup tasks at manufacturing plant m
        '''

        return self._ost

    @property
    def wp(self) -> List[List[int]]:
        ''' m: manufacturing plant, 
            t: time (days), 
            sigma: process time for family produced in manufacturing plant m
            Assumption no ongoing setup tasks at manufacturing plant m
        '''

        return self._wp

    @property
    def el_min(self) -> List[int]:
        ''' F: lots of family f to be exported; here: Minimum number
            Powdered Milk, UHT, Butter, Cheese
        '''

        return self._el_min

    @property
    def el_max(self) -> List[int]:
        ''' F: lots of family f to be exported; here: Maximum number
            Powdered Milk, UHT, Butter, Cheese
        '''

        return self._el_max

    @property
    def is_(self) -> List[float]:
        ''' M: maximum portion of total capacity that can be left
            idle during a production campaign  at manufacturing plant m with [0,1) value#
        '''

        return self._is_

    @property
    def omega_fw(self) -> List[int]:
        ''' factory warehouse shelf-life of products of family f
            Powdered Milk, UHT, Butter, Cheese
            100 as a high number for long time span
        '''

        return self._omega_fw

    @property
    def omega_dc(self) -> List[int]:
        ''' distribution center shelf-life of products of family f
            Powdered Milk, UHT, Butter, Cheese
            100 as a high number for long time span
        '''

        return self._omega_dc

    @property
    def rr(self) -> list[int]:
        ''' revenue from reduced price selling of products of family f over stock (distressed sales) 
            Powdered Milk, UHT, Butter, Cheese
        '''

        return self._rr

    @property
    def r(self) -> List[int]:
        ''' revenue from selling one ton of family f in any distribution center of the Supply Chain 
            Powdered Milk, UHT, Butter, Cheese
        '''

        return self._r

    @property
    def re(self) -> List[int]:
        ''' revenue from exporting a batch of family f 
            UHT and Powdered Milk, Yogurt, Cheese
            only for powdered milk! 
        '''

        return self._re

    @property
    def imax(self) -> List[List[int]]:
        ''' Maximum storage capacities at location l for fresh and dry product families i 
        '''

        return self._imax

    @property
    def zmax(self) -> List[int]:
        ''' For shift-based production, maximum shifts, otherwise 1
            Retrieved from paper
        '''

        return self._zmax

    @property
    def sc(self) -> List[int]:
        ''' Production capacity of the manufacturing plant m per work shift in metric tons
            Retrieved from paper
            0 for lenghtbased production plants
        '''

        return self._sc

    @property
    def beta(self) -> List[float]:
        ''' Deterioration coefficient for products manufactured at factory m 
        '''

        return self._beta

    @property
    def sigma(self) -> List[int]:
        ''' Process time in periods for the family produced at manufacturing plant m

            List for availability of product lines 
            Powdered Milk: Need to be quality tested -> 1 day 
            UHT Milk: Nothing mentioned -> 0 day
            Butter: Nothing mentioned -> 0 day
            Cheese: Ripening phase -> 4 days
        '''

        return self._sigma

    @property
    def iwip0(self) -> List[int]:
        ''' Inventory of work-in-progress from previous planning horizon at manufacturing plant m
        '''

        return self._iwip0
    

    @property
    def sco(self) -> int:
        ''' Setup costs in Monetary Units
        '''

        return self._sco

    
    @property
    def SRA(self) -> Scenario_Analyse:
        ''' Scenario Reduction Analysis Instance with all data and results
        '''

        return self._SRA

    @property
    def dp(self) -> list[list[list[list[int]]]]:
        ''' Family demand for distribution center l on day t under scenario s.
        '''
        pass

        return self._dp

    @property
    def rho(self) -> list[float]:
        ''' The probability of scenario s.
        '''

        return self._rho

    @property
    def dri(self) -> list[list[int]]:
        ''' Raw milk daily input on day t under scenario s
        '''

        return self._dri

    @property
    def T(self) -> range:
        ''' Range for time span of optimization horizon
        '''

        return self._T

    @property
    def F(self) -> range:
        ''' Range for product family types 
        '''
        
        return self._F

    @property
    def FT(self) -> range:
        ''' Range for family types, fresh or dry 
        '''

        return self._FT

    @property
    def MP(self) -> range:
        ''' Range for manufacturing plants
        '''

        return self._MP

    @property
    def CT(self) -> range:
        ''' Range for production camp. types. length or shift based
        '''

        return self._CT

    @property
    def L(self) -> range:
        ''' Range for distribution centers
        '''

        return self._L

    @property
    def S(self) -> range:
        ''' Range for reduced scenarios
        '''

        return self._S
    
    ###### DETAILED MODEL ###### 

    @property
    def P(self) -> range:
        ''' Range for products
        '''

        return self._P

    @property
    def ls(self) -> list[int]:
        ''' Product p export lot size, expressed in metric tons.
        '''
        return self._ls

    @property
    def id0(self) -> list[list[int]]:
        ''' Product p initial inventory at any location l ∈ L∪ < {FW}.
        '''
        return self._id0
    
    @property
    def r_p(self) -> list[int]:
        ''' Product p revenue from selling one ton in any distribution center of the supply chain.
        '''
        return self._r_p
    
    @property
    def tc(self) -> list[list[int]]:
        ''' Product p transportation cost from factory to distribution center l.
        '''

        return self._tc
    
    @property
    def re_p(self) -> list[int]:
        ''' Product p revenue from exporting a batch.
        '''
        return self._re_p
    
    @property
    def fly(self) -> list[int]:
        ''' Product p family type.
        '''
        return self._fly

    @property
    def dpd (self) -> list[list[list[list[int]]]]:
        ''' Product p demand for distribution center l on day t under scenario s.
        '''
        return self._dpd
    
    @property
    def id0_FW(self) -> list[list[int]]:
        ''' Product p initial inventory at FW.
        '''
        return self._id0_FW
    

    @property
    def fty_p(self) -> list[int]:
        ''' Product p family type.
        '''
        return self._fty_p
    
    @property
    def rr_p(self) -> list[int]:
        ''' Product p revenue from reduced price selling of products of family f over stock (distressed sales).
        '''
        return self._rr_p


class S_star(Parameters):
    ''' 
    Class to calculate the s_star value (mean values of the demand).
    Class S_star that inherits from class Parameters and is used to calculate the s_star value (mean values of the demand)
    '''

    def __init__(self, json_file_path: str = "data/case_study_data.json"):
        ''' 
        Constructor for this class.
        
        Parameters:
            json_file_path (str): Path to the file with the datafile (JSON file).
        '''
        self._use_SRA = False  # False to indicate that we do not want to use the SRA

        super().__init__(json_file_path)

        self.__calculate_s_star()
        self._s_star = 0

    def __calculate_s_star(self) -> None:
        ''' 
        Calculate the mean values of the demand.
        
        This is a placeholder function to be implemented with actual calculation logic.
        '''
        pass  # Placeholder for actual calculation logic

    def recreate_dp(self) -> List[List[List[List[float]]]]:
        ''' 
        Recreate the demand values adjusted by the expected value (rho).
        
        Returns:
            List[List[List[List[float]]]]: Adjusted demand values.
        '''
        
        dp = [[
            [
                [
                    self._dp[s][f][l][t] * self._rho[s] for s in self._S  # / len(self._S) 
                    for t in self._T
                ]
                for l in self._L
            ]
            for f in self._F
        ]]

        return dp

    def recreate_dri(self) -> List[List[float]]:
        ''' 
        Recreate the raw milk input values adjusted by the expected value (rho).
        
        Returns:
            List[List[float]]: Adjusted raw milk input values.
        '''
        dri = [
            [
                self._dri[s][t] * self._rho[s] for s in self._S  #/ len(self._S) 
                for t in self._T
            ]
        ]

        return dri

    def calculate_expected_value(self) -> List[float]:
        ''' 
        Calculate the expected value (rho) of all scenarios.
        
        Returns:
            List[float]: List containing the expected value.
        '''
        rho = [sum(self._rho)]

        return rho  

    @property
    def s_star(self) -> float:
        ''' 
        Mean values of the demand.
        
        Returns:
            float: The mean value of the demand.
        '''
        return self._s_star
