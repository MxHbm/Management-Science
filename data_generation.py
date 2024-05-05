
import random

### RANODM NUMBER GENERATOR 

# Create an instance of the Random class
rng = random.Random()

# Seed the random number generator for reproducibility
rng.seed(42)

from gurobipy import *
from gurobipy import GRB



### Script for generating data fpr our model
class Parameters_FirstStage:

    def __init__(self, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
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
        self.hl = self.create_hl()
        #Haoran
        self.fty = self.create_fty()
        self.cty = self.create_cty()
        self.fpr = self.create_fpr()
        self.fy = self.create_fy()
        self.rsc = self.create_rsc()
        self.roc = self.create_roc()
        self.el = self.create_el()
        self.tau = self.create_tau()
        #Julien
        self.i_0 = self.create_i_0(F, L)
        self.tl_min = self.create_tl_min(F)
        self.tl_max = self.create_tl_max(F)
        self.r0 = self.create_r0(F)
        self.r_max = self.create_r_max(F)
        self.dmax = self.create_dmax(T, MP)
        self.cmin = self.create_cmin(MP)
        self.cmax = self.create_cmax(MP)
        self.alpha = self.create_alpha(T, MP)
        self.ost = self.create_ost(T, MP)
        #Christoph
        self.wp = self.create_wp(MP, T)
        self.el_min = self.create_el_min(F)
        self.el_max = self.create_el_max(F)
        self.is_ = self.create_is(MP)
        self.omega_fw = self.create_omega_fw(F)
        self.omega_dc = self.create_omega_dc(F)
        self.rr = self.create_rr(F)
        self.r = self.create_r(F)
        self.re = self.create_re(F)
        #Max
        self.imax = self.create_imax()
        self.zmax = self.create_zmax()
        self.sc = self.create_sc()
        self.beta = self.create_beta(MP)
        self.sigma = self.create_sigma()
        self.iwip0 = self.create_iwip0()
        self.tc = self.create_tc()
        self.sco = self.create_sco()

        # Additonal
        self.names_DC = self.create_names_DC()

    def create_hl(self) -> int:
        ''' Add description of the function here '''
        hl = 30         # 30 days in the paper 
        hl = 5         # just for debugging (not real number)   
        return hl

    def create_fty(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_cty(self) -> list:
        ''' Campaign type for production plant m -> Which work model is used in manufacturing plant m 
        
            0 = Lengthbased
            1 = Shiftbased
        '''
        
        cty = [0,1,1,1]
        
        return cty

    def create_fpr(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_fy(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_rsc(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_roc(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_el(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_tau(self) -> list[int]:
        ''' Transportation time from factory to distribution center in days'''

        transport_time_factory_dc = [2,1,1,2,0,1,0,2,1]
        
        return transport_time_factory_dc

    def create_i_0(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_tl_min(self) -> list:
        ''' Add description of the function here '''
        tl_min = 0      # just for debugging (not real number)
        return tl_min

    def create_tl_max(self) -> list:
        ''' Add description of the function here '''
        tl_max = 250     # just for debugging (not real number)
        return tl_max

    def create_r0(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_r_max(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_dmax(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_cmin(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_cmax(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_alpha(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_ost(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_wp(self, M, T ) -> list:
        ''' m: manufacturing plant, 
            t: time (days), 
            sigma: process time for family produced in manufacturing plant m'''
        # self.sigma
        pass

    def create_el_min(self, F) -> list:
        ''' F: lots of family f to be exported; here: Minimum number'''
        pass

    def create_el_max(self, F) -> list:
        ''' F: lots of family f to be exported; here: Maximum number'''

        pass

    def create_is(self, M) -> list:
        ''' M: maximum portion of total capacity that can be left idle during a production campaign  at manufacturing plant m with [0,1) value'''
        pass

    def create_omega_fw(self, F) -> list:
        ''' factory warehouse shelf-life of products of family f'''
        pass

    def create_omega_dc(self, F) -> list:
        ''' distribution center shelf-life of products of family f'''
        pass

    def create_rr(self, F) -> list:
        ''' revenue from reduced price selling of products of family f over stock (distressed sales) '''
        pass

    def create_r(self, F) -> list:
        ''' revenue from selling one ton of family f in any distribution center of the Supply Chain '''
        pass

    def create_re(self, F) -> list:
        ''' revenue from exporting a batch of family f '''
        pass

    def create_imax(self) -> list[list[int]]:
        ''' Maximum storage capacities at location l for fresh and dry product families '''

        max_storage_product_groups = [[12,10],[68, 114],[16, 35],[16,40],[9, 27],
                                    [31,54],[20, 81],[20,58],[58,195]]
        
        return max_storage_product_groups

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

    def create_sigma(self) -> list:
        ''' Process time in periods for the family produced at manufacturing plant m

        List for availability of product lines 
        Powdered Milk: Need to be quality tested -> 1 day 
        UHT Milk: Nothing mentioned -> 0 day
        Yogurt: Nothing mentioned -> 0 day
        Cheese: Ripening phase -> 4 days'''

        # Powdered Milk, UHT Milk, Yogurt, Cheese

        sigma = [1,0,0,4]

        return sigma 

    def create_iwip0(self) -> list:
        ''' Inventory of work-in-progress from previous planning horizon at manufacturing plant m '''
        
        # No data given -> Assume there is nothing given

        iwip = [0,0,0,0]

        return iwip

    def create_tc(self) -> list[list[int]]:
        ''' Transportation costs from the production complex to the distribution center '''
        
        transport_costs_product_group_matrix = [[15.641,13.034],[4.956, 4.13],[10.332,8.61],[14.818, 12.348],[0.067, 0.056],
                                                [14.364, 11.97],[4.032, 3.36],[21.638,18.032],[9.021,7.518]]
        
        return transport_costs_product_group_matrix

    def create_sco(self) -> int:
        ''' Setup costs in Monetary Units'''
        
        setup = 20 # unit is MU

        return setup

    def create_names_DC(self) -> list[str]: 
        """ Names of the distribution centers """

        return ["DC-SAL", "DC-CBA", "DC-CTE","DC-POS","DC-RAF","DC-MZA", "DC-ROS", "DC_NQN", "DC-BUE"]


class DecisionVariables_FirstStage:

    def __init__(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        """    self.CreateDecisionVariables(model, T, F, S, FT, MP, CT, L)

    def CreateDecisionVariables(self, model, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        ''' Add description of the function here '''
    """
        self.EXI = model.addVar(vtype=GRB.CONTINUOUS, name="EXI")
        self.ENB = model.addVar(lb=0, name="ENB")
        self.TCOST = model.addVar(lb=0, name="TCOST")
        self.SN = model.addVar(lb=0, name="SN")
        self.RMt = model.addVars(MP, T, lb=0, name="RMt")
        self.IFf_t = model.addVars(F, T, lb=0, name="IFf_t")
        self.FPf_t = model.addVars(F, T, lb=0, name="FPf_t")
        self.Vi_l_t = model.addVars(F, L, T, lb=0, name="Vi_l_t")
        self.DVf_l_t = model.addVars(F, L, T, lb=0, name="DVf_l_t")
        self.Am_t = model.addVars(MP, T, lb=0, name="Am_t")
        self.MOm_t = model.addVars(MP, T, lb=0, name="MOm_t")
        self.IWIPm_t = model.addVars(MP, T, lb=0, name="IWIPm_t")
        self.Qm_t = model.addVars(MP, T, lb=0, name="Qm_t")
        self.Z1m_t = model.addVars(MP, T, vtype=GRB.BINARY, name="Z1m_t")
        self.Z2m_t = model.addVars(MP, T, vtype=GRB.BINARY, name="Z2m_t")
        self.Auxm_t = model.addVars(MP, T, lb=0, name="Auxm_t")

        #return model

class IntegerVariables:

    def __init__(self, model, parameters_FirstStage, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):
        self.TRi_l_t = model.addVars(FT, L, T, lb=0, name="TRi_l_t")
        self.Ef_t = model.addVars(F, T, lb=0, name="Ef_t")
        self.Zm_t = model.addVars(MP, T, vtype=GRB.INTEGER, lb=0, ub=parameters_FirstStage.zmax, name="Zm_t")
        

