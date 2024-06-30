from parameters import Parameters
import gurobipy as gp
from gurobipy import GRB

class DecisionVariables:
    ''' Overall class for decision variables of both models '''

    def __init__(self, model: gp.Model, data: Parameters):
        self.first_stage = self.FirstStage(model, data)
        self.second_stage = self.SecondStage(model, data)
        self.binary = self.Binary(model, data)
        self.integer = self.Integer(model, data)

    class FirstStage:
        ''' Continuous decision variables of the first stage of both models '''

        def __init__(self, model: gp.Model, data: Parameters):
            # Family Aggregated Model
            self.EXI = model.addVar(vtype=GRB.CONTINUOUS, name="EXI")
            self.ENB = model.addVar(name="ENB")        # for debugging
            self.TCOST = model.addVar(name="TCOST")     # for debugging
            self.SN = model.addVar(lb=0, name="SN")
            self.RM = model.addVars(data.T, lb=0, name="RMt")
            self.IF = model.addVars(data.F, data.T, lb=0, name="IFf_t")
            self.FP = model.addVars(data.F, data.T, lb=0, name="FPf_t")
            self.V = model.addVars(data.F, data.L, data.T, lb=0, name="Vi_l_t")
            self.DV = model.addVars(data.F, data.L, data.T, lb=0, name="DVf_l_t")
            self.MO = model.addVars(data.MP, data.T, lb=0, name="MOm_t")
            self.IWIP = model.addVars(data.MP, data.T, lb=0, name="IWIPm_t")
            self.Q = model.addVars(data.MP, data.T, lb=0, name="Qm_t")

            # Detailed Planning Model
            self.ED = model.addVars(data.P, data.T, lb=0, name="EDp_t")
            self.PD = model.addVars(data.P, data.T, lb=0, name="PDp_t")
            self.PS = model.addVars(data.P, data.L, data.T, lb=0, name="PSp_l_t")
            self.IFD = model.addVars(data.P, data.T, lb=0, name="IFDp_t")
            self.VD = model.addVars(data.FT, data.L, data.T, lb=0, name="VDi_l_t")

    class SecondStage:
        ''' Continuous decision variables of the second stage of both models '''

        def __init__(self, model: gp.Model, data: Parameters):
            # Family Aggregated Model
            self.SA = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="SAs_f_l_t")
            self.SO = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="SOs_f_l_t")
            self.OS = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="OSs_f_l_t")
            self.RC = model.addVars(data.S, lb=0, name="RCs_s")
            self.RS = model.addVars(data.S, data.T, lb=0, name="RSs_t")
            self.RO = model.addVars(data.S, data.T, lb=0, name="ROs_t")
            self.RI = model.addVars(data.S, data.T, lb=0, name="RIs_t")
            self.ID = model.addVars(data.S, data.F, data.L, data.T, lb=0, name="IDs_f_l_t")

            # Detailed Planning Model
            self.RETURN = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="RETURN")
            self.COST = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="COST")
            self.IDD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="IDDs_p_l_t")
            self.SOD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="SODs_p_l_t")
            self.OSD = model.addVars(data.S, data.P, data.L, data.T, lb=0, name="OSDs_p_l_t")

    class Binary:
        ''' Binary decision variables of both models '''

        def __init__(self, model: gp.Model, data: Parameters):
            # Family Aggregated Model
            self.Y = model.addVars(data.MP, data.T, data.dmax[0], vtype=GRB.BINARY, name="Ym_t")

            # Detailed Planning Model
            # No binary variables in Detailed Planning Model

    class Integer:
        ''' Integer decision variables of both models '''
        
        def __init__(self, model: gp.Model, data: Parameters):
            # Family Aggregated Model
            self.TR = model.addVars(data.FT, data.L, data.T, vtype=GRB.INTEGER, lb=0, name="TRi_l_t")
            self.E = model.addVars(data.F, data.T, vtype=GRB.INTEGER, lb=0, name="Ef_t")
            self.Z = model.addVars(data.MP, data.T, vtype=GRB.INTEGER, lb=0, name="Zm_t")

            for m in data.MP:
                for t in data.T:
                    self.Z[(m, t)].ub = data.zmax[m]

            # Detailed Planning Model
            self.TRD = model.addVars(data.FT, data.L, data.T, vtype=GRB.INTEGER, lb=0, name="TRDi_l_t")
