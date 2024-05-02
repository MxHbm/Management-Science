### Script for generating data fpr our model

class Parameters:

    def __init__(self, T: list, F: list, S: list, FT: list, MP: list, CT: list, L: list):

        #First definition of parameters and call for implementing them
        self.fty = self.create_fty()
        self.cty = self.create_cty()
        self.fpr = self.create_fpr()
        self.fy = self.create_fy()
        self.rsc = self.create_rsc()
        self.roc = self.create_roc()
        self.el = self.create_el()
        self.tau = self.create_tau()
        self.i0f = self.create_i0f()
        self.tl_min = self.create_tl_min()
        self.tl_max = self.create_tl_max()
        self.r0 = self.create_r0()
        self.r_max = self.create_r_max()
        self.dmax = self.create_dmax()
        self.cmin = self.create_cmin()
        self.cmax = self.create_cmax()
        self.alpha = self.create_alpha()
        self.ost = self.create_ost()
        self.wp = self.create_wp(MP, T, self.sigma)
        self.el_min = self.create_el_min(F)
        self.el_max = self.create_el_max(F)
        self.is_ = self.create_is(M)
        self.omega_fw = self.create_omega_fw(F)
        self.omega_dc = self.create_omega_dc(F)
        self.rr = self.create_rr(F)
        self.r = self.create_r(F)
        self.re = self.create_re(F)
        self.imax = self.create_imax()
        self.zmax = self.create_zmax()
        self.sc = self.create_sc()
        self.beta = self.create_beta()
        self.sigma = self.create_sigma()
        self.iwip0 = self.create_iwip0()
        self.tc = self.create_tc()
        self.sco = self.create_sco()

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

    def create_tau(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_i0f(self) -> list:
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

    def create_imax(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_zmax(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_sc(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_beta(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_sigma(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_iwip0(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_tc(self) -> list:
        ''' Add description of the function here '''
        pass

    def create_sco(self) -> list:
        ''' Add description of the function here '''
        pass
