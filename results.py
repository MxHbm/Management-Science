import pandas as pd
from parameters import Parameters, S_star
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import gurobipy as gp
''' results.py '''

class Results:
    def __init__(self, model1, model2, emvpModel, mvpModel, data:Parameters, data_s_star:S_star):
        self.family_model = model1
        self.detailed_model = model2
        self.emvp_model = emvpModel
        self.mvp_model = mvpModel
        self.data = data
        self.data_s_star = data_s_star

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

        self.evaluate_cost_distribution()
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

                            sales_family_t += (dp - so) * self.data.rho[s]

                            # mvp
                            if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                                so_mvp = self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X

                                dp_mvp = self.data_s_star.dp[s][f][l][t]    
                                sales_mvp_t += (dp_mvp - so_mvp) * self.data_s_star.rho[s]
        
        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                            

                            sod = self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                            dpd = self.data.dpd[s][p][l][t]

                            sales_detailed_t += (dpd - sod) * self.data.rho[s]


                            if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                                sod_emvp = self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                                dpd_emvp = self.data_s_star.dpd[s][p][l][t]
                                rho_emvp = self.data_s_star.rho[s]

                                sales_emvp_t += (dpd_emvp- sod_emvp) * rho_emvp

                            

                        # if self.family_model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]') is not None:
                        #     sales_t += self.family_model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]').X

        # print(f'Sales Family: {sales_family_t} \t\t Sales Detailed: {sales_detailed_t} \t\t Sales MVP: {sales_mvp_t} \t\t Sales EMVP: {sales_emvp_t}')

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
                        lost_sales_t_family += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data.rho[s]


                        if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                            lost_sales_t_mvp += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data_s_star.rho[s]
                            
        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                        lost_sales_t_detailed += self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X * self.data.rho[s]

                        # emvp
                        if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                            lost_sales_t_emvp += self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X * self.data_s_star.rho[s]



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
                        distressed_sales_family += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rho[s]


                        if self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]') is not None:
                            distressed_sales_mvp += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data_s_star.rho[s]

        for s in self.S:
            for p in self.P:
                for l in self.L:
                    for t in self.T:
                        distressed_sales_detailed += self.detailed_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rho[s]

                        # emvp
                        if self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]') is not None:
                            distressed_sales_emvp += self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data_s_star.rho[s]
                        
                        

        return [distressed_sales_family, distressed_sales_detailed, distressed_sales_mvp, distressed_sales_emvp]

    def create_raw_material_losses_t(self):
        # Compute the value for 'Raw Material Losses [t]'

        raw_material_losses_family_t = 0
        raw_material_losses_detailed_t = 0
        raw_material_losses_mvp_t = 0
        raw_material_losses_emvp_t = 0

        for s in self.S:
            for t in self.T:
                raw_material_losses_family_t += self.family_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.rho[s]
                # raw_material_losses_detailed_t += self.detailed_model.getVarByName(f'ROs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_mvp_t += self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data_s_star.rho[s]

                # emvp
                if self.emvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_emvp_t += self.emvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data_s_star.rho[s]

        return [raw_material_losses_family_t, raw_material_losses_detailed_t, raw_material_losses_mvp_t, raw_material_losses_emvp_t]

    def create_raw_material_purchase_t(self):
        # Compute the value for 'Raw Material Purchase [t]'

        raw_material_purchase_family_t = 0
        raw_material_purchase_detailed_t = 0
        raw_material_purchase_mvp_t = 0
        raw_material_purchase_emvp_t = 0

        for s in self.S:
            for t in self.T:
                if self.family_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_family_t += self.family_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rho[s]
                #raw_material_purchase_detailed_t += self.detailed_model.getVarByName(f'RSs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_mvp_t += self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X  * self.data_s_star.rho[s]
                
                # emvp
                if self.emvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_emvp_t += self.emvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data_s_star.rho[s]

        # raw_material_purchase_detailed_t = raw_material_purchase_family_t
        # raw_material_purchase_emvp_t = raw_material_purchase_mvp_t

        return [raw_material_purchase_family_t, raw_material_purchase_detailed_t, raw_material_purchase_mvp_t, raw_material_purchase_emvp_t]

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

        # production_detailed_t = production_family_t
        # production_emvp_t = production_mvp_t
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

        # product_shipped_detailed_t = product_shipped_family_t
        # product_shipped_emvp_t = product_shipped_mvp_t
        return [product_shipped_family_t, product_shipped_detailed_t, product_shipped_mvp_t, product_shipped_emvp_t]

    def create_sales_income_mu(self):
        # Compute the value for 'Sales Income [MU]'

        sales_income_family_mu = 0
        sales_income_detailed_mu = 0
        sales_income_mvp_mu = 0
        sales_income_emvp_mu = 0

        sales_income_detailed_mu_negative = 0
        sales_income_emvp_mu_negative = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                            so = self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            dp = self.data.dp[s][f][l][t]

                            sales_income_family_mu += (dp - so) * self.data.r[f] * self.data.rho[s]

                            if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                                so_mvp = self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                                dp_mvp = self.data_s_star.dp[s][f][l][t]

                                sales_income_mvp_mu += (dp_mvp - so_mvp) * self.data.r[f]  * self.data_s_star.rho[s]

        for s in self.S:
            for p in self.MP:
                sales_income_detailed_mu_product = 0
                sales_income_emvp_mu_product = 0
                for l in self.L:
                    for t in self.T:
                            
                            sod = self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                            dpd = self.data.dpd[s][p][l][t]

                            sales = (dpd - sod) * self.data.r_p[p] * self.data.rho[s]

                            sales_income_detailed_mu_product += sales

                            if sales < 0:
                                # print(f'Detail: s:{s}, p:{p}, l:{l}, t:{t} - Sales: {sales} \t\t SOD: {sod} \t\t DPD: {dpd}')
                                sales_income_detailed_mu_negative += sales

                            # emvp
                            if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                                sod_emvp = self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X
                                dpd_emvp = self.data_s_star.dpd[s][p][l][t]

                                sales_emvp = (dpd_emvp - sod_emvp)  * self.data.r_p[p]  * self.data_s_star.rho[s]

                                sales_income_emvp_mu_product += sales_emvp

                                if sales_emvp < 0:
                                    # print(f'EMVP: s:{s}, p:{p}, l:{l}, t:{t} - Sales: {sales_emvp} \t\t SOD: {sod_emvp} \t\t DPD: {dpd_emvp}')
                                    sales_income_emvp_mu_negative += sales_emvp

                # print(f's:{s}, p:{p} - Sales Income Family: {sales_income_family_mu} \t\t Sales Income Detailed: {sales_income_detailed_mu} \t\t Sales Income MVP: {sales_income_mvp_mu} \t\t Sales Income EMVP: {sales_income_emvp_mu}')
                sales_income_detailed_mu += sales_income_detailed_mu_product
                sales_income_emvp_mu += sales_income_emvp_mu_product

        # print(f'Sales Income Family: {sales_income_family_mu} \t\t Sales Income Detailed: {sales_income_detailed_mu} \t\t Sales Income MVP: {sales_income_mvp_mu} \t\t Sales Income EMVP: {sales_income_emvp_mu}')
        # print(f'Sales Income Detailed Negative: {sales_income_detailed_mu_negative} \t\t Sales Income EMVP Negative: {sales_income_emvp_mu_negative}')
        # print(f'Sales Income Detailed Positive: {sales_income_detailed_mu - sales_income_detailed_mu_negative} \t\t Sales Income EMVP Positive: {sales_income_emvp_mu - sales_income_emvp_mu_negative}')
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
                        distressed_sales_family_mu += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f] * self.data.rho[s]

                        # mvp
                        if self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]') is not None:
                            distressed_sales_mvp_mu += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]  * self.data_s_star.rho[s]
        for s in self.S:
            for p in self.MP:
                for l in self.L:
                    for t in self.T:
                        # OSD
                        distressed_sales_detailed_mu += self.detailed_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p] * self.data.rho[s]

                        # emvp
                        if self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]') is not None:
                            distressed_sales_emvp_mu += self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p] * self.data_s_star.rho[s]
                        
                        

        return [distressed_sales_family_mu, distressed_sales_detailed_mu, distressed_sales_mvp_mu, distressed_sales_emvp_mu]


    def create_raw_material_losses_cost_mu(self):
        # Compute the value for 'Raw Material Losses Cost [MU]'

        raw_material_losses_family_mu = 0
        raw_material_losses_detailed_mu = 0
        raw_material_losses_mvp_mu = 0
        raw_material_losses_emvp_mu = 0

        for s in self.S:
            for t in self.T:
                raw_material_losses_family_mu += self.family_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc * self.data.rho[s]
                # raw_material_losses_detailed_t += self.detailed_model.getVarByName(f'ROs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_mvp_mu += self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc * self.data_s_star.rho[s]

                # emvp
                if self.emvp_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                    raw_material_losses_emvp_mu += self.emvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc * self.data_s_star.rho[s]

        # raw_material_losses_detailed_mu = raw_material_losses_family_mu
        return [raw_material_losses_family_mu, raw_material_losses_detailed_mu, raw_material_losses_mvp_mu, raw_material_losses_emvp_mu]

    def create_raw_material_purchase_cost_mu(self):
        # Compute the value for 'Raw Material Purchase Cost [MU]'

        raw_material_purchase_family_mu = 0
        raw_material_purchase_detailed_mu = 0
        raw_material_purchase_mvp_mu = 0
        raw_material_purchase_emvp_mu = 0

        for s in self.S:
            for t in self.T:
                if self.family_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_family_mu += self.family_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rsc * self.data.rho[s]
                #raw_material_purchase_detailed_t += self.detailed_model.getVarByName(f'RSs_t[{s},{t}]').X

                # mvp
                if self.mvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_mvp_mu += self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rsc * self.data_s_star.rho[s]

                # emvp
                if self.emvp_model.getVarByName(f'RSs_t[{s},{t}]') is not None:
                    raw_material_purchase_emvp_mu += self.emvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rsc * self.data_s_star.rho[s]

        # raw_material_purchase_detailed_mu = raw_material_purchase_family_mu
        return [raw_material_purchase_family_mu, raw_material_purchase_detailed_mu, raw_material_purchase_mvp_mu, raw_material_purchase_emvp_mu]

    def create_exports_income_mu(self):
        # Compute the value for 'Exports Income [MU]'

        exports_family_mu = 0
        exports_detailed_mu = 0
        exports_mvp_mu = 0
        exports_emvp_mu = 0

        for f in self.F:
            for t in self.T:
                exports_family_mu += self.family_model.getVarByName(f'Ef_t[{f},{t}]').X * self.data.re[f] * self.data.el[f]

                # mvp
                if self.mvp_model.getVarByName(f'Ef_t[{f},{t}]') is not None:
                    exports_mvp_mu += self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X * self.data.re[f] * self.data.el[f]
        
        for p in self.MP:
            for t in self.T:
                exports_detailed_mu += self.detailed_model.getVarByName(f'EDp_t[{p},{t}]').X * self.data.re_p[p] * self.data.ls[p]

                if self.emvp_model.getVarByName(f'EDp_t[{p},{t}]') is not None:
                    exports_emvp_mu += self.emvp_model.getVarByName(f'EDp_t[{p},{t}]').X * self.data.re_p[p] * self.data.ls[p]

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
                    if self.mvp_model.getVarByName(f'TRi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_mvp_mu += self.mvp_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

                    # emvp
                    if self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]') is not None:
                        product_shipped_emvp_mu += self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

        return [product_shipped_family_mu, product_shipped_detailed_mu, product_shipped_mvp_mu, product_shipped_emvp_mu]

    def create_setups_cost_mu(self):
        # Compute the value for 'Setups Cost [MU]'
        setup_costs_family_mu = 0
        setup_costs_detailed_mu = 0
        setup_costs_mvp_mu = 0
        setup_costs_emvp_mu = 0

        for m in self.MP:
            for t in self.T:
                for k in range(self.data.dmax[0]):
                    setup_costs_family_mu += self.family_model.getVarByName(f'Ym_t[{m},{t},{k}]').X * self.data.sco
                    # setup_costs_detailed_mu += self.detailed_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.su[m]

                    if self.mvp_model.getVarByName(f'Ym_t[{m},{t},{k}]') is not None:
                        setup_costs_mvp_mu += self.mvp_model.getVarByName(f'Ym_t[{m},{t},{k}]').X * self.data.sco

                    if self.emvp_model.getVarByName(f'Ym_t[{m},{t},{k}]') is not None:
                        setup_costs_emvp_mu += self.emvp_model.getVarByName(f'Ym_t[{m},{t},{k}]').X * self.data.sco

        # setup_costs_detailed_mu = setup_costs_family_mu
        return [setup_costs_family_mu, setup_costs_detailed_mu, setup_costs_mvp_mu, setup_costs_emvp_mu]

    def create_expected_net_benefits_mu(self):
        # Compute the value for 'Expected Net Benefits [MU]'

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

    def PrintResults(self, table6, table8, objFunction):
        pd.options.display.float_format = '{:,.2f}'.format
        print('=========================================')
        print('Results:')
        print('Objective value FAM: %g' % self.family_model.objVal)
        print('Objective value DPM: %g' % self.detailed_model.objVal)
        print('Objective value MVP: %g' % self.mvp_model.objVal)
        print('Objective value EMVP: %g' % self.emvp_model.objVal)
        print('table 6:')
        print(table6)

        print('ObjectiveFunction:')
        print(objFunction)

        #print('table 8:')
        #print(table8)

    

    def ComputeResultsOfTable6(self):

        variables = {
            'sales_t': self.sales_t,
            'lost_sales_t': self.lost_sales_t,
            'distressed_sales_t': self.distressed_sales_t,
            'exports_t': self.exports_t,
            'raw_material_losses_t': self.raw_material_losses_t,
            'raw_material_purchase_t': self.raw_material_purchase_t,
            'production_t': self.production_t,
            'product_shipped_t': self.product_shipped_t,
            'trucks_required': self.trucks_required,
            'sales_income_mu': self.sales_income_mu,
            'distressed_sales_mu': self.distressed_sales_mu,
            'exports_income_mu': self.exports_income_mu,
            'raw_material_losses_cost_mu': self.raw_material_losses_cost_mu,
            'raw_material_purchase_cost_mu': self.raw_material_purchase_cost_mu,
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
            '% deviation SP-DPM from EMVP': [self.calculate_deviation(costs_sum['SP-DPM'], costs_sum['EMVP'])]
        })

        total_income_row = pd.DataFrame({
            'Metric': ['Total Income'],
            'SP-FAM': [income_sum['SP-FAM']],
            'SP-DPM': [income_sum['SP-DPM']],
            'MVP': [income_sum['MVP']],
            'EMVP': [income_sum['EMVP']],
            '% deviation SP-DPM from EMVP': [self.calculate_deviation(costs_sum['SP-DPM'], costs_sum['EMVP'])]
        })

        difference_row = pd.DataFrame({
            'Metric': ['Difference (Income - Costs)'],
            'SP-FAM': [difference_sum['SP-FAM']],
            'SP-DPM': [difference_sum['SP-DPM']],
            'MVP': [difference_sum['MVP']],
            'EMVP': [difference_sum['EMVP']],
            '% deviation SP-DPM from EMVP': [self.calculate_deviation(costs_sum['SP-DPM'], costs_sum['EMVP'])]
        })

        # Concatenate the original DataFrame with the new rows
        df = pd.concat([df, total_costs_row, total_income_row, difference_row], ignore_index=True)

        # aggregate SP-FAM and SP-DPM to SP_agg and MVP and EMVP to EMVP_agg
        df['SP_agg'] = df['SP-FAM'] + df['SP-DPM']
        df['EMVP_agg'] = df['MVP'] + df['EMVP']
        df['% deviation SP_agg from EMVP_agg'] = df.apply(lambda row: self.calculate_deviation(row['SP_agg'], row['EMVP_agg']), axis=1)

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
    
    def ComputeObjFunction(self):

        # Initialize total cost
        T_COST = 0
        cost1_fam, cost2_fam, cost3_fam = 0, 0, 0
        cost1_mvp, cost2_mvp, cost3_mvp = 0, 0, 0
        cost1_dpm = 0
        cost1_emvp = 0

        # First Summation
        for i in self.data.FT:
            for l in self.data.L:
                for t in self.data.T:
                    if self.family_model.getVarByName(f'TRi_l_t[{i},{l},{t}]') is not None:
                        cost = self.family_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]  
                        cost1_fam += cost

                    if self.mvp_model.getVarByName(f'TRi_l_t[{i},{l},{t}]') is not None:
                        cost = self.mvp_model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]  
                        cost1_mvp += cost

                    if self.detailed_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]') is not None:
                        cost1_dpm += self.detailed_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]

                    if self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]') is not None:
                        cost1_emvp += self.emvp_model.getVarByName(f'TRDi_l_t[{i},{l},{t}]').X * self.data.tc[l][i]


        # Second Summation
        for m in self.data.MP:
            for t in self.data.T:
                if self.family_model.getVarByName(f'Ym_t[{m},{t}]') is not None:
                    cost = self.family_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.sco
                    cost2_fam += cost

                if self.mvp_model.getVarByName(f'Ym_t[{m},{t}]') is not None:
                    cost = self.mvp_model.getVarByName(f'Ym_t[{m},{t}]').X * self.data.sco
                    cost2_mvp += cost

        # Third Summation
        for s in self.data.S:
            for t in self.data.T:
                # if self.family_model.getVarByName(f'ROs_t[{s},{t}]') is not None:
                cost = (self.family_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rsc
                        + self.family_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc)
                cost3_fam += cost * self.data.rho[s]

                if s in self.data_s_star.S:
                    cost = (self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X * self.data.rsc
                            + self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X * self.data.roc)
                    cost3_mvp += cost * self.data_s_star.rho[s]
        
        objValue_FAM = self.family_model.objVal
        objValue_DPM = self.detailed_model.objVal
        objValue_MVP = self.mvp_model.objVal
        objValue_EMVP = self.emvp_model.objVal
        

        # Initialize sums
        sum_part1_fam, sum_part2_fam = 0, 0
        sum_part1_dpm, sum_part2_dpm = 0, 0
        sum_part1_mvp, sum_part2_mvp = 0, 0
        sum_part1_emvp, sum_part2_emvp = 0, 0


        # Calculate first part of the equation
        for f in self.data.F:
            for t in self.data.T:
                sum_part1_fam += self.data.re[f] * self.data.el[f] * self.family_model.getVarByName(f'Ef_t[{f},{t}]').X
                sum_part1_mvp += self.data.re[f] * self.data.el[f] * self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X

        for p in self.P:
            for t in self.data.T:
                sum_part1_dpm += self.data.re_p[p] * self.data.ls[p] * self.detailed_model.getVarByName(f'EDp_t[{p},{t}]').X
                sum_part1_emvp += self.data.re_p[p] * self.data.ls[p] * self.emvp_model.getVarByName(f'EDp_t[{p},{t}]').X

        # Calculate second part of the equation
        for s in self.data.S:
            sum_s = 0

            for l in self.data.L:
                for f in self.data.F:
                    for t in self.data.T:
                        sum_s += (self.data.r[f] * (self.data.dp[s][f][l][t] - self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X )
                                  + self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f])
                        if self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]') is not None:
                            sum_part2_mvp += (self.data.r[f] * (self.data.dp[s][f][l][t] - self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X )
                                        + self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]) * self.data_s_star.rho[s]
                            
                        
            sum_part2_fam += self.data.rho[s] * sum_s
            # print(f'Detailed: s:{s} - sum_s: {sum_s} * rho: {self.data.rho[s]} = {self.data.rho[s] * sum_s}')
            # if s in self.data_s_star.S:
            #     sum_part2_mvp += self.data_s_star.rho[s] * sum_s_mvp
                # print(f'EMVP: s:{s} - sum_s: {sum_s_mvp} * rho: {self.data_s_star.rho[s]} = {self.data_s_star.rho[s] * sum_s_mvp}')

            sum_s_dpm = 0
            sum_s_emvp = 0
            for l in self.data.L:
                for p in self.data.P:
                    for t in self.data.T:
                        sum_s_dpm += (self.data.r_p[p] * (self.data.dpd[s][p][l][t] - self.detailed_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X )
                                     + self.detailed_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p])
                        
                        if self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]') is not None:
                            sum_s_emvp += (self.data.r_p[p] * (self.data.dpd[s][p][l][t] - self.emvp_model.getVarByName(f'SODs_p_l_t[{s},{p},{l},{t}]').X )
                                         + self.emvp_model.getVarByName(f'OSDs_p_l_t[{s},{p},{l},{t}]').X * self.data.rr_p[p])
            
            sum_part2_dpm += self.data.rho[s] * sum_s_dpm

            if s in self.data_s_star.S:
                sum_part2_emvp += self.data_s_star.rho[s] * sum_s_emvp

        # Calculate ENB
        benefit_fam = sum_part1_fam + sum_part2_fam
        t_cost_fam = (cost1_fam + cost2_fam + cost3_fam)
        enb_fam = benefit_fam - t_cost_fam

        benefit_dpm = sum_part1_dpm + sum_part2_dpm
        t_cost_dpm = (cost1_dpm)
        enb_dpm = benefit_dpm - t_cost_dpm

        benefit_mvp = sum_part1_mvp + sum_part2_mvp
        t_cost_mvp = (cost1_mvp + cost2_mvp + cost3_mvp)
        enb_mvp = benefit_mvp - t_cost_mvp

        benefit_emvp = sum_part1_emvp + sum_part2_emvp
        t_cost_emvp = (cost1_emvp)
        enb_emvp = benefit_emvp - t_cost_emvp

        pd.options.display.float_format = '{:,.2f}'.format


        # costs and benefits to df - new row for every cost and benefit:
        data = {'SP-FAM':   [cost1_fam, cost2_fam, cost3_fam,   sum_part1_fam, sum_part2_fam, cost1_fam + cost2_fam + cost3_fam, benefit_fam, enb_fam, objValue_FAM],
                'SP-DPM':   [cost1_dpm, 0,          0,          sum_part1_dpm, sum_part2_dpm, cost1_dpm, benefit_dpm, enb_dpm, objValue_DPM],
                'MVP':      [cost1_mvp, cost2_mvp, cost3_mvp,   sum_part1_mvp, sum_part2_mvp, cost1_mvp + cost2_mvp + cost3_mvp, benefit_mvp, enb_mvp, objValue_MVP],
                'EMVP':     [cost1_emvp, 0,         0,          sum_part1_emvp, sum_part2_emvp, cost1_emvp, benefit_emvp, enb_emvp, objValue_EMVP]}
        df = pd.DataFrame(data, index = ['Cost 1', 'Cost 2', 'Cost 3', 'Benefit1', 'Benefit2', 'TCOST', 'Benefit', 'ENB', 'ObjValue'])

        # aggregated df: SP ( FAM + DPM) and EMVP (MVP + EMVP):
        df['SP_agg'] = df['SP-FAM'] + df['SP-DPM']
        df['EMVP_agg'] = df['MVP'] + df['EMVP']
        # deviation for each row:
        df['% agg deviation'] = df.apply(lambda row: self.calculate_deviation(row['SP_agg'], row['EMVP_agg']), axis=1)

        print(df)
        


        return


    def Evaluate_results(self):
        pd.options.display.float_format = '{:.2f}'.format
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        table6 = self.ComputeResultsOfTable6()
        table8 = self.ComputeResultsOfTable8()
        objFunction = self.ComputeObjFunction()
        self.PrintResults(table6, table8, objFunction)
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

            ax.set_title(f'Scenario {scenario+1}')
            ax.set_xlabel('Time t')
            ax.set_ylabel('Values')
            ax.set_xticks(x)
            ax.set_xticklabels(scenario_data['t'].unique())
            ax.grid(True)
            ax.legend(loc='upper left', bbox_to_anchor=(1,1))

            plt.tight_layout()
            plt.savefig(f'figures/plot_scenario_{scenario+1}.png')
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

            ax.set_title(f'Sales Perspective - Scenario {scenario+1}')
            ax.set_xlabel('Time t')
            ax.set_ylabel('Sales Quantities')
            ax.set_xticks(x)
            ax.set_xticklabels(scenario_data['t'])
            ax.grid(True)
            ax.legend(loc='upper left', bbox_to_anchor=(1,1))

            plt.tight_layout()
            plt.savefig(f'figures/plot_scenario_{scenario+1}-sales.png')

    # evaluate cost distribution
    def evaluate_cost_distribution(self):
        # plot RSs_t, ROs_t over time per scenario

        s_min, s_mean, s_max = self.get_scenario_with_demand()
        

        # # self.plot1_ri_rs_ro()
        # self.plot1_ri_rs_ro(s_min=s_min, s_max=s_max, s_mean=s_mean)
        # self.plot2_ri_rs_ro()
        # self.plot3_sales_quantities()
        # self.plot4_sales_income()
        # self.plot6_distribution_center()
        # self.plot6_distribution_center_new(s_min=s_min, s_max=s_max, s_mean=s_mean)

        self.plot7_manufacturing_output(s_min=s_min, s_max=s_max, s_mean=s_mean)

        # # self.plot5_costs_and_sales_with_minmaxmean(s_min, s_max, s_mean)

    

        #self.plot_combined_sales_quantities_and_income()

    def get_scenario_with_demand(self):
        demand = pd.DataFrame()
        supply = pd.DataFrame()
        for s in self.data.S:
            demand_value = 0
            supply_value = self.data.SRA.reduced_scenarios[s][-1] 
            for f in self.data.F:
                demand_value += self.data.SRA.reduced_scenarios[s][f] / self.data.fy[f]
                print(f'scenarios: {s+1} - demand: {demand_value} - supply: {supply_value}')
                print(f'scenarios: {s+1} - supply: {self.data.SRA.reduced_scenarios[s][f]} - fy: {self.data.fy[f]}')
            demand[s] = [demand_value / supply_value]

        demand = demand.T.rename(columns={0: 'demand'})
        print(demand)
        min = demand['demand'].min()
        max = demand['demand'].max()
        mean = demand['demand'].mean()
        # mean = abs(demand['demand'] - mean ).argsort()[:1]
        mean = demand.iloc[(demand['demand'] - mean).abs().argsort()[:1]].index[0]
        
        min = np.where(demand['demand'] == min)[0][0]
        max = np.where(demand['demand'] == max)[0][0]
        # mean = np.where(demand['demand'] == mean)[0]

        print(min, max, mean)

        return min, mean, max
    
    def plot5_costs_and_sales_with_minmaxmean(self, s_min, s_max, s_mean):

        self.plot1_ri_rs_ro(s_min=s_min, s_max=s_max, s_mean=s_mean)
        self.plot6_distribution_center(s_min=s_min, s_max=s_max, s_mean=s_mean)
        pass


    def plot1_ri_rs_ro(self, s_min = None, s_max = None, s_mean = None):
        # Initialize dictionaries to hold the aggregated data for all scenarios
        min_mean_max = {'min': s_min, 'max': s_max, 'mean': s_mean}
        rs_mvp = {}
        ro_mvp = {}
        ri_mvp = {}
        dri_mvp = {}
        rm_mvp = {}

        for s in self.data.S:
            rs_data = {}
            ro_data = {}
            ri_data = {}
            dri_data = {}
            rm_data = {}

            fig = plt.figure(figsize=(12, 6))
            axes = fig.subplot_mosaic([['RS'], ['RO'], ['RI'], ['dri'], ['RM']], sharex=True)
            

            for t in self.data.T:
                rs_data[t] = self.family_model.getVarByName(f'RSs_t[{s},{t}]').X
                ro_data[t] = self.family_model.getVarByName(f'ROs_t[{s},{t}]').X
                ri_data[t] = self.family_model.getVarByName(f'RIs_t[{s},{t}]').X
                dri_data[t] = self.data.dri[s][t]
                rm_data[t] = self.family_model.getVarByName(f'RMt[{t}]').X
                #rc_data = self.family_model.getVarByName(f'RCs_t[{s},{t}]').X

                if s in self.data_s_star.S:
                    rs_mvp[t] = self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X
                    ro_mvp[t] = self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X
                    ri_mvp[t] = self.mvp_model.getVarByName(f'RIs_t[{s},{t}]').X
                    dri_mvp[t] = self.data.dri[s][t]
                    rm_mvp[t] = self.mvp_model.getVarByName(f'RMt[{t}]').X

            # Correct plotting by separating keys and values
            axes['RS'].plot(list(rs_data.keys()), list(rs_data.values()), label='RSs_t', color='green')
            axes['RO'].plot(list(ro_data.keys()), list(ro_data.values()), label='ROs_t', color='red')
            axes['RI'].plot(list(ri_data.keys()), list(ri_data.values()), label='RIs_t', color='blue')
            axes['dri'].plot(list(dri_data.keys()), list(dri_data.values()), label='dri_t', color='orange')
            axes['RM'].plot(list(rm_data.keys()), list(rm_data.values()), label='RM_t', color='purple')

            # For MVP data, ensure you're also separating keys and values
            axes['RS'].plot(list(rs_mvp.keys()), list(rs_mvp.values()), label='RSs_t_mvp', color='black', linestyle='dashed')
            axes['RO'].plot(list(ro_mvp.keys()), list(ro_mvp.values()), label='ROs_t_mvp', color='black', linestyle='dashed')
            axes['RI'].plot(list(ri_mvp.keys()), list(ri_mvp.values()), label='RIs_t_mvp', color='black', linestyle='dashed')
            axes['dri'].plot(list(dri_mvp.keys()), list(dri_mvp.values()), label='dri_t_mvp', color='black', linestyle='dashed')
            axes['RM'].plot(list(rm_mvp.keys()), list(rm_mvp.values()), label='RM_t_mvp', color='black', linestyle='dashed')

            if s in min_mean_max.values():
                value = [i for i in min_mean_max if min_mean_max[i] == s][0]
                demand_suffix = f' ({value} demand)'
            else:
                demand_suffix = ''
            axes['RI'].set_title(f'Raw Milk Inventory - Scenario {s+1}{demand_suffix}')
            axes['RS'].set_title(f'Raw Milk Supply - Scenario {s+1}{demand_suffix}')
            axes['RO'].set_title(f'Raw Milk Overstock - Scenario {s+1}{demand_suffix}')
            axes['dri'].set_title(f'Demand - Scenario {s+1}{demand_suffix}')
            axes['RM'].set_title(f'Raw Milk - Scenario {s+1}{demand_suffix}')

            axes['RI'].set_xlabel('Time t')
            axes['RI'].set_ylabel('Values')
            axes['RS'].set_ylabel('Values')
            axes['RO'].set_ylabel('Values')
            axes['dri'].set_ylabel('Values')
            axes['RM'].set_ylabel('Values')

            axes['RI'].legend()
            axes['RS'].legend()
            axes['RO'].legend()
            axes['dri'].legend()
            axes['RM'].legend()



            plt.tight_layout()

            if s in min_mean_max.values():
                value = [i for i in min_mean_max if min_mean_max[i] == s][0]
                plt.savefig(f'figures/cost_distribution_scenario_{s+1}_{value}.png')
            else:
                plt.savefig(f'figures/cost_distribution_scenario_{s+1}.png')

            plt.close(fig)  # Close the figure to avoid display issues in some environments

            # Plot combined RS, RO, RI, dri, RM
            # constraint: RIs,t = r0 + ∑dri_s − ∑RMt + ∑RSs_t − ∑ROst
            fig, ax = plt.subplots(figsize=(12, 12))

            width = 0.3
          

            for t in range(len(list(rs_data.keys())) ):

                rs = rs_data.get(t, 0)
                ro = ro_data.get(t, 0)
                rm = rm_data.get(t, 0)
                dri = dri_data.get(t, 0)
                if t > 0:
                    previous_value = ri_data.get(t-1, 0) #dri_data.get(t, 0) #+ ri_data.get(t-1, 0)
                else:
                    previous_value = self.data.r0 #+ dri_data.get(t, 0)
                


                # usage of raw milk inventory
                # inventory_usage = ri_data.get(t-1, 0) - ri_data.get(t, 0) if (t > 0) and ((ri_data.get(t-1, 0) - ri_data.get(t, 0)) > 0) else 0
                # ax.bar(t-width/2, -inventory_usage, bottom=ri_data.get(t, 0) if t>0 else ri_data.get(t,0), label='RIs_t - Raw Milk Consumption satisfied\n by Raw Milk Inventory' if t == 1 else "", color='blue', hatch='..', width=1.5*width, alpha=0.9)

                # dri_t bar plot
                ax.bar(t-width, dri, bottom=previous_value, label='dri_t - Raw Milk Input' if t == 1 else "", color='lime', width=width, alpha=0.9)
                dri_end = previous_value + dri

                # RSs_t bar plot
                ax.bar(t-width, rs, bottom=dri_end, label='RSs_t - purchase of Raw Milk to a third Supplier' if t == 1 else "", color='green', width=width, alpha = 0.9)
                rs_end = dri_end + rs
                
                # RM_t bar plot
                ax.bar(t, -rm, bottom=rs_end, label='RM_t - Raw Milk Consumption' if t == 1 else "", color='fuchsia', width=width, alpha=0.8)
                rm_end = rs_end - rm

                # ROs_t bar plot
                ax.bar(t, -ro, bottom=rm_end, label='ROs_t - Raw Milk Disposal' if t == 1 else "", color='red', width=width, alpha=0.9)
                ro_end = rm_end - ro
                # Update previous_value for next iteration
                previous_value = ro_end + dri_data.get(t, 0)

            ax.bar(-width, self.data.r0, label='r0 - Initial Raw Milk Inventory\n from previous planning horizon', color='black', width=width, alpha=0.9)

            # ax.plot(list(rs_data.keys()), list(rs_data.values()), label='RSs_t', color='green')     # barplot starting from r0 respectivly from previous height/value
            # ax.plot(list(ro_data.keys()), list(ro_data.values()), label='ROs_t', color='red')       # barplot starting from r0 + RSs_t
            ax.plot(list(ri_data.keys()), list(ri_data.values()), label='RIs_t - Raw Milk Inventory', color='blue')      # LINE PLOT
            ax.plot(list(dri_data.keys()), list(dri_data.values()), label='dri_t - Raw milk Daily Input', color='orange')  # line plot
            # ax.plot(list(rm_data.keys()), list(rm_data.values()), label='RM_t', color='purple')     # barplot starting from r0 - RM

            ax.plot(list(rs_mvp.keys()), list(rs_mvp.values()), label='RSs_t_mvp', color='black', linestyle='dashed')
            ax.plot(list(ro_mvp.keys()), list(ro_mvp.values()), label='ROs_t_mvp', color='black', linestyle='dashed')
            ax.plot(list(ri_mvp.keys()), list(ri_mvp.values()), label='RIs_t_mvp', color='black', linestyle='dashed')
            ax.plot(list(dri_mvp.keys()), list(dri_mvp.values()), label='dri_t_mvp', color='black', linestyle='dashed')
            ax.plot(list(rm_mvp.keys()), list(rm_mvp.values()), label='RM_t_mvp', color='black', linestyle='dashed')

            #ax.set_title(f'Raw milk supply consumption (Constraint (5)) - Scenario {s}{demand_suffix}')
            ax.set_xlabel('Time t in days')
            ax.set_ylabel('Quantity in tons')
            ax.legend(ncol=3, loc='best', bbox_to_anchor=(0.1, -0.2, 0.8, 0.5))

            

            # Save the combined figure
            if s in min_mean_max.values():
                value = [i for i in min_mean_max if min_mean_max[i] == s][0]
                demand_suffix = f' ({value} demand)'
                ax.set_title(f'Raw milk supply consumption (Constraint (5)) - Scenario {s+1}{demand_suffix}')
                plt.tight_layout()
                plt.savefig(f'figures/combined_plot_scenario_{s+1}_{value}.png')
            else:
                ax.set_title(f'Raw milk supply consumption (Constraint (5)) - Scenario {s+1}')
                plt.tight_layout()
                plt.savefig(f'figures/combined_plot_scenario_{s+1}.png')
            plt.close(fig)


    def plot2_ri_rs_ro(self):

        # Initialize dictionaries to hold the aggregated data for all scenarios
        rs_data_all = []
        ro_data_all = []
        ri_data_all = []
        rs_mvp_mean = []
        ro_mvp_mean = []
        ri_mvp_mean = []

        # Collect data for each scenario
        for s in self.data.S:
            rs_data = []
            ro_data = []
            ri_data = []

            for t in self.data.T:
                rs_data.append(self.family_model.getVarByName(f'RSs_t[{s},{t}]').X)
                ro_data.append(self.family_model.getVarByName(f'ROs_t[{s},{t}]').X)
                ri_data.append(self.family_model.getVarByName(f'RIs_t[{s},{t}]').X)

                # Calculate mean values for MVP model
                if s in self.data_s_star.S:
                    rs_mvp_mean.append([self.mvp_model.getVarByName(f'RSs_t[{s},{t}]').X ])
                    ro_mvp_mean.append([self.mvp_model.getVarByName(f'ROs_t[{s},{t}]').X ])
                    ri_mvp_mean.append([self.mvp_model.getVarByName(f'RIs_t[{s},{t}]').X ])

            rs_data_all.append(rs_data)
            ro_data_all.append(ro_data)
            ri_data_all.append(ri_data)

            

        # Plotting
        fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(18, 18))

        # RS plot
        for rs_data in rs_data_all:
            axes[0].plot(self.data.T, rs_data, color='grey', alpha=0.5)
        axes[0].plot(self.data.T, rs_mvp_mean, label='RSs_t_mvp_mean', color='black', linestyle='dashed')
        axes[0].set_title('Raw Milk Supply per Scenario vs. MVP')
        axes[0].set_ylabel('Values')
        axes[0].legend()

        # RO plot
        for ro_data in ro_data_all:
            axes[1].plot(self.data.T, ro_data, color='grey', alpha=0.5)
        axes[1].plot(self.data.T, ro_mvp_mean, label='ROs_t_mvp_mean', color='black', linestyle='dashed')
        axes[1].set_title('Raw Milk Overstock Quantity per Scenario vs. MVP')
        axes[1].set_ylabel('Values')
        axes[1].legend()

        # RI plot
        for ri_data in ri_data_all:
            axes[2].plot(self.data.T, ri_data, color='grey', alpha=0.5)
        axes[2].plot(self.data.T, ri_mvp_mean, label='RIs_t_mvp_mean', color='black', linestyle='dashed')
        axes[2].set_title('Raw Milk Inventory per Scenario vs. MVP')
        axes[2].set_xlabel('Time t')
        axes[2].set_ylabel('Values')
        axes[2].legend()

        plt.tight_layout()

        plt.savefig(f'figures/plot2_raw-milk_distribution_over-{s+1}-scenarios.png')
        plt.close(fig)  # Close the figure to avoid display issues in some environments

    def plot3_sales_quantities(self):

        # Initialize dictionaries to hold the aggregated data for all scenarios
        so_data_all = []
        os_data_all = []
        dp_data_all = []
        so_mvp_data = []
        os_mvp_data = []
        dp_mvp_data = []

        # Collect data for each scenario
        for s in self.data.S:
            so_data = []
            os_data = []
            dp_data = []


            for t in self.data.T:
                so, os, dp = 0, 0, 0
                so_mvp, os_mvp, dp_mvp = 0, 0, 0

                for f in self.data.F:
                    for l in self.data.L:
                        so += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                        os += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                        dp += self.data.dp[s][f][l][t]

                        # Calculate mean values for MVP model
                        if s in self.data_s_star.S:
                            so_mvp += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            os_mvp += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                            dp_mvp += self.data_s_star.dp[s][f][l][t]
                            
                
                so_data.append(so)
                os_data.append(os)
                dp_data.append(dp)

                if s in self.data_s_star.S:
                    so_mvp_data.append(so_mvp)
                    os_mvp_data.append(os_mvp)
                    dp_mvp_data.append(dp_mvp)

            so_data_all.append(so_data)
            os_data_all.append(os_data)
            dp_data_all.append(dp_data)

        exp = {}
        exp_mvp = {}
        for t in self.data.T:
            exp_f = {}
            exp_f[t] = 0

            exp_mvp_f = {}
            exp_mvp_f[t] = 0
            for f in self.data.F:
                # Ef_t
                exp_f[t] += self.family_model.getVarByName(f'Ef_t[{f},{t}]').X
                exp_mvp_f[t] += self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X

            exp[t] = exp_f[t]
            exp_mvp[t] = exp_mvp_f[t]

        # exp dict to list:
        exp = [exp[t] for t in self.data.T]        
        exp_mvp = [exp_mvp[t] for t in self.data.T]    

        # Plotting
        fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(18, 18))

        # Export plot
        axes[0].plot(self.data.T, exp, color='grey', alpha=0.5)
        axes[0].plot(self.data.T, exp_mvp, label='Ef_t_mvp_mean', color='black', linestyle='dashed')
        axes[0].set_title('Export Quantity vs. MVP')
        axes[0].set_ylabel('Quantity in tons')
        axes[0].legend()

        # SO plot
        for data in so_data_all:
            axes[1].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[1].plot(self.data.T, so_mvp_data, label='SOs_t_mvp_mean', color='black', linestyle='dashed')
        axes[1].set_title('Stock Out Quantity per Scenario vs. Mean Value Problem')
        axes[1].set_ylabel('Quantity in tons')
        axes[1].legend()

        # OS plot
        for data in os_data_all:
            axes[2].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[2].plot(self.data.T, os_mvp_data, label='OSs_f_l_t_mvp_mean', color='black', linestyle='dashed')
        axes[2].set_title('Over Stock Quantity per Scenario vs. Mean Value Problem')
        axes[2].set_xlabel('Time t')
        axes[2].set_ylabel('Quantity in tons')
        axes[2].legend()

        for data in dp_data_all:
            axes[3].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[3].plot(self.data.T, dp_mvp_data, label='dps_f_l_t_mvp_mean', color='black', linestyle='dashed')
        axes[3].set_title('Demand - Over Stock Quantity per Scenario vs. Mean Value Problem')
        axes[3].set_xlabel('Time t')
        axes[3].set_ylabel('Quantity in tons')
        axes[3].legend()

        plt.tight_layout()

        plt.savefig(f'figures/plot3_sales_quantities_distribution_over-{s+1}-scenarios.png')
        plt.close(fig)  # Close the figure to avoid display issues in some environments

    def plot4_sales_income(self):

        # Initialize dictionaries to hold the aggregated data for all scenarios
        so_data_all = []
        os_data_all = []
        dp_data_all = []
        so_mvp_data = []
        os_mvp_data = []
        dp_mvp_data = []

        # Collect data for each scenario
        for s in self.data.S:
            so_data = []
            os_data = []
            dp_data = []


            for t in self.data.T:
                so, os, dp = 0, 0, 0
                so_mvp, os_mvp, dp_mvp = 0, 0, 0

                for f in self.data.F:
                    for l in self.data.L:
                        so += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data.r[f]
                        os += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]
                        dp += self.data.dp[s][f][l][t]  * self.data.r[f]

                        # Calculate mean values for MVP model
                        if s in self.data_s_star.S:
                            so_mvp += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data.r[f]
                            os_mvp += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]
                            dp_mvp += self.data_s_star.dp[s][f][l][t] * self.data.r[f]
                            
                
                so_data.append(so)
                os_data.append(os)
                dp_data.append(dp)

                if s in self.data_s_star.S:
                    so_mvp_data.append(so_mvp)
                    os_mvp_data.append(os_mvp)
                    dp_mvp_data.append(dp_mvp)

            so_data_all.append(so_data)
            os_data_all.append(os_data)
            dp_data_all.append(dp_data)

        exp = {}
        exp_mvp = {}
        for t in self.data.T:
            exp_f = {}
            exp_f[t] = 0

            exp_mvp_f = {}
            exp_mvp_f[t] = 0
            for f in self.data.F:
                # Ef_t
                exp_f[t] += self.family_model.getVarByName(f'Ef_t[{f},{t}]').X * self.data.re[f] * self.data.ls[f]
                exp_mvp_f[t] += self.mvp_model.getVarByName(f'Ef_t[{f},{t}]').X * self.data.re[f] * self.data.ls[f]

            exp[t] = exp_f[t]
            exp_mvp[t] = exp_mvp_f[t]

        # exp dict to list:
        exp = [exp[t] for t in self.data.T]        
        exp_mvp = [exp_mvp[t] for t in self.data.T]    

        # Plotting
        fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(18, 18))

        # Export plot
        axes[0].plot(self.data.T, exp, color='grey', alpha=0.5)
        axes[0].plot(self.data.T, exp_mvp, label='Ef_t_mvp_mean', color='black', linestyle='dashed')
        axes[0].set_title('Export Value vs. MVP')
        axes[0].set_ylabel('Value in Monetary Units')
        axes[0].legend()

        # SO plot
        for data in so_data_all:
            axes[1].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[1].plot(self.data.T, so_mvp_data, label='SOs_t_mvp_mean', color='black', linestyle='dashed')
        axes[1].set_title('Stock Out Value per Scenario vs. Mean Value Problem')
        axes[1].set_ylabel('Value in Monetary Units')
        axes[1].legend()

        # OS plot
        for data in os_data_all:
            axes[2].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[2].plot(self.data.T, os_mvp_data, label='OSs_f_l_t_mvp_mean', color='black', linestyle='dashed')
        axes[2].set_title('Over Stock Value per Scenario vs. Mean Value Problem')
        axes[2].set_xlabel('Time t')
        axes[2].set_ylabel('Value in Monetary Units')
        axes[2].legend()

        for data in dp_data_all:
            axes[3].plot(self.data.T, data, color='grey', alpha=0.5)
        axes[3].plot(self.data.T, dp_mvp_data, label='dps_f_l_t_mvp_mean', color='black', linestyle='dashed')
        axes[3].set_title('Demand - Over Stock Value per Scenario vs. Mean Value Problem')
        axes[3].set_xlabel('Time t')
        axes[3].set_ylabel('Value in Monetary Unit')
        axes[3].legend()

        plt.tight_layout()

        plt.savefig(f'figures/plot4_sales_values_distribution_over-{s+1}-scenarios.png')
        plt.close(fig)  # Close the figure to avoid display issues in some environments

    def plot_combined_sales_quantities_and_income(self):
        # Initialize dictionaries to hold the aggregated data for all scenarios
        so_data_all_quantities = []
        os_data_all_quantities = []
        dp_data_all_quantities = []
        so_mvp_data_quantities = []
        os_mvp_data_quantities = []
        dp_mvp_data_quantities = []
        
        so_data_all_income = []
        os_data_all_income = []
        dp_data_all_income = []
        so_mvp_data_income = []
        os_mvp_data_income = []
        dp_mvp_data_income = []

        # Collect data for each scenario
        for s in self.data.S:
            so_data_quantities = []
            os_data_quantities = []
            dp_data_quantities = []
            
            so_data_income = []
            os_data_income = []
            dp_data_income = []

            for t in self.data.T:
                so_quantities, os_quantities, dp_quantities = 0, 0, 0
                so_mvp_quantities, os_mvp_quantities, dp_mvp_quantities = 0, 0, 0
                
                so_income, os_income, dp_income = 0, 0, 0
                so_mvp_income, os_mvp_income, dp_mvp_income = 0, 0, 0

                for f in self.data.F:
                    for l in self.data.L:
                        so_quantities += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                        os_quantities += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                        dp_quantities += self.data.dp[s][f][l][t]

                        so_income += self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data.r[f]
                        os_income += self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]
                        dp_income += self.data.dp[s][f][l][t] * self.data.r[f]

                        if s in self.data_s_star.S:
                            so_mvp_quantities += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            os_mvp_quantities += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                            dp_mvp_quantities += self.data_s_star.dp[s][f][l][t]

                            so_mvp_income += self.mvp_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X * self.data.r[f]
                            os_mvp_income += self.mvp_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X * self.data.rr[f]
                            dp_mvp_income += self.data_s_star.dp[s][f][l][t] * self.data.r[f]

                so_data_quantities.append(so_quantities)
                os_data_quantities.append(os_quantities)
                dp_data_quantities.append(dp_quantities)

                so_data_income.append(so_income)
                os_data_income.append(os_income)
                dp_data_income.append(dp_income)

                if s in self.data_s_star.S:
                    so_mvp_data_quantities.append(so_mvp_quantities)
                    os_mvp_data_quantities.append(os_mvp_quantities)
                    dp_mvp_data_quantities.append(dp_mvp_quantities)
                    
                    so_mvp_data_income.append(so_mvp_income)
                    os_mvp_data_income.append(os_mvp_income)
                    dp_mvp_data_income.append(dp_mvp_income)

            so_data_all_quantities.append(so_data_quantities)
            os_data_all_quantities.append(os_data_quantities)
            dp_data_all_quantities.append(dp_data_quantities)
            
            so_data_all_income.append(so_data_income)
            os_data_all_income.append(os_data_income)
            dp_data_all_income.append(dp_data_income)

        # Plotting combined data
        fig, ax1 = plt.subplots(figsize=(18, 9))

        color = 'tab:blue'
        ax1.set_xlabel('Time t')
        ax1.set_ylabel('Quantities', color=color)
        
        for data in so_data_all_quantities:
            ax1.plot(self.data.T, data, color='blue', alpha=0.3)
        for data in os_data_all_quantities:
            ax1.plot(self.data.T, data, color='green', alpha=0.3)
        for data in dp_data_all_quantities:
            ax1.plot(self.data.T, data, color='red', alpha=0.3)
            
        ax1.plot(self.data.T, so_mvp_data_quantities, label='SO quantities MVP', color='blue', linestyle='dashed')
        ax1.plot(self.data.T, os_mvp_data_quantities, label='OS quantities MVP', color='green', linestyle='dashed')
        ax1.plot(self.data.T, dp_mvp_data_quantities, label='DP quantities MVP', color='red', linestyle='dashed')
        
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.legend(loc='upper left')

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        
        color = 'tab:gray'
        ax2.set_ylabel('Values', color=color)  # we already handled the x-label with ax1
        for data in so_data_all_income:
            ax2.plot(self.data.T, data, color='blue', alpha=0.3)
        for data in os_data_all_income:
            ax2.plot(self.data.T, data, color='green', alpha=0.3)
        for data in dp_data_all_income:
            ax2.plot(self.data.T, data, color='red', alpha=0.3)
        
        ax2.plot(self.data.T, so_mvp_data_income, label='SO values MVP', color='blue', linestyle='dashed')
        ax2.plot(self.data.T, os_mvp_data_income, label='OS values MVP', color='green', linestyle='dashed')
        ax2.plot(self.data.T, dp_mvp_data_income, label='DP values MVP', color='red', linestyle='dashed')
        
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.legend(loc='upper right')

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.title('Sales Quantities and Income Over Time')

        plt.savefig('figures/combined_sales_quantities_and_income.png')
        plt.close(fig)  # Close the figure to avoid display issues in some environments

    def plot6_distribution_center(self):
        # create one plot per scenario. Each subplot per scenario should show the distribution center for each family and time period with its inventory, sales, and overstock quantities.
        # Initialize dictionaries to hold the aggregated data for all scenarios
        scenarios = {}
        for s in self.data.S:
            scenario_data = []
            for t in self.data.T:
                for f in self.data.F:
                    for l in self.data.L:
                        shipped = self.family_model.getVarByName(f'DVf_l_t[{f},{l},{t}]').X
                        sales = self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                        overstock = self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                        inventory = self.family_model.getVarByName(f'IDs_f_l_t[{s},{f},{l},{t}]').X
                        scenario_data.append((s, f, l, t, shipped, inventory, sales, overstock))
            scenarios[s] = scenario_data
        scenarios1 = pd.DataFrame(scenarios)
        # Convert the tuples to a DataFrame with individual columns
        df_list = [pd.DataFrame(scenarios1[col].tolist(), columns=['s', 'f', 'l', 't', 'shipped', 'inventory', 'sales', 'overstock']) for col in scenarios1.columns]

        # Concatenate the individual DataFrames into one DataFrame
        df = pd.concat(df_list, keys=scenarios1.columns, names=['scenario', 'row'])

        # Reset index to flatten the multi-level index from concatenation
        df = df.reset_index(level='row', drop=True).reset_index()

        # Set the multi-level index
        df = df.set_index(['scenario', 'f', 'l', 't'])

        # Sort the index for better readability
        df = df.sort_index()

        # Display the resulting DataFrame
        print(df)

        # Reset the index to make 'scenario', 's', 'f', 'l', 't' columns available for plotting
        df_reset = df.reset_index()

        # Iterate over each scenario
        for scenario in df_reset['scenario'].unique():
            # Group by 'l', 't', 'f' and sum the values for the current scenario
            scenario_df = df_reset[df_reset['scenario'] == scenario].groupby(['l', 't', 'f']).sum().reset_index()

            # Get the unique distribution centers
            distribution_centers = scenario_df['l'].unique()
            
            # Create a 2x2 grid of subplots
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10), sharex=True)
            fig.suptitle(f'Scenario {scenario}', fontsize=16)
            axes = axes.flatten()  # Flatten the 2x2 array of axes for easier iteration
            
            # Iterate over each distribution center and plot on corresponding subplot
            for i, distribution_center in enumerate(distribution_centers):
                ax = axes[i]
                
                # Filter for the current distribution center
                dc_df = scenario_df[scenario_df['l'] == distribution_center]
                
                # Pivot the DataFrame to get a better structure for stacked bar plots
                sales_pivot = dc_df.pivot(index='t', columns='f', values='sales').fillna(0)
                overstock_pivot = dc_df.pivot(index='t', columns='f', values='overstock').fillna(0)
                
                # Plot sales and overstock as stacked bars
                sales_bars = sales_pivot.plot(kind='bar', stacked=True, ax=ax, cmap='tab20', alpha=0.7, edgecolor='black', legend=False)
                overstock_bars = overstock_pivot.plot(kind='bar', stacked=True, ax=ax, cmap='tab20', alpha=0.4, edgecolor='black', legend=False)

                # Add labels to the legend
                handles1, labels1 = ax.get_legend_handles_labels()
                new_labels = [f'Family {int(label)}' for label in labels1]
                ax.legend(handles=handles1, labels=new_labels, title='Family', loc='upper left')
                
                # Plot shipped and inventory as lines
                # ax2 = ax.twinx()
                # sns.lineplot(x='t', y='shipped', data=dc_df, ax=ax2, color='black', label='Shipped')
                # sns.lineplot(x='t', y='inventory', data=dc_df, ax=ax2, color='red', label='Inventory')
                
                # Set titles and labels
                ax.set_title(f'Distribution Center {distribution_center}', fontsize=14)
                ax.set_xlabel('Time')
                ax.set_ylabel('Sales/Overstock')
                # ax2.set_ylabel('Shipped/Inventory')
                
                # Combine legends
                handles1, labels1 = ax.get_legend_handles_labels()
                # handles2, labels2 = ax2.get_legend_handles_labels()
                # ax.legend(handles1 + handles2, new_labels + labels2, loc='upper left')
                ax.legend(handles1, new_labels, loc='upper left')
                #ax2.get_legend().remove()
            
            # Remove empty subplots
            for j in range(i+1, len(axes)):
                fig.delaxes(axes[j])
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig(f'figures/plot6_distribution_center_scenario_{scenario+1}.png')
            plt.close()

    def plot6_distribution_center_new(self, s_min = None, s_max = None, s_mean = None):
        # Initialize dictionaries to hold the aggregated data for all scenarios
        min_mean_max = {'min': s_min, 'max': s_max, 'mean': s_mean}
        # create one plot per scenario. Each subplot per scenario should show the distribution center for each family and time period with its inventory, sales, and overstock quantities.
        # Initialize dictionaries to hold the aggregated data for all scenarios
        scenarios = {}
        for s in self.data.S:
            scenario_data = []
            shipped = {}
            sales = {}
            overstocks = {}
            inventories = {}
            demands = {}
            for t in self.data.T:
                for f in self.data.F:
                    for l in self.data.L:
                        shipped[(t,l,f)] = self.family_model.getVarByName(f'DVf_l_t[{f},{l},{t}]').X
                        sales[(t,l,f)] = self.family_model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                        overstocks[(t,l,f)] = self.family_model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                        inventories[(t,l,f)] = self.family_model.getVarByName(f'IDs_f_l_t[{s},{f},{l},{t}]').X
                        demands[(t,l,f)] = self.data.dp[s][f][l][t]

                        #scenario_data.append((s, f, l, t, shipped, inventory, sales, overstock))
            # scenarios[s] = scenario_data
        #scenarios1 = pd.DataFrame(scenarios)

            fig, ax = plt.subplots(figsize=(12, 12))

            width = 0.3
            

            for t in self.data.T:
                for l in self.data.L:
                    for f in self.data.F:
                        ship = shipped.get((t,l,f), 0)
                        sale = sales.get((t,l,f), 0)
                        overstock = overstocks.get((t,l,f), 0)
                        inventory = inventories.get((t,l,f), 0)
                        demand = demands.get((t,l,f), 0)

                        if t > 0:
                            previous_value = inventories.get((t-1, l, f), 0) #dri_data.get(t, 0) #+ ri_data.get(t-1, 0)
                        else:
                            previous_value = self.data.i_0_f[l] #+ dri_data.get(t, 0)
                        


                        # usage of raw milk inventory
                        # inventory_usage = ri_data.get(t-1, 0) - ri_data.get(t, 0) if (t > 0) and ((ri_data.get(t-1, 0) - ri_data.get(t, 0)) > 0) else 0
                        # ax.bar(t-width/2, -inventory_usage, bottom=ri_data.get(t, 0) if t>0 else ri_data.get(t,0), label='RIs_t - Raw Milk Consumption satisfied\n by Raw Milk Inventory' if t == 1 else "", color='blue', hatch='..', width=1.5*width, alpha=0.9)

                        # dri_t bar plot
                        ax.bar(t-width, ship, bottom=previous_value, label='DVf_l_t - Raw Milk Input' if t == 1 else "", color='lime', width=width, alpha=0.9)
                        ship_end = previous_value + ship

                        # RSs_t bar plot
                        ax.bar(t-width, sale, bottom=ship_end, label='SOs_f_l_t - stock out of Inventory' if t == 1 else "", color='green', width=width, alpha = 0.9)
                        so_end = ship_end + sale
                        
                        # RM_t bar plot
                        ax.bar(t, -overstock, bottom=so_end, label='SOs_f_l_t - Overstock' if t == 1 else "", color='fuchsia', width=width, alpha=0.8)
                        overstock_end = so_end - overstock

                        # ROs_t bar plot
                        ax.bar(t, -demand, bottom=overstock_end, label='ROs_t - Raw Milk Disposal' if t == 1 else "", color='red', width=width, alpha=0.9)
                        demand_end = overstock_end - demand
                        # Update previous_value for next iteration
                        #previous_value = ro_end + dri_data.get(t, 0)

                #ax.bar(-width, self.data.r0, label='r0 - Initial Raw Milk Inventory\n from previous planning horizon', color='black', width=width, alpha=0.9)

                # ax.plot(list(rs_data.keys()), list(rs_data.values()), label='RSs_t', color='green')     # barplot starting from r0 respectivly from previous height/value
                # ax.plot(list(ro_data.keys()), list(ro_data.values()), label='ROs_t', color='red')       # barplot starting from r0 + RSs_t
                ax.plot(list(inventories.keys()), list(inventories.values()), label='IDs_f_l_t - DC Inventory', color='blue')      # LINE PLOT
                # ax.plot(list(dri_data.keys()), list(dri_data.values()), label='dri_t - Raw milk Daily Input', color='orange')  # line plot
                # ax.plot(list(rm_data.keys()), list(rm_data.values()), label='RM_t', color='purple')     # barplot starting from r0 - RM


                #ax.set_title(f'Raw milk supply consumption (Constraint (5)) - Scenario {s}{demand_suffix}')
                ax.set_xlabel('Time t in days')
                ax.set_ylabel('Quantity in tons')
                ax.legend(ncol=3, loc='best', bbox_to_anchor=(0.1, -0.2, 0.8, 0.5))
                
                """
            # Convert the tuples to a DataFrame with individual columns
            df_list = [pd.DataFrame(scenarios1[col].tolist(), columns=['s', 'f', 'l', 't', 'shipped', 'inventory', 'sales', 'overstock']) for col in scenarios1.columns]

            # Concatenate the individual DataFrames into one DataFrame
            df = pd.concat(df_list, keys=scenarios1.columns, names=['scenario', 'row'])

            # Reset index to flatten the multi-level index from concatenation
            df = df.reset_index(level='row', drop=True).reset_index()

            # Set the multi-level index
            df = df.set_index(['scenario', 'f', 'l', 't'])

            # Sort the index for better readability
            df = df.sort_index()

            # Display the resulting DataFrame
            print(df)

            # Reset the index to make 'scenario', 's', 'f', 'l', 't' columns available for plotting
            df_reset = df.reset_index()

            # Iterate over each scenario
            for scenario in df_reset['scenario'].unique():
                # Group by 'l', 't', 'f' and sum the values for the current scenario
                scenario_df = df_reset[df_reset['scenario'] == scenario].groupby(['l', 't', 'f']).sum().reset_index()

                # Get the unique distribution centers
                distribution_centers = scenario_df['l'].unique()
                
                # Create a 2x2 grid of subplots
                fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10), sharex=True)
                #fig.suptitle(f'Scenario {scenario}', fontsize=16)
                axes = axes.flatten()  # Flatten the 2x2 array of axes for easier iteration
                
                # Iterate over each distribution center and plot on corresponding subplot
                for i, distribution_center in enumerate(distribution_centers):
                    ax = axes[i]
                    
                    # Filter for the current distribution center
                    dc_df = scenario_df[scenario_df['l'] == distribution_center]

                    
                    # Pivot the DataFrame to get a better structure for stacked bar plots
                    sales_pivot = dc_df.pivot(index='t', columns='f', values='sales').fillna(0)
                    overstock_pivot = dc_df.pivot(index='t', columns='f', values='overstock').fillna(0)
                    
                    # Plot sales and overstock as stacked bars
                    #sales_bars = sales_pivot.plot(kind='bar', stacked=True, ax=ax, cmap='tab20', alpha=0.7, edgecolor='black', legend=False)

                    # Add labels to the legend
                    handles1, labels1 = ax.get_legend_handles_labels()
                    new_labels = [f'Sales Family {int(label)}' for label in labels1]
                    ax.legend(handles=handles1, labels=new_labels, title='Family', loc='upper left')

                    overstock_bars = overstock_pivot.plot(kind='bar', stacked=True, ax=ax, cmap='tab20', alpha=0.4, edgecolor='black', legend=True, label = 'Overstock')
                    """
                    
                    
                # # Plot shipped and inventory as lines
                # ax2 = ax.twinx()
                # sns.lineplot(x='t', y='shipped', data=dc_df, ax=ax2, color='black', label='Shipped')
                # sns.lineplot(x='t', y='inventory', data=dc_df, ax=ax2, color='red', label='Inventory')
                
                # Set titles and labels
                # handles1, labels1 = ax.get_legend_handles_labels()
                # new_labels = [f'Sales Family {int(float(label))}' for label in labels1]
                # ax.legend(handles=handles1, labels=new_labels, title='Family', loc='upper left')
                ax.set_title(f'Distribution Center {l}', fontsize=14)
                ax.set_xlabel('Time')
                ax.set_ylabel('Sales/Overstock')
                # ax2.set_ylabel('Shipped/Inventory')
                
                # Combine legends
                # handles1, labels1 = ax.get_legend_handles_labels()
                #handles2, labels2 = ax2.get_legend_handles_labels()
                # ax.legend(handles1 + handles2, new_labels + labels2, loc='upper left')
                #ax2.get_legend().remove()
                
                # Remove empty subplots
                # for j in range(i+1, len(ax)):
                #     fig.delaxes(ax[j])
                
                if s in min_mean_max.values():
                    value = [i for i in min_mean_max if min_mean_max[i] == s][0]
                    demand_suffix = f' ({value} demand)'
                    # global title
                    fig.suptitle(f'Scenario {s+1}{demand_suffix}', fontsize=16)
                    plt.tight_layout()
                    plt.savefig(f'figures/plot6_distribution_center_scenario_{s+1}_{value}.png')
                else:
                    fig.suptitle(f'Scenario {s+1}', fontsize=16)
                    plt.tight_layout()

                    # plt.tight_layout(rect=[0, 0.03, 1, 0.95])
                    plt.savefig(f'figures/plot6_distribution_center_scenario_{s+1}.png')
                plt.close()

    def plot7_manufacturing_output(self, s_min = None, s_max = None, s_mean = None):


        m =    {m for m in self.data.MP}
        t =    {t for t in self.data.T}
        mo =   {(m, t, self.family_model.getVarByName(f'MOm_t[{m},{t}]').X) for m in self.data.MP for t in self.data.T}
        z =    {(m, t, self.family_model.getVarByName(f'Zm_t[{m},{t}]').X) for m in self.data.MP for t in self.data.T}
        y =    {(m, t, k, self.family_model.getVarByName(f'Ym_t[{m},{t},{k}]').X) for m in self.data.MP for t in self.data.T for k in range(self.data.dmax[0]) if self.data.cty[m] == 0 }

        mo_df = pd.DataFrame(mo, columns=['Factory', 'Time', 'MO'])
        z_df = pd.DataFrame(z, columns=['Factory', 'Time', 'Z'])

        # DataFrame für Y erstellen
        y_columns = range(self.data.dmax[0])
        y_index = pd.MultiIndex.from_product([self.data.MP, self.data.T], names=['Factory', 'Time'])
        y_values = {(m, t): {k: self.family_model.getVarByName(f'Ym_t[{m},{t},{k}]') for k in y_columns} for m in self.data.MP for t in self.data.T}
        y_df = pd.DataFrame.from_dict({(i, j): y_values[i, j] for i in self.data.MP for j in self.data.T}, orient='index')
        y_df.index = y_index

        # Plot erstellen
        fig, ax1 = plt.subplots(figsize=(14, 7), sharex=True)

        # MO Plot
        sns.barplot(data=mo_df, x='Time', y='MO', hue='Factory', ax=ax1)
        ax1.set_ylabel('Manufacture Output (MO)')
        ax1.set_title('Manufacture Output (MO) and Shifts (Z) per Factory over Time')

        # Zweite Achse für Z und Y
        ax2 = ax1.twinx()

        # Z Plot
        sns.scatterplot(data=z_df, x='Time', y='Z', hue='Factory', ax=ax2, legend=False)
        ax2.set_ylabel('Number of Shifts (Z)')

        # Anpassungen und Anzeigen
        ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax2.legend(loc='upper right', bbox_to_anchor=(1.2, 1))

        # combine both legends:
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles=handles1 + handles2, labels=labels1 + labels2, loc='upper left', bbox_to_anchor=(1, 1))

        plt.tight_layout()

        plt.savefig('figures/plot7_manufacturing_output.png')

        # create heat map
        # combine mo_df and z_df

        fig = plt.figure(figsize=(14, 8))

        # DataFrames zusammenführen und pivotieren
        mo_z_df = mo_df.merge(z_df, on=['Factory', 'Time']).sort_values(by=['Factory', 'Time'])
        mo_z_df = mo_z_df.pivot(index='Time', columns='Factory', values='MO').T

        # Heatmap erstellen
        ax = sns.heatmap(mo_z_df, cmap='coolwarm', annot=True, fmt=".0f", linewidths=.5)


        # Sekundäre Y-Achse hinzufügen
        ax2 = ax.twinx()
        ax2.set_ylabel('\n\n\nManufacture Output (MO)')
        ax2.set_yticks([])  # Entfernt die Ticks der sekundären Y-Achse

        # Achsenbeschriftungen anpassen
        # ax.set_xlabel('Time')
        ax.set_ylabel('Manufacturing Plant')

        # Entferne die Ticks und Labels der ursprünglichen y-Achse
        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_label_position('left')
        #ax.set_yticks([])

       # plt.title('Manufacture Output (MO) per Factory over Time')
        plt.tight_layout()

        plt.savefig('figures/plot7-1_manufacturing_output.png')

