#### Script for creating instances of different types of variables in the model ####

from parameters import Parameters
import gurobipy as gp
from gurobipy import GRB

class DecisionVariablesModel1:
    ''' Overall class for decision variables of the model'''

    def __init__(self, model: gp.Model, data: Parameters):
        self.first_stage = self.FirstStage(model, data)
        self.second_stage = self.SecondStage(model, data)
        self.binary = self.Binary(model, data)
        self.integer = self.Integer(model, data)

    class FirstStage:
        ''' Continuous decision variables of the first stage of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            self.EXI = model.addVar(vtype=GRB.CONTINUOUS, name="EXI")
            self.ENB = model.addVar(name="ENB")        # for debugging
            self.TCOST = model.addVar(name="TCOST")     # for debugging
            self.SN = model.addVar(lb=0, name="SN")
            self.RM = model.addVars(data.T, lb=0, name="RMt")
            self.IF = model.addVars(data.F, data.T, lb=0, name="IFf_t")
            self.FP = model.addVars(data.F, data.T, lb=0, name="FPf_t")
            self.V = model.addVars(data.F, data.L, data.T, lb=0, name="Vi_l_t")
            self.DV = model.addVars(data.F, data.L, data.T, lb=0, name="DVf_l_t")
            self.A = model.addVars(data.MP, data.T, lb=0, name="Am_t")
            self.MO = model.addVars(data.MP, data.T, lb=0, name="MOm_t")
            self.IWIP = model.addVars(data.MP, data.T, lb=0, name="IWIPm_t")
            self.Q = model.addVars(data.MP, data.T, lb=0, name="Qm_t")
            self.Z1 = model.addVars(data.MP, data.T, name="Z1m_t")
            self.Z2 = model.addVars(data.MP, data.T, name="Z2m_t")
            self.Aux = model.addVars(data.MP, data.T, lb=0, name="Auxm_t")
            ### Variabels needed for the detailed planning model
            # self.ED = model.addVars(data.P, data.T, lb=0, name="EDp_t")
            # self.PD = model.addVars(data.P, data.T, lb=0, name="PDp_t")
            # self.PS = model.addVars(data.P, data.L ,data.T, lb=0, name="PSp_l_t")
            # self.IFD = model.addVars(data.P, data.T, lb=0, name="IFDp_t")
            # self.VD = model.addVars(data.FT, data.L, data.T, lb=0, name="VDi_l_t")

    class SecondStage:
        ''' Continuous decision variables of the second stage of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            self.SA = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="SAs_f_l_t")
            self.SO = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="SOs_f_l_t")
            self.OS = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="OSs_f_l_t")
            self.RC = model.addVars(data.S, lb=0, name="RCs_s")
            self.RS = model.addVars(data.S, data.T, lb=0, name="RSs_t")
            self.RO = model.addVars(data.S, data.T, lb=0, name="ROs_t")
            self.RI = model.addVars(data.S, data.T, lb=0, name="RIs_t")
            self.ID = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="IDs_f_l_t")
            ### Variabels needed for the detailed planning model
            # self.RETURN = model.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="RETURN")
            # self.COST = model.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="COST")
            # self.IDD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="IDDs_p_l_t")
            # self.SOD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="SODs_p_l_t")
            # self.OSD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="OSDs_p_l_t")

    class Binary:
        ''' Binary decision variables of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            self.R1 = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="R1m_t")
            self.R2 = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="R2m_t")
            self.Y = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="Ym_t")

    class Integer:
        ''' Integer decision variables of the model '''
        
        def __init__(self, model: gp.Model, data: Parameters):
            self.TR = model.addVars(data.FT, data.L, data.T, vtype=GRB.INTEGER, lb=0,ub=30, name="TRi_l_t") ### New IMPLEMENTED UPPER BOUND !!! 
            self.E = model.addVars(data.F, data.T, vtype=GRB.INTEGER, lb=0, name="Ef_t")
            self.Z = model.addVars(data.MP, data.T, vtype=GRB.INTEGER, lb=0, name="Zm_t")
            ### Variabels needed for the detailed planning model
            # self.TRD = model.addVars(data.FT, data.L, data.T, vtype=GRB.INTEGER, lb=0, name="TRDi_l_t")

            for m in data.MP:
                for t in data.T:
                    self.Z[(m, t)].ub = data.zmax[m]


class DecisionVariablesModel2:
    ''' Overall class for decision variables of the model'''

    def __init__(self, model: gp.Model, data: Parameters):
        self.first_stage = self.FirstStage(model, data)
        self.second_stage = self.SecondStage(model, data)
        self.binary = self.Binary(model, data)
        self.integer = self.Integer(model, data)

    class FirstStage:
        ''' Continuous decision variables of the first stage of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            ### Variabels needed for the detailed planning model
            self.ED = model.addVars(data.P, data.T, lb=0, name="EDp_t")
            self.PD = model.addVars(data.P, data.T, lb=0, name="PDp_t")
            self.PS = model.addVars(data.P, data.L ,data.T, lb=0, name="PSp_l_t")
            self.IFD = model.addVars(data.P, data.T, lb=0, name="IFDp_t")
            self.VD = model.addVars(data.FT, data.L, data.T, lb=0, name="VDi_l_t")

    class SecondStage:
        ''' Continuous decision variables of the second stage of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            ### Variabels needed for the detailed planning model
            self.RETURN = model.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="RETURN")
            self.COST = model.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="COST")
            self.IDD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="IDDs_p_l_t")
            self.SOD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="SODs_p_l_t")
            self.OSD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="OSDs_p_l_t")

    class Binary:
        ''' Binary decision variables of the model '''

        def __init__(self, model: gp.Model, data: Parameters):
            #self.R1 = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="R1m_t")
            #self.R2 = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="R2m_t")
            #self.Y = model.addVars(data.MP, data.T, vtype=GRB.BINARY, name="Ym_t")
            pass

    class Integer:
        ''' Integer decision variables of the model '''
        
        def __init__(self, model: gp.Model, data: Parameters):
            ### Variabels needed for the detailed planning model
            self.TRD = model.addVars(data.FT, data.L, data.T, vtype=GRB.INTEGER, lb=0, name="TRDi_l_t")
