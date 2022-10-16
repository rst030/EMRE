ge = 2.0023193043625635
mwfq = 9.6e9  # Hz
b0 = 3420 / 1e4  # T
h = 6.62607015e-34  # J / Hz
mu_b = 9.274009994e-24  # J / T

class g_calculator(object):

    g = 2

    def __init__(self):
        self.g = h * mwfq / mu_b / b0
        pass

    def calculate_g(self,_mwfq,_b0): # calculate g from microwave frequency and B
        return h * _mwfq / mu_b / _b0

    def calculate_b0(self,_mwfq,_g): # calculate B from microwave frequency and g
        return h * _mwfq / mu_b / _g

    def calculate_mwfq(self,_b0, _g): # calculate microwave frequency from B and h
        return mu_b * _b0 * _g/h