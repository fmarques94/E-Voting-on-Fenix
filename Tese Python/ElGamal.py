import random
import secrets
import primeGenerator as Prime

class ElGamal:
    #Python implementation of the ElGamal encryption system

    def __init__(self,keys=None):
        if keys:
            self.keys = keys
        return None

    def generate_keys(self,parameters):
        assert "p" in parameters
        assert "g" in parameters
        p = parameters["p"]
        g = parameters["g"]
        priv = 0
        while priv == 0:
            priv = secrets.randbelow(p)
        y = pow(g,priv,p)

        self.keys={"pub":
        {
            "p":p,
            "g":g,
            "y":y},
        "priv":{
            "d":priv
            }
        }

        return self.keys

    def __get_public_key(self):
        if self.keys is None:
            raise Exception("No keys.")
        if "pub" not in self.keys:
            raise Exception("No Public Key")
        return self.keys["pub"]

    def __get_private_key(self):
        if self.keys is None:
            raise Exception("No keys.")
        if "priv" not in self.keys:
            raise Exception("No Private Key")
        return self.keys["priv"]

    def encrypt(self,m):
        pub = self.__get_public_key()

        assert "p" in pub
        assert "g" in pub
        assert "y" in pub

        p = pub["p"]
        g = pub["g"]
        y = pub["y"]

        k = 0
        while k==0:
            k = secrets.randbelow(p)

        c1 = pow(g,k,p)

        c2 = (pow(y,k,p)*pow(g,m,p))%p

        return c1,c2,k

    def decrypt(self,x):
        pub = self.__get_public_key()
        priv = self.__get_private_key()
        assert "p" in pub
        assert "g" in pub
        assert "y" in pub
        assert "d" in priv

        p = pub["p"]
        g = pub["g"]
        y = pub["y"]
        d = priv["d"]

        c1 = x[0]
        c2 = x[1]


        aux = pow(pow(c1,p-2,p),d,p)
        #r = pow(c1,p-1-d,p)
        m = (aux*(c2%p))%p

        return m

    def generate_lookup_table(self,a=0,b=10**3):
		#
		# Receives a base g, prime p, a public key pub and a interval [a,b],
		# computes and encrypts all values g**i mod p for a <= i <= b and
		# returns a lookup table
		#
        pub = self.__get_public_key()
        alpha = pub["g"]
        p = pub["p"]
        table = {}
        c=0
        for i in range(a,b):
            if i==0:
                c = 1%p
                table[c]=i
            else:
                c = (c*alpha)%p
                table[c] = i
        return table