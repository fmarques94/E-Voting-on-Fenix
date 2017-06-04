
import random
import secrets
import ElectionServer.Crypto.numbTheory as numbTheory
import ElectionServer.Crypto.primeGenerator as Prime


def generate_parameters(p_size=1024,q_size=160):
    while True:
        try:
            q = Prime.generate_large_prime(q_size)
        except Exception:
            print("Could not generate prime with " + str(q_size) + " bytes. Trying again.")
        p = secrets.randbits(p_size - q_size + 1)*q+1
        if Prime.is_prime(p,11):
            break
    aux = numbTheory.primitive_root(p)

    g = pow(aux,(p-1)//q, p)

    parameters = {"q":q,"p":p,"g":g}

    return parameters
    