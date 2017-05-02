import ElGamal
import Schnorr
import ParameterGenerator

def testSchnorr():
    print("Testing Schnorr")
    print("Going to generate keys")
    schnorr = Schnorr.Schnorr()
    schnorr.generate_keys(parameters)
    print(schnorr.keys)
    print("")
    print("Going to sign value 10")
    signature = schnorr.sign(10)
    print(signature)
    print("")
    print("Going to verify if value is 5")
    print(schnorr.verify(signature,5))
    print("")
    print("Going to verify if value is 10")
    print(schnorr.verify(signature,10))
    print("")


def testElGamal():
    print("Testing El Gamal")
    print("Going to generate keys")
    elgamal = ElGamal.ElGamal()
    elgamal.generate_keys(parameters)
    print(elgamal.keys)
    print("")
    print("Going to encrypt value 5")
    ciphertext = elgamal.encrypt(5)
    print("Encripted value 5:")
    print(ciphertext)
    print("")
    print("Going to decrypt value 5:")
    plaintext = elgamal.decrypt(ciphertext)
    print("Decripted Value:")
    print(plaintext)
    print("")
    print("Going to generate lookup table and search for the value")
    table = elgamal.generate_lookup_table()
    print("Lookup table generated. Searching value:")
    print("Value = "+str(table[plaintext]))
    print("")
    print("Testing homomorphic propertie.")
    print("Encripting value 20")
    ciphertext2 = elgamal.encrypt(20)
    print(ciphertext2)
    print("")
    print("Using homomorphic propertie")
    ciphertext3 = []
    ciphertext3.append(ciphertext[0]*ciphertext2[0])
    ciphertext3.append(ciphertext[1]*ciphertext2[1])
    print(ciphertext3)
    print("")
    print("Going to decrypt and show result. Should be 25")
    plaintext2 = elgamal.decrypt(ciphertext3)
    print("Value = " + str(table[plaintext2]))
    print("")

def testSharedSecret():
    print("Testing shared secret")
    print("Generating two key pairs")

    elgamal1 = ElGamal.ElGamal()
    elgamal2 = ElGamal.ElGamal()
    elgamal3 = ElGamal.ElGamal()

    elgamal1.generate_keys(parameters)
    elgamal2.generate_keys(parameters)

    keys = {"pub":{
            "p":parameters["p"],
            "g":parameters["g"],
            "y":elgamal1.keys["pub"]["y"]*elgamal2.keys["pub"]["y"]
        },
        "priv":{
            "d":elgamal1.keys["priv"]["d"]+elgamal2.keys["priv"]["d"]
        }
    }

    print(keys)

    elgamal3.keys = keys

    print("Generated shared key. Encrypting value 5")
    ciphertext = elgamal3.encrypt(5)
    print("Decrypting and generating table")
    table = elgamal3.generate_lookup_table()
    print(table[elgamal3.decrypt(ciphertext)])


print("Starting tests")
#number of tests
nTests = 1

for i in range(nTests):
    print("Generating parameters")

    parameters = None

    parameters = ParameterGenerator.generate_parameters()

    assert parameters

    #print("Generated parameters")
    #print(parameters)
    #print("")

    testElGamal()
    #testSchnorr()

    testSharedSecret()

print("")
print("Tests Ended with Success")


