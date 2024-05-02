### Script for generating data fpr our model

class Parameters_FirstStage:

    def __init__(self, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):

        #First definition of parameters and call for implementing them
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
        self.i_0 = self.create_i_0()
        self.tl_min = self.create_tl_min()
        self.tl_max = self.create_tl_max()
        self.r0 = self.create_r0()
        self.r_max = self.create_r_max()
        self.dmax = self.create_dmax()
        self.cmin = self.create_cmin()
        self.cmax = self.create_cmax()
        self.alpha = self.create_alpha()
        self.ost = self.create_ost()
        #Christoph
        self.wp = self.create_wp(MP, T, self.sigma)
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
        self.beta = self.create_beta()
        self.sigma = self.create_sigma()
        self.iwip0 = self.create_iwip0()
        self.tc = self.create_tc()
        self.sco = self.create_sco()

        # Additonal
        self.names_DC = self.create_names_DC()


    def create_fty(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_cty(self) -> list:
        ''' Add description of the function here '''
        pass

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
        ''' Transportzeit von Fabrik zu verteilzentrum in tagen'''

        transportzeit_fabrik_dc = [2,1,1,2,0,1,0,2,1]
        
        return transportzeit_fabrik_dc

    def create_i_0(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_tl_min(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_tl_max(self) -> list:
        ''' Add description of the function here '''
        pass

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

    def create_wp(self, M, T, sigma ) -> list:
        ''' m: manufacturing plant, 
            t: time (days), 
            sigma: process time for family produced in manufacturing plant m'''

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
        ''' distrinution center shelf-life of products of family f'''
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
        ''' Maximale Lagerbestände am Standort l für frische und trockene Produktfamilien '''

        max_lager_produktgruppen = [[12,10],[68, 114],[16, 35],[16,40],[9, 27],
                                    [31,54],[20, 81],[20,58],[58,195]]
        
        return max_lager_produktgruppen

    def create_zmax(self) -> list:
        ''' Für schichtbasierte Produktion maximale Schichten, sonst 1'''
        pass

    def create_sc(self) -> list:
        ''' Produktionskapazität der Produktionsstätte m einer Arbeitsschich '''
        pass

    def create_beta(self) -> list:
        ''' Verschlechterungskoeffizient für Produkte, die in Werk m hergestellt werden '''
        pass

    def create_sigma(self) -> list:
        ''' Prozesszeit in Perioden für die in der Produktionsstätte m hergestellte Produktfamilie '''
        pass

    def create_iwip0(self) -> list:
        ''' Bestand unfertiger Erzeugnisse aus vorherigem Planungshorizont in Produktionsstätte m '''
        pass

    def create_tc(self) -> list[list[int]]:
        ''' Transportkosten vom Produktionskomplex zum Verteilzentrum '''
        
        transportkosten_produktgruppen_matrix = [[15.641,13.034],[4.956, 4.13],[10.332,8.61],[14.818, 12.348],[0.067, 0.056],
                                                 [14.364, 11.97],[4.032, 3.36],[21.638,18.032],[9.021,7.518]]
        
        return transportkosten_produktgruppen_matrix
    

    def create_sco(self) -> int:
        ''' Setup Kosten in Monetary Units'''
        
        setup = 20 # unit is MU

        return setup

    def create_names_DC(self) -> list[str]: 
        """ Namen der Distribution center """

        return ["DC-SAL", "DC-CBA", "DC-CTE","DC-POS","DC-RAF","DC-MZA", "DC-ROS", "DC_NQN", "DC-BUE"]
