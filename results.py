import pandas as pd
from parameters import Parameters
import matplotlib.pyplot as plt
import numpy as np
import gurobipy as gp
''' results.py '''

class Results:
    def __init__(self, model1, model2, emvpModel, mvpModel, data:Parameters):
        self.family_model = model1
        self.detailed_model = model2
        self.emvp_model = emvpModel
        self.mvp_model = mvpModel
        self.data = data

        self.T = data.T
        self.F = data.F
        self.S = data.S
        self.FT = data.FT
        self.MP = data.MP
        self.CT = data.CT
        self.L = data.L
        self.P = data.P

        self.sales_t = self.create_sales_t()
        self.lost_sales_t = self.create_lost_sales_t()
        self.distressed_sales_t = self.create_distressed_sales_t()
        self.raw_material_losses_t = self.create_raw_material_losses_t()
        self.raw_material_purchase_t = self.create_raw_material_purchase_t()
        self.exports_t = self.create_exports_t()
        self.production_t = self.create_production_t()
        self.product_shipped_t = self.create_product_shipped_t()
        self.sales_income_mu = self.create_sales_income_mu()
        self.distressed_sales_mu = self.create_distressed_sales_mu()
        self.raw_material_losses_cost_mu = self.create_raw_material_losses_cost_mu()
        self.raw_material_purchase_cost_mu = self.create_raw_material_purchase_cost_mu()
        self.exports_income_mu = self.create_exports_income_mu()
        self.cost_shipped_dc_mu = self.create_cost_shipped_dc_mu()
        self.setups_cost_mu = self.create_setups_cost_mu()
        self.expected_net_benefits_mu = self.create_expected_net_benefits_mu()

        # new 
        self.trucks_required = self.create_trucks_required()

        pd.set_option('display.width', 100)
        self.create_result_visualization(self.family_model, self.detailed_model, self.data)

        # self.evaluate_cost_distribution(self.family_model, self.detailed_model)
        pass

    def paper_values_table6(self):
        data = {
            'Metric': ['Sales [t]', 'Lost Sales [t]', 'Distressed Sales of Products [t]', 'Raw Material Losses [t]', 'Raw Material Purchase [t]', 'Exports [t]', 'Production [t]', 'Product shipped to DC [t]', 'Sales Income [MU]', 'Distressed Sales of Products [MU]', 'Raw Material Losses Cost [MU]', 'Raw Material Purchase Cost [MU]', 'Exports Income [MU]', 'Cost for shipped to DC [MU]', 'Setups Cost [MU]', 'Expected Net Benefits [MU]'],
            'SP': [12815, 1715.2, 3694.1, 22951, 1078.4, 975, 16561, 15556, 62241, 3516, 22951, 2156.90, 4875, 10814, 40, 34670.1],
            'EMVP': [11149, 3381, 1410.2, 20334, 4471.9, 2500, 14460, 11607, 53541, 752, 20334, 8943.7, 12500, 8798.5, 80, 28636.8],
            'Deviation': ['+14.9%', '-49.3%', '+162.0%', '+12.9%', '-75.9%', '-61.0%', '+14.5%', '+34.0%', '+16.2%', '+367.5%', '+12.9%', '-75.9%', '-61.0%', '+22.9%', '-50.0%', '+21.1%']
        }
        df = pd.DataFrame(data)
        return df


    def paper_values_table8(self):
        data = {
            'Metric': ['Production [t]', 'Production [t]', 'Production [t]', 'Production [t]', 
                       'N° of PM Export Lots', 'Processed Raw Milk [t]', 
                       'Required trucks', 'Required trucks',  'Required trucks', 
                       'DCs Expected Stockout days', 'DCs Expected Stockout days', 'DCs Expected Stockout days', 'DCs Expected Stockout days', 
                       'DCs Expected Overstock days', 'DCs Expected Overstock days', 'DCs Expected Overstock days', 
                       'Expected number of days with raw milk Overstock', 
                       'Expected number of days with raw milk bought at premium price', 
                       'Expected Sales (MU)', 'Expected Raw Milk Costs (MU)', 'Expected Net Benefits (MU)'] ,
            'Sub-Metric': ['UHT', 'Milk', 'Yogurt', 'Cheese', 
                           'N° of PM Export Lots', 'Processed Raw Milk [t]', 
                           'Fresh', 'Dry', 'UHT', 
                           'Powdered Milk', 'Yogurt', 'Cheese', 'UHT', 
                           'Powdered Milk', 'Yogurt', 'Cheese', 
                           'Raw Milk', 'Raw Milk', 
                           'Sales', 'Raw Milk', 'Net Benefits'] ,
            'SP':   [9881.6, 1938, 4465.3, 276.4, 39,   33759, 598, 1348,  9.7,  5.5, 10,    6.7, 3.5, 3.8,  6.4, 2.3, 10.5, 2.2, 62241, 25107, 34670.1],
            'EMVP': [6600,   3360, 4499.8, None,  100, 397769, 554,  910, 20.2, 16.1, 13.1, 29.7, 7.9, 4.8, 18.1, 1.2, 12.1, 9,   53541, 29277, 28636.8]
        }
        
        df = pd.DataFrame(data)
        df.set_index(['Metric', 'Sub-Metric'], inplace=True, drop=True)

        return df
        #df = pd.DataFrame(data)
        #return df

    def create_sales_t(self):
        # Compute the value for 'Sales [t]'

        sales_family_t = 0
        sales_detailed_t = 0
        sales_mvp_t = 0
        sales_emvp_t = 0


        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                            so = self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            dp = self.data.dp[s][f][l][t]

                            sales_family_t += dp - so

                            # mvp
                            if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                                sales_mvp_t += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
        
        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                            

                            sod = self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                            dpd = self.data.dpd[s][p][l][t]

                            sales_detailed_t += dpd - sod

                            if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                                sod_emvp = self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X

                            sales_emvp_t += dpd - sod_emvp

                        # if self.family_model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]') is not None:
                        #     sales_t += self.family_model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]').X


        return [sales_family_t, sales_detailed_t,  sales_mvp_t, sales_emvp_t]

    def create_lost_sales_t(self):
        # Compute the value for 'Lost Sales [t]'

        lost_sales_t_detailed = 0
        lost_sales_t_family = 0
        lost_sales_t_emvp = 0
        lost_sales_t_mvp = 0


        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                        lost_sales_t_family += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X


                        if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                            lost_sales_t_mvp += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X       
                            
        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                        lost_sales_t_detailed += self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X

                        # emvp
                        if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                            lost_sales_t_emvp += self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X



        # return [lost_sales_t_family, lost_sales_t_detailed]
        return [lost_sales_t_family, lost_sales_t_detailed, lost_sales_t_mvp, lost_sales_t_emvp]

    def create_distressed_sales_t(self):
        # Compute the value for 'Distressed Sales of Products [t]'

        distressed_sales_family = 0
        distressed_sales_detailed = 0
        distressed_sales_emvp = 0
        distressed_sales_mvp = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                        # OS 
                        distressed_sales_family += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X


                        if self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]') is not None:
                            distressed_sales_mvp += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X

        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                        distressed_sales_detailed += self.detailed_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X

                        # emvp
                        if self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]') is not None:
                            distressed_sales_emvp += self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X
                        
                        

        return [distressed_sales_family, distressed_sales_detailed, distressed_sales_mvp, distressed_sales_emvp]

    def create_raw_material_losses_t(self):
        # Compute the value for 'Raw Material Losses [t]'

        raw_material_losses_family_t = 0
        raw_material_losses_detailed_t = 0
        raw_material_losses_mvp_t = 0
        raw_material_losses_emvp_t = 0

        for s in self.S:
            for t in self.T:
                raw_material_losses_family_t += self.family_model.getVarByName(f'ROs_t[{s},{t}]').X
                # raw_material_losses_detailed_t += self.detailed_model.getVarByName(f'ROs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_mvp_t += self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X

                # emvp
                if self.emvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_emvp_t += self.emvp_model.getVarByName(f'ROs_t[{s},{t}]').X


                # if self.family_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                #     raw_material_losses_t += self.family_model.getVarByName(f'ROs_t[{s},{t}]').Obj
        return [raw_material_losses_family_t, raw_material_losses_family_t, raw_material_losses_mvp_t, raw_material_losses_emvp_t]

    def create_raw_material_purchase_t(self):
        # Compute the value for 'Raw Material Purchase [t]'

        raw_material_purchase_family_t = 0
        raw_material_purchase_detailed_t = 0
        raw_material_purchase_mvp_t = 0
        raw_material_purchase_emvp_t = 0

        for s in self.S:
            for t in self.T:
                if self.family_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_family_t += self.family_model.getVarByName(f'RSs_t[{s},{t}]').X
                #raw_material_purchase_detailed_t += self.detailed_model.getVarByName(f'RSs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_mvp_t += self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X
                
                # emvp
                if self.emvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_emvp_t += self.emvp_model.getVarByName(f'RSs_t[{s},{t}]').X

        return [raw_material_purchase_family_t, raw_material_purchase_family_t, raw_material_purchase_mvp_t, raw_material_purchase_emvp_t]

    def create_exports_t(self):
        # Compute the value for 'Exports [t]'

        exports_family_t = 0
        exports_detailed_t = 0
        exports_mvp_t = 0
        exports_emvp_t = 0

        for f in self.F:
            for t in self.T:
                exports_family_t += self.family_model.getVarByName(f'Ef_t[{f},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'Ef_t[{f},{t}]') is not None:
                    exports_mvp_t += self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X
        
        for p in self.MP:
            for t in self.T:
                exports_detailed_t += self.detailed_model.getVarByName(f'EDp_t[{p},{t}]').X

                if self.emvp_model.getVarByName(f'EDp_t[{p},{t}]') is not None:
                    exports_emvp_t += self.emvp_model.getVarByName(f'EDp_t[{p},{t}]').X

        return [exports_family_t, exports_detailed_t, exports_mvp_t, exports_emvp_t]

    def create_production_t(self):
        # Compute the value for 'Production [t]'

        production_family_t = 0
        production_detailed_t = 0
        production_mvp_t = 0
        production_emvp_t = 0

        for f in self.F:
            for t in self.T:
                production_family_t += self.family_model.getVarByName(f'FPf_t[{f},{t}]').X

                if self.detailed_model.getVarByName(f'FPf_t[{f},{t}]') is not None:
                    production_detailed_t += self.detailed_model.getVarByName(f'FPf_t[{f},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'FPf_t[{f},{t}]') is not None:
                    production_mvp_t += self.mvp_model.getVarByName(f'FPf_t[{f},{t}]').X
                
                # emvp
                if self.emvp_model.getVarByName(f'FPf_t[{f},{t}]') is not None:
                    production_emvp_t += self.emvp_model.getVarByName(f'FPf_t[{f},{t}]').X

                # if self.family_model.getVarByName(f'FPf_t[{f},{t}]') is not None:
                #     production_t += self.family_model.getVarByName(f'FPf_t[{f},{t}]').Obj

        production_detailed_t = production_family_t
        return [production_family_t, production_detailed_t, production_mvp_t, production_emvp_t]

    def create_product_shipped_t(self):
        # Compute the value for 'Product shipped to DC [t]'

        product_shipped_family_t = 0
        product_shipped_detailed_t = 0
        product_shipped_mvp_t = 0
        product_shipped_emvp_t = 0

        for i in self.FT:
            for l in self.L:
                for t in self.T:
                    product_shipped_family_t += self.family_model.getVarByName(f'Vi_l_t[{i},{l},{t}]').X 

                    if self.detailed_model.getVarByName(f'Vi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_detailed_t += self.detailed_model.getVarByName(f'Vi_l_t[{i},{l},{t}]').X 

                    # mvp
                    if self.mvp_model.getVarByName(f'Vi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_mvp_t += self.mvp_model.getVarByName(f'Vi_l_t[{i},{l},{t}]').X 

                    # emvp
                    if self.emvp_model.getVarByName(f'Vi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_emvp_t += self.emvp_model.getVarByName(f'Vi_l_t[{i},{l},{t}]').X 

        product_shipped_detailed_t = product_shipped_family_t
        return [product_shipped_family_t, product_shipped_detailed_t, product_shipped_mvp_t, product_shipped_emvp_t]

    def create_sales_income_mu(self):
        # Compute the value for 'Sales Income [MU]'

        sales_income_family_mu = 0
        sales_income_detailed_mu = 0
        sales_income_mvp_mu = 0
        sales_income_emvp_mu = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                            so = self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            dp = self.data.dp[s][f][l][t]

                            sales_income_family_mu += (dp - so) * self.data.r[f]


                            if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                                sales_income_mvp_mu += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X

        for s in self.S:
            for p in self.MP:
                for l in self.L:
                    for t in self.T:
                            
                            sod = self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                            dpd = self.data.dpd[s][p][l][t]

                            sales_income_detailed_mu += (dpd - sod) * self.data.r_p[p]

                            # emvp
                            if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                                sod_emvp = self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X

                            sales_income_emvp_mu += (dpd - sod_emvp)  * self.data.r_p[p]

        return [sales_income_family_mu, sales_income_detailed_mu, sales_income_mvp_mu, sales_income_emvp_mu]

    def create_distressed_sales_mu(self):
        # Compute the value for 'Distressed Sales of Products [MU]'

        distressed_sales_family_mu = 0
        distressed_sales_detailed_mu = 0
        distressed_sales_mvp_mu = 0
        distressed_sales_emvp_mu = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                        # OS 
                        distressed_sales_family_mu += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]

                        # mvp
                        if self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]') is not None:
                            distressed_sales_mvp_mu += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]
        for s in self.S:
            for p in self.MP:
                for l in self.L:
                    for t in self.T:
                        # OSD
                        distressed_sales_detailed_mu += self.detailed_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p]

                        # emvp
                        if self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]') is not None:
                            distressed_sales_emvp_mu += self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p]
                        
                        

        return [distressed_sales_family_mu, distressed_sales_detailed_mu, distressed_sales_mvp_mu, distressed_sales_emvp_mu]


        return [0, 0, 0]

    def create_raw_material_losses_cost_mu(self):
        # Compute the value for 'Raw Material Losses Cost [MU]'

        raw_material_losses_family_mu = 0
        raw_material_losses_detailed_mu = 0
        raw_material_losses_mvp_mu = 0
        raw_material_losses_emvp_mu = 0

        for s in self.S:
            for t in self.T:
                raw_material_losses_family_mu += self.family_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc
                # raw_material_losses_detailed_t += self.detailed_model.getVarByName(f'ROs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_mvp_mu += self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc

                # emvp
                if self.emvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_emvp_mu += self.emvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc


                # if self.family_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                #     raw_material_losses_t += self.family_model.getVarByName(f'ROs_t[{s},{t}]').Obj
        return [raw_material_losses_family_mu, raw_material_losses_family_mu, raw_material_losses_mvp_mu, raw_material_losses_emvp_mu]

    def create_raw_material_purchase_cost_mu(self):
        # Compute the value for 'Raw Material Purchase Cost [MU]'

        raw_material_purchase_family_mu = 0
        raw_material_purchase_detailed_mu = 0
        raw_material_purchase_mvp_mu = 0
        raw_material_purchase_emvp_mu = 0

        for s in self.S:
            for t in self.T:
                if self.family_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_family_mu += self.family_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.roc
                #raw_material_purchase_detailed_t += self.detailed_model.getVarByName(f'RSs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_mvp_mu += self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.roc

                # emvp
                if self.emvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_emvp_mu += self.emvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.roc

                # if self.family_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                #     raw_material_purchase_t += self.family_model.getVarByName(f'RSs_t[{s},{t}]').Obj

        return [raw_material_purchase_family_mu, raw_material_purchase_family_mu, raw_material_purchase_mvp_mu, raw_material_purchase_emvp_mu]

    def create_exports_income_mu(self):
        # Compute the value for 'Exports Income [MU]'

        exports_family_mu = 0
        exports_detailed_mu = 0
        exports_mvp_mu = 0
        exports_emvp_mu = 0

        for f in self.F:
            for t in self.T:
                exports_family_mu += self.family_model.getVarByName(f'Ef_t[{f},{t}]').X * self.data.re[f] * self.data.ls[f]

                # mvp
                if self.mvp_model.getVarByName(f'Ef_t[{f},{t}]') is not None:
                    exports_mvp_mu += self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X
        
        for p in self.MP:
            for t in self.T:
                exports_detailed_mu += self.detailed_model.getVarByName(f'EDp_t[{p},{t}]').X * self.data.re_p[p] * self.data.el[p]

                if self.emvp_model.getVarByName(f'EDp_t[{p},{t}]') is not None:
                    exports_emvp_mu += self.emvp_model.getVarByName(f'EDp_t[{p},{t}]').X

                # if self.family_model.getVarByName(f'Ef_t[{f},{t}]') is not None:
                #     exports_t += self.family_model.getVarByName(f'Ef_t[{f},{t}]').Obj

        return [exports_family_mu, exports_detailed_mu, exports_mvp_mu, exports_emvp_mu]

    def create_cost_shipped_dc_mu(self):
        # Compute the value for 'Cost for shipped to DC [MU]'

        product_shipped_family_mu = 0
        product_shipped_detailed_mu = 0
        product_shipped_mvp_mu = 0
        product_shipped_emvp_mu = 0

        for i in self.FT:
            for l in self.L:
                for t in self.T:
                    product_shipped_family_mu += self.family_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

        
                    product_shipped_detailed_mu += self.detailed_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

                    # mvp
                    if self.mvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_mvp_mu += self.mvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

                    # emvp
                    if self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_emvp_mu += self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

                    # if self.family_model.getVarByName(f'DVf_l_t[{f},{l},{t}]') is not None:
                    #     product_shipped_t += self.family_model.getVarByName(f'DVf_l_t[{f},{l},{t}]').Obj

        return [product_shipped_family_mu, product_shipped_detailed_mu, product_shipped_mvp_mu, product_shipped_emvp_mu]

    def create_setups_cost_mu(self):
        # Compute the value for 'Setups Cost [MU]'
        setup_costs_family_mu = 0
        setup_costs_detailed_mu = 0
        setup_costs_mvp_mu = 0
        setup_costs_emvp_mu = 0

        for m in self.MP:
            for t in self.T:
                setup_costs_family_mu += self.family_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.sco
                # setup_costs_detailed_mu += self.detailed_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.su[m]

                if self.mvp_model.getVarByName(f'Ym_t[{m},{t}]') is not None:
                    setup_costs_mvp_mu += self.mvp_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.sco

                if self.emvp_model.getVarByName(f'Ym_t[{m},{t}]') is not None:
                    setup_costs_emvp_mu += self.emvp_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.sco

        setup_costs_detailed_mu = setup_costs_family_mu
        return [setup_costs_family_mu, setup_costs_detailed_mu, setup_costs_mvp_mu, setup_costs_emvp_mu]

    def create_expected_net_benefits_mu(self):
        # Compute the value for 'Expected Net Benefits [MU]'
        # Replace the following line with your computation
        expected_net_benefits_family_mu = self.family_model.objVal
        expected_net_benefits_detailed_mu = self.detailed_model.objVal
        expected_net_benefits_mvp_mu = self.mvp_model.objVal
        expected_net_benefits_emvp_mu = self.emvp_model.objVal

        return [expected_net_benefits_family_mu, expected_net_benefits_detailed_mu, expected_net_benefits_mvp_mu, expected_net_benefits_emvp_mu]

    def create_trucks_required(self):
        # Compute the value for 'Required trucks'

        trucks_required_family = 0
        trucks_required_detailed = 0
        trucks_required_mvp = 0
        trucks_required_emvp = 0

        for i in self.FT:
            for l in self.L:
                for t in self.T:
                    trucks_required_family += self.family_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X
                    trucks_required_detailed += self.detailed_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X
                    trucks_required_mvp += self.mvp_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X
                    trucks_required_emvp += self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X

        return [trucks_required_family, trucks_required_detailed, trucks_required_mvp, trucks_required_emvp]

    
    def calculate_deviation(self, value, comparison):

        if (comparison == int(0)) or comparison == float(0) : #or isinstance(comparison, list):
            return 'N/A'
        return f'{round((value - comparison) / comparison * 100, 1)}%'

    def PrintResults(self, table6, table8):
        pd.options.display.float_format = '{:,.2f}'.format
        print('=========================================')
        print('Results:')
        print('Objective value FAM: %g' % self.family_model.objVal)
        print('Objective value DPM: %g' % self.detailed_model.objVal)
        print('Objective value EMVP: %g' % self.emvp_model.objVal)
        print('table 6:')
        print(table6)

        print('table 8:')
        print(table8)

    

    def ComputeResultsOfTable6(self):

        variables = {
            'sales_t': self.sales_t,
            'lost_sales_t': self.lost_sales_t,
            'distressed_sales_t': self.distressed_sales_t,
            'raw_material_losses_t': self.raw_material_losses_t,
            'raw_material_purchase_t': self.raw_material_purchase_t,
            'exports_t': self.exports_t,
            'production_t': self.production_t,
            'product_shipped_t': self.product_shipped_t,
            'trucks_required': self.trucks_required,
            'sales_income_mu': self.sales_income_mu,
            'distressed_sales_mu': self.distressed_sales_mu,
            'raw_material_losses_cost_mu': self.raw_material_losses_cost_mu,
            'raw_material_purchase_cost_mu': self.raw_material_purchase_cost_mu,
            'exports_income_mu': self.exports_income_mu,
            'cost_shipped_dc_mu': self.cost_shipped_dc_mu,
            'setups_cost_mu': self.setups_cost_mu,
            'expected_net_benefits_mu': self.expected_net_benefits_mu,
        }

        metric_names = [
            'Sales [t]', 'Lost Sales [t]', 'Distressed Sales of Products [t]',
            'Raw Material Losses [t]', 'Raw Material Purchase [t]', 'Exports [t]',
            'Production [t]', 'Product shipped to DC [t]', 'Sales Income [MU]',
            'Distressed Sales of Products [MU]', 'Raw Material Losses Cost [MU]',
            'Raw Material Purchase Cost [MU]', 'Exports Income [MU]',
            'Cost for shipped to DC [MU]', 'Setups Cost [MU]',
            'Expected Net Benefits [MU]'
        ]

        data = []

        for metric_name in variables.keys():
                spFAM_value = variables[metric_name][0]
                spDPM_value = variables[metric_name][1]
                mvp_value = variables[metric_name][2]
                emvp_value = variables[metric_name][3]
                deviation = self.calculate_deviation(spDPM_value, emvp_value)
                data.append([metric_name, spFAM_value, spDPM_value, mvp_value, emvp_value, deviation])            

        
        df = pd.DataFrame(data, columns=['Metric', 'SP-FAM', 'SP-DPM', 'MVP', 'EMVP', '% deviation SP-DPM from EMVP'])

        # creata summation row for each costs and over all income metrics
        # costs 
        cost_rows = ['raw_material_losses_cost_mu', 'raw_material_purchase_cost_mu', 'cost_shipped_dc_mu', 'setups_cost_mu']
        income_rows = ['sales_income_mu', 'distressed_sales_mu', 'exports_income_mu']

        # Calculate the sums for costs and income
        costs_sum = df[df['Metric'].isin(cost_rows)].sum(numeric_only=True)
        income_sum = df[df['Metric'].isin(income_rows)].sum(numeric_only=True)
        difference_sum = income_sum - costs_sum

        total_costs_row = pd.DataFrame({
            'Metric': ['Total Costs'],
            'SP-FAM': [costs_sum['SP-FAM']],
            'SP-DPM': [costs_sum['SP-DPM']],
            'MVP': [costs_sum['MVP']],
            'EMVP': [costs_sum['EMVP']],
            '% deviation SP-DPM from EMVP': ['N/A']
        })

        total_income_row = pd.DataFrame({
            'Metric': ['Total Income'],
            'SP-FAM': [income_sum['SP-FAM']],
            'SP-DPM': [income_sum['SP-DPM']],
            'MVP': [income_sum['MVP']],
            'EMVP': [income_sum['EMVP']],
            '% deviation SP-DPM from EMVP': ['N/A']
        })

        difference_row = pd.DataFrame({
            'Metric': ['Difference (Income - Costs)'],
            'SP-FAM': [difference_sum['SP-FAM']],
            'SP-DPM': [difference_sum['SP-DPM']],
            'MVP': [difference_sum['MVP']],
            'EMVP': [difference_sum['EMVP']],
            '% deviation SP-DPM from EMVP': ['N/A']
        })

        # Concatenate the original DataFrame with the new rows
        df = pd.concat([df, total_costs_row, total_income_row, difference_row], ignore_index=True)


        return df

    def ComputeResultsOfTable8(self):    
        data = {'SP':  [self.sales_t, 
                        self.lost_sales_t,
                        self.distressed_sales_t,
                        self.raw_material_losses_t,
                        self.raw_material_purchase_t,
                        self.exports_t,
                        self.production_t,
                        self.product_shipped_t,
                        self.sales_income_mu,
                        self.distressed_sales_mu,
                        self.raw_material_losses_cost_mu,
                        self.raw_material_purchase_cost_mu,
                        self.exports_income_mu,
                        self.cost_shipped_dc_mu,
                        self.setups_cost_mu,
                        self.expected_net_benefits_mu]}
                        
        listOfResults = pd.DataFrame()
        listOfResults['SP'] = data['SP']

        data = {
            'SP-paper': self.paper_values_table8()['SP'],
            'EMVP-paper': self.paper_values_table8()['EMVP'],
        }

        df = pd.DataFrame(data, index = self.paper_values_table8().index)
        return df


    def Evaluate_results(self):
        pd.options.display.float_format = '{:.2f}'.format
        table6 = self.ComputeResultsOfTable6()
        table8 = self.ComputeResultsOfTable8()
        self.PrintResults(table6, table8)
        pass

    def Calculate_ss(self, data:Parameters, gp_model_detailed, logger):
        ''' Calculate the value of the objective function of the detailed planning model
            --> stochastic solution'''

        ss = gp_model_detailed.ObjVal

        logger.info(f'SS: {ss}')

        return ss, logger

    def Calculate_vss(self, ss, emvp, logger):
        ''' Calculate the value of stochastic solution
            --> VSS = SS - EMVP'''

        vss = ss - emvp

        logger.info(f'vss: {vss}')

        return vss, logger
    

    def create_result_visualization(self, model1, model2, data_path):
        # visualize milk input and family output
        # self.graph_milk_input_output(model1, model2, data_path)
        # self.plot_sales_perspective(data_path)
        pass

 
    def graph_milk_input_output(self, model1, model2, data_path):
        # Import the results
        data_path = 'results/plot_table_ts.csv'
        df = pd.read_csv(data_path) 

        # Create subplots for each scenario
        # Convert relevant columns to float
        columns_to_convert = ['RM_t', 'SAs_f_l_t', 'SOs_f_l_t', 'OSs_f_l_t', 'RCs', 'RSs_t', 'ROs_t', 'RIs_t']
        df[columns_to_convert] = df[columns_to_convert].astype(float)

        # Get unique scenarios
        scenarios = df['s'].unique()

        for scenario in scenarios:
            scenario_data = df[df['s'] == scenario].groupby('t').sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))

            x = np.arange(len(scenario_data['t'].unique()))
            
            width = 0.2  # Width of the bars

            # Plot RM_t
            data_RMt = df[df['s'] == scenario][['t', 'RM_t']].drop_duplicates().set_index('t').sort_index()['RM_t']
            print(data_RMt)
            ax.bar(x - width, data_RMt, width, label='RM_t', color='blue')

            # Plot SA, SO, OS stacked
            ax.bar(x, scenario_data.groupby('t')['SAs_f_l_t'].sum(), width, label='SAs_f_l_t', color='orange', bottom=scenario_data.groupby('t')['SOs_f_l_t'].sum() + scenario_data.groupby('t')['OSs_f_l_t'].sum())
            ax.bar(x, scenario_data.groupby('t')['SOs_f_l_t'].sum(), width, label='SOs_f_l_t', color='green', bottom=scenario_data.groupby('t')['OSs_f_l_t'].sum())
            ax.bar(x, scenario_data.groupby('t')['OSs_f_l_t'].sum(), width, label='OSs_f_l_t', color='red')

            # Plot RS, RO, RI stacked
            ax.bar(x + width, scenario_data.groupby('t')['RSs_t'].sum(), width, label='RSs_t', color='purple', bottom=scenario_data.groupby('t')['ROs_t'].sum() + scenario_data.groupby('t')['RIs_t'].sum())
            ax.bar(x + width, scenario_data.groupby('t')['ROs_t'].sum(), width, label='ROs_t', color='brown', bottom=scenario_data.groupby('t')['RIs_t'].sum())
            ax.bar(x + width, scenario_data.groupby('t')['RIs_t'].sum(), width, label='RIs_t', color='gray')

            ax.set_title(f'Scenario {scenario}')
            ax.set_xlabel('Time t')
            ax.set_ylabel('Values')
            ax.set_xticks(x)
            ax.set_xticklabels(scenario_data['t'].unique())
            ax.grid(True)
            ax.legend(loc='upper left', bbox_to_anchor=(1,1))

            plt.tight_layout()
            plt.savefig(f'figures/plot_scenario_{scenario}.png')
            # plt.show()

    def plot_sales_perspective(self, data_path):
        # Import the results
        data_path = 'results/plot_table_ts.csv'
        df = pd.read_csv(data_path)

        columns_to_convert = ['RM_t', 'SAs_f_l_t', 'SOs_f_l_t', 'OSs_f_l_t', 'RCs', 'RSs_t', 'ROs_t', 'RIs_t']
        df[columns_to_convert] = df[columns_to_convert].astype(float)

        # Get unique scenarios
        scenarios = df['s'].unique()

        for scenario in scenarios:
            scenario_data = df[df['s'] == scenario].groupby('t').sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))

            x = np.arange(len(scenario_data['t']))
            
            width = 0.4  # Width of the bars

            # Plot sales perspective with SA, SO, OS stacked
            ax.bar(x, scenario_data['SAs_f_l_t'], width, label='SAs_f_l_t', color='orange', bottom=scenario_data['SOs_f_l_t'] + scenario_data['OSs_f_l_t'])
            ax.bar(x, scenario_data['SOs_f_l_t'], width, label='SOs_f_l_t', color='green', bottom=scenario_data['OSs_f_l_t'])
            ax.bar(x, scenario_data['OSs_f_l_t'], width, label='OSs_f_l_t', color='red')

            ax.set_title(f'Sales Perspective - Scenario {scenario}')
            ax.set_xlabel('Time t')
            ax.set_ylabel('Sales Quantities')
            ax.set_xticks(x)
            ax.set_xticklabels(scenario_data['t'])
            ax.grid(True)
            ax.legend(loc='upper left', bbox_to_anchor=(1,1))

            plt.tight_layout()
            plt.savefig(f'figures/plot_scenario_{scenario}-sales.png')

    # evaluate cost distribution
    def evaluate_cost_distribution(self, model1, model2):
        for model in [model1, model2]:
            F = self.F
            L = self.L
            T = self.T
            S = self.S
            MP = self.MP
            
            TR_var = model.getVarByName('TRi_l_t')
            Y_var = model.getVarByName('Ym_t')
            RS_var = model.getVarByName('RSs_t')
            RO_var = model.getVarByName('ROs_t')
            E_var = model.getVarByName('Ef_t')
            dp_var = model.getVarByName('dp_s_f_l_t')
            SO_var = model.getVarByName('SOs_f_l_t')
            OS_var = model.getVarByName('OSs_f_l_t')



            print("Optimaler erwarteter Nettoertrag (ENB):", model.objVal)
            print("Transportkosten (TR):")
            for i in range(len(F)):
                for l in range(len(L)):
                    for t in range(len(T)):
                        print(f"F: {F[i]}, L: {L[l]}, T: {T[t]}, TR: {TR_var[i, l, t].X}")
            
            print("Setup-Kosten (Y):")
            for m in range(len(MP)):
                for t in range(len(T)):
                    print(f"MP: {MP[m]}, T: {T[t]}, Y: {Y_var[m, t].X}")
            
            print("Rohmilchkosten bei Unterbestand (RS):")
            for s in range(len(S)):
                for t in range(len(T)):
                    print(f"S: {S[s]}, T: {T[t]}, RS: {RS_var[s, t].X}")
            
            print("Rohmilchkosten bei Überbestand (RO):")
            for s in range(len(S)):
                for t in range(len(T)):
                    print(f"S: {S[s]}, T: {T[t]}, RO: {RO_var[s, t].X}")
            
            print("Exporteinnahmen (E):")
            for f in range(len(F)):
                for t in range(len(T)):
                    print(f"F: {F[f]}, T: {T[t]}, E: {E_var[f, t].x}")
            
            print("Nachfrage (dp):")
            for s in range(len(S)):
                for f in range(len(F)):
                    for l in range(len(L)):
                        for t in range(len(T)):
                            print(f"S: {S[s]}, F: {F[f]}, L: {L[l]}, T: {T[t]}, dp: {dp_var[s, f, l, t].x}")
            
            print("Überbestand (SO):")
            for s in range(len(S)):
                for f in range(len(F)):
                    for l in range(len(L)):
                        for t in range(len(T)):
                            print(f"S: {S[s]}, F: {F[f]}, L: {L[l]}, T: {T[t]}, SO: {SO_var[s, f, l, t].x}")
            
            print("Verkauf von Überbestand (OS):")
            for s in range(len(S)):
                for l in range(len(L)):
                    for f in range(len(F)):
                        for t in range(len(T)):
                            print(f"S: {S[s]}, L: {L[l]}, F: {F[f]}, T: {T[t]}, OS: {OS_var[s, l, f, t].x}")
