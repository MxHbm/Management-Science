
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
import pandas as pd


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
        

