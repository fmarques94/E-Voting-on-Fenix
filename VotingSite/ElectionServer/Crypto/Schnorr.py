import random
import secrets
import hashlib
import math
import ElectionServer.Crypto.primeGenerator as Prime
import ElectionServer.Crypto.numbTheory

class Schnorr:
    #Implements the Schnorr signature scheme

    def __init__(self,keys=None, Bq=160, Bp = 1024):
        if keys:
            self.keys = keys
        self.Bq = Bq
        self.Bp = Bp
        return None

    def generate_keys(self,parameters):
        
        assert "p" in parameters
        assert "q" in parameters
        assert "g" in parameters

        p = parameters["p"]
        q = parameters["q"]
        alpha = parameters["g"]

        a = secrets.randbelow(q)        # 0<= 0 <= q-1
        beta = pow(alpha,a,p)

        self.keys={
            "pub":{
                "p":p,
                "q":q,
                "alpha":alpha,
                "beta":beta
            },
            "priv":{
                "a":a
            }
        }

        return self.keys

    def get_public_key(self):
        if self.keys is None:
            raise Exception("No keys available")
        if not "pub" in self.keys:
            raise Exception("No public key available")
        return self.keys["pub"]

    def get_private_key(self):
        if self.keys is None:
            raise Exception("No keys available")
        if not "priv" in self.keys:
            raise Exception("No private key available")
        return self.keys["priv"]

    def sign(self,message):
        pub = self.get_public_key()
        priv = self.get_private_key()

        assert "alpha" in pub
        assert "p" in pub
        assert "beta" in pub
        assert "q" in pub
        assert "a" in priv

        p = pub["p"]
        q = pub["q"]
        beta = pub["beta"]
        alpha = pub["alpha"]
        a = priv["a"]
        k = 0
        while k == 0:                   #1<=k<=q-1
            k = secrets.randbelow(q)
        aux = pow(alpha,k,p)

        print(aux)

        s1 = self.__hash(message,aux)

        s2 = (k+a*s1)%q

        return s1,s2
       

    def verify(self,signature,message):
        pub = self.get_public_key()

        assert "alpha" in pub
        assert "p" in pub
        assert "beta" in pub
        assert "q" in pub

        p = pub["p"]
        q = pub["q"]
        beta = pub["beta"]
        alpha = pub["alpha"]

        #print(pow(pow(beta,p-2,p),signature[0],p))
        aux = (pow(alpha,signature[1],p) * pow(pow(beta,p-2,p),signature[0],p))%p
        
        #print("aux = "+str(aux))

        return signature[0] == self.__hash(message,aux)
        

    def __hash(self,message,C):
        hash = hashlib.sha256()
        hash.update(str(message).encode())
        hash.update(str(C).encode())
        return int(hash.hexdigest(),16)
