class IRSpectrum(object):
    '''This is the class that will be used to store the graphs that
    we use in the program. It will store a CAS, the formula, the name, 
    and a string containing the path to the graph'''
    
    def __init__(self, cas, formula, name, graph):
        self.cas = cas
        self.formula = formula
        self.name = name
        self.graph = graph

    def compare(self, other):
        pass