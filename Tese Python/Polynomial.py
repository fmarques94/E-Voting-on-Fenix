import random

class Polynomial:
    'Class that contains a polynomial'

    def __init__(self,degree,parameters):
        self.coefficients = []
        self.p = parameters["p"]
        self.q = parameters["q"]
        self.g = parameters["g"]
        self.__generatePolynomial(degree)

    def __generatePolynomial(self,degree):
        i=0
        while i!=degree:
            self.coefficients.append(random.randrange(1,self.q))
            i+=1
    
    def calculate(self,variable):
        result = self.coefficients[0]
        for i in range(1,len(self.coefficients)):
            result += self.coefficients[i]*pow(variable,i)
        return result
        
    
