import pandas as pd

''' results.py '''

class Results:
    def __init__(self, model, T, F, S, FT, MP, CT, L):
        self.model = model

        self.T = T
        self.F = F
        self.S = S
        self.FT = FT
        self.MP = MP
        self.CT = CT
        self.L = L

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

        pd.set_option('display.width', 100)

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

    def create_sales_t(self):
        # Compute the value for 'Sales [t]'

        sales_t = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                        if self.model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]') is not None:
                            sales_t += self.model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]').x


        return sales_t

    def create_lost_sales_t(self):
        # Compute the value for 'Lost Sales [t]'

        lost_sales_t = 0

        for s in self.S:
            for f in self.F:
                for l in self.L:
                    for t in self.T:
                        if self.model.getVarByName(f'LSs_f_l_t[{s},{f},{l},{t}]') is not None:
                            lost_sales_t += self.model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]')

        print(lost_sales_t)

        return lost_sales_t

    def create_distressed_sales_t(self):
        # Compute the value for 'Distressed Sales of Products [t]'
        # Replace the following line with your computation
        distressed_sales_t = 1
        return distressed_sales_t

    def create_raw_material_losses_t(self):
        # Compute the value for 'Raw Material Losses [t]'
        # Replace the following line with your computation
        raw_material_losses_t = 1
        return raw_material_losses_t

    def create_raw_material_purchase_t(self):
        # Compute the value for 'Raw Material Purchase [t]'
        # Replace the following line with your computation
        raw_material_purchase_t = 1
        return raw_material_purchase_t

    def create_exports_t(self):
        # Compute the value for 'Exports [t]'
        # Replace the following line with your computation
        exports_t = 1
        return exports_t

    def create_production_t(self):
        # Compute the value for 'Production [t]'
        # Replace the following line with your computation
        production_t = 1
        return production_t

    def create_product_shipped_t(self):
        # Compute the value for 'Product shipped to DC [t]'
        # Replace the following line with your computation
        product_shipped_t = 1
        return product_shipped_t

    def create_sales_income_mu(self):
        # Compute the value for 'Sales Income [MU]'
        # Replace the following line with your computation
        sales_income_mu = 1
        return sales_income_mu

    def create_distressed_sales_mu(self):
        # Compute the value for 'Distressed Sales of Products [MU]'
        # Replace the following line with your computation
        distressed_sales_mu = 1
        return distressed_sales_mu

    def create_raw_material_losses_cost_mu(self):
        # Compute the value for 'Raw Material Losses Cost [MU]'
        # Replace the following line with your computation
        raw_material_losses_cost_mu = 1
        return raw_material_losses_cost_mu

    def create_raw_material_purchase_cost_mu(self):
        # Compute the value for 'Raw Material Purchase Cost [MU]'
        # Replace the following line with your computation
        raw_material_purchase_cost_mu = 1
        return raw_material_purchase_cost_mu

    def create_exports_income_mu(self):
        # Compute the value for 'Exports Income [MU]'
        # Replace the following line with your computation
        exports_income_mu = 1
        return exports_income_mu

    def create_cost_shipped_dc_mu(self):
        # Compute the value for 'Cost for shipped to DC [MU]'
        # Replace the following line with your computation
        cost_shipped_dc_mu = 1
        return cost_shipped_dc_mu

    def create_setups_cost_mu(self):
        # Compute the value for 'Setups Cost [MU]'
        # Replace the following line with your computation
        setups_cost_mu = 1
        return setups_cost_mu

    def create_expected_net_benefits_mu(self):
        # Compute the value for 'Expected Net Benefits [MU]'
        # Replace the following line with your computation
        expected_net_benefits_mu = 1
        return expected_net_benefits_mu
    
    def calculate_deviation(self, value, comparison):
        if comparison == 0:
            return 'N/A'
        return f'+{round((value - comparison) / comparison * 100, 1)}%'

    def PrintResults(self, comparedResults):
        print('=========================================')
        print('Results:')
        print('Objective value: %g' % self.model.objVal)
        print(comparedResults)

    

    def ComputeResults(self):

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
            'Metric': ['Sales [t]', 'Lost Sales [t]', 'Distressed Sales of Products [t]', 'Raw Material Losses [t]', 'Raw Material Purchase [t]', 'Exports [t]', 'Production [t]', 'Product shipped to DC [t]', 'Sales Income [MU]', 'Distressed Sales of Products [MU]', 'Raw Material Losses Cost [MU]', 'Raw Material Purchase Cost [MU]', 'Exports Income [MU]', 'Cost for shipped to DC [MU]', 'Setups Cost [MU]', 'Expected Net Benefits [MU]'],
            'SP': [self.sales_t, self.lost_sales_t, self.distressed_sales_t, self.raw_material_losses_t, self.raw_material_purchase_t, self.exports_t, self.production_t, self.product_shipped_t, self.sales_income_mu, self.distressed_sales_mu, self.raw_material_losses_cost_mu, self.raw_material_purchase_cost_mu, self.exports_income_mu, self.cost_shipped_dc_mu, self.setups_cost_mu, self.expected_net_benefits_mu],
            'EMVP': [self.sales_t, self.lost_sales_t, self.distressed_sales_t, self.raw_material_losses_t, self.raw_material_purchase_t, self.exports_t, self.production_t, self.product_shipped_t, self.sales_income_mu, self.distressed_sales_mu, self.raw_material_losses_cost_mu, self.raw_material_purchase_cost_mu, self.exports_income_mu, self.cost_shipped_dc_mu, self.setups_cost_mu, self.expected_net_benefits_mu],
            'Deviation': [  self.calculate_deviation(self.sales_t, self.sales_t),
                            self.calculate_deviation(self.lost_sales_t, self.lost_sales_t),
                            self.calculate_deviation(self.distressed_sales_t, self.distressed_sales_t),
                            self.calculate_deviation(self.raw_material_losses_t, self.raw_material_losses_t),
                            self.calculate_deviation(self.raw_material_purchase_t, self.raw_material_purchase_t),
                            self.calculate_deviation(self.exports_t, self.exports_t),
                            self.calculate_deviation(self.production_t, self.production_t),
                            self.calculate_deviation(self.product_shipped_t, self.product_shipped_t),
                            self.calculate_deviation(self.sales_income_mu, self.sales_income_mu),
                            self.calculate_deviation(self.distressed_sales_mu, self.distressed_sales_mu),
                            self.calculate_deviation(self.raw_material_losses_cost_mu, self.raw_material_losses_cost_mu),
                            self.calculate_deviation(self.raw_material_purchase_cost_mu, self.raw_material_purchase_cost_mu),
                            self.calculate_deviation(self.exports_income_mu, self.exports_income_mu),
                            self.calculate_deviation(self.cost_shipped_dc_mu, self.cost_shipped_dc_mu),
                            self.calculate_deviation(self.setups_cost_mu, self.setups_cost_mu),
                            self.calculate_deviation(self.expected_net_benefits_mu, self.expected_net_benefits_mu)],
            'SP-paper': self.paper_values_table6()['SP'],
            'EMVP-paper': self.paper_values_table6()['EMVP'],
            'Deviation-paper': self.paper_values_table6()['Deviation'],
            #'diff SP paper-model': self.paper_values_table6()['SP'] - listOfResults,
            #'diff EMVP paper-model': self.paper_values_table6()['EMVP'] - listOfResults,
            #'deviation SP paper-model': self.calculate_deviation(listOfResults['SP'], self.paper_values_table6()['SP']),
        }
        df = pd.DataFrame(data)
        return df

    #results = ComputeResults(self)
    
    def Evaluate_results(self):
        computedResults = self.ComputeResults()
        self.PrintResults(computedResults)
        pass

    