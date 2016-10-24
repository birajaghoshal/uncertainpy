from uncertainpy import Model

import numpy as np
import odespy

# The class name and file name must be the same
class ValderramaHodkinHuxleyModel(Model):
    """
    The model must be able to handle these calls

    simulation = model()
    simulation.load()
    simulation.setParameters(parameters -> dictionary)
    simulation.run()
    simulation.save(current_process -> int)

    simulation.cmd()
    """
    def __init__(self, parameters=None):
        """
        Init must be able to be called with 0 arguments
        """
        Model.__init__(self, parameters=parameters)


        ## HH Parameters
        self.V_rest = -10   # mV
        self.Cm = 1         # uF/cm**2
        self.gbar_Na = 120  # mS/cm**2
        self.gbar_K = 36    # mS/cm**2
        self.gbar_l = 0.3   # mS/cm**2
        self.E_Na = 115     # mV
        self.E_K = -12      # mV
        self.E_l = 10.6     # mV

        self.m0 = 0.0011    # unitless
        self.n0 = 0.0003    # unitless
        self.h0 = 0.9998    # unitless

        ## setup parameters and state variables
        self.I_value = 150     # mA
        T = 15                 # ms
        dt = 0.025             # ms
        self.t = np.arange(0, T + dt, dt)


        self.xlabel = "time [ms]"
        self.ylabel = "voltage [mv]"


    def I(self, t):
        # if t >= 5 and t <= 30:
        #     return self.I_value
        # else:
        #     return 0
        return self.I_value

    # K channel
    def alpha_n(self, V):
        return 0.01*(10 - V)/(np.exp((10 - V)/10.) - 1)

    def beta_n(self, V):
        return 0.125*np.exp(-V/80.)

    def n_f(self, n, V):
        return self.alpha_n(V)*(1 - n) - self.beta_n(V)*n

    def n_inf(self, V):
        return self.alpha_n(V)/(self.alpha_n(V) + self.beta_n(V))


    # Na channel (activating)
    def alpha_m(self, V):
        return 0.1*(25 - V)/(np.exp((25 - V)/10.) - 1)

    def beta_m(self, V):
        return 4*np.exp(-V/18.)

    def m_f(self, m, V):
        return self.alpha_m(V)*(1 - m) - self.beta_m(V)*m

    def m_inf(self, V):
        return self.alpha_m(V)/(self.alpha_m(V) + self.beta_m(V))


    # Na channel (inactivating)
    def alpha_h(self, V):
        return 0.07*np.exp(-V/20.)

    def beta_h(self, V):
        return 1/(np.exp((30 - V)/10.) + 1)

    def h_f(self, h, V):
        return self.alpha_h(V)*(1 - h) - self.beta_h(V)*h

    def h_inf(self, V):
        return self.alpha_h(V)/(self.alpha_h(V) + self.beta_h(V))


    def dXdt(self, X, t):
        V, h, m, n = X

        g_Na = self.gbar_Na*(m**3)*h
        g_K = self.gbar_K*(n**4)
        g_l = self.gbar_l

        dmdt = self.m_f(m, V)
        dhdt = self.h_f(h, V)
        dndt = self.n_f(n, V)

        dVdt = (self.I(t) - g_Na*(V - self.E_Na) - g_K*(V - self.E_K) - g_l*(V - self.E_l))/self.Cm

        return [dVdt, dhdt, dmdt, dndt]


    def run(self):

        # self.h0 = self.h_inf(self.V_rest)
        # self.m0 = self.m_inf(self.V_rest)
        # self.n0 = self.n_inf(self.V_rest)
        #

        initial_conditions = [self.V_rest, self.h0, self.m0, self.n0]


        solver = odespy.RK4(self.dXdt)
        solver.set_initial_condition(initial_conditions)
        X, t = solver.solve(self.t)

        self.t = t
        self.U = X[:, 0]