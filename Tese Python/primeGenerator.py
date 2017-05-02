import random
import secrets
import math

def is_prime(n, s):
    #Uses Miller-Rabin algorithm to verify if a number is prime
    #Returns True(n is probaly prime) or False (n is definitly composite)

    if n<3:         #No number under 3 is prime
        return False
    if n%2 == 0:    #No even number is prime
        return False
    r = 0
    d = n-1
    while d%2==0:
        r +=1
        d = d // 2
    for i in range(s):
        a = random.randrange(2, n-1)
        x = pow(a, d, n)
        if x!=1 and x + 1 != n:
            for i in range(1, r):
                x = pow(x, 2, n)
                if x==1:
                    return False
                elif x==n-1:
                    a = 0
                    break
            if a:
                return False
    return True

def generate_large_prime(k, s=11):
    #Generates a large prime of k bits

    numberOfAttempts = 100*(math.log(k,  2) +  1)
    while numberOfAttempts>0:
        n = secrets.randbits(k)
        numberOfAttempts-=1
        if is_prime(n, s) == True:
            return n
    raise Exception("Failed to find a prime after " +  str(numberOfAttempts) +  " attempts")

