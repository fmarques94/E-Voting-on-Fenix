import ElGamal
import Schnorr
import ParameterGenerator
import secrets

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

    #parameters = {'p':2579,
	#'g':2}
    schnorr = Schnorr.Schnorr()
    schnorr.keys={
            "pub":{
                "p":54596238329429367799219317166956355608149049433674341610528584708625084419129371690543862544071054859016228541203530039407999782430340306818051296378230235424021625629535431285870168049317060060782738915256521090176225331521467715784633297355586696177670519143687585274791449948075965550273591916258349825309,
                "q":1242933729413885884649508283744264352387925537937,
                "alpha":47076197901785643808028816214703055630223823971600867368404129632220204628738010997471811723999765459552191058004115410573028939705910540703080712709329483947362027162081391557321285796995097116062898545515079385813505850686084996043403269207514412610401723748931250315361530507137709620434500737279351547216,
                "beta":33809272378387549105818833283006363110233542982252343394438335751533133941437024533325204354712760505261834585851110176903811973219505986057617398379129354824647033196733237206302141543298821748758792684166235354556628940478498588485850201032461282836659919604727184720565728072815423842808328272658301578338
            },
            "priv":{
                "a":1108380066908650876406278864096782104591752573332
            }
        }
    
    print("Keys set")
	
    signature = schnorr.sign(10)
    print(signature)
    print("")
    print("Going to verify if value is 5")
    print(schnorr.verify(signature,5))
    print("")
    print("Going to verify if value is 10")
    print(schnorr.verify(signature,10))
    print("")
    '''
    parameters = ParameterGenerator.generate_parameters()
        
    assert parameters
    elgamal = ElGamal.ElGamal()
    elgamal.generate_keys(parameters)
	
    x = elgamal.keys["priv"]["d"]
    h = elgamal.keys["pub"]["y"]
    #print("h="+str(h))
    #print("x="+str(x))
    p = parameters['p']
    g = parameters['g']
	
    e = secrets.randbelow(p)
    k = secrets.randbelow(p)
	
    r = pow(g,k,p)
	
    print('Testing multiplication')
    s = k + x*e

	#r = g^k mod p = (g^(k+xe) * g(-xe) mod p = g^s*h^-e mod p
	
    aux = (pow(g,s,p)*pow(pow(h,p-2,p),e,p))%p
	
    print(r == aux)
    print("r="+str(r))
    print("aux="+str(aux))
    #print("aux1="+str(aux1))
    #print("aux2="+str(aux2))
    print("h="+str(h))
    print("e="+str(e))
    print("s="+str(s))
    print("k="+str(k))


    #print("Generated parameters")
    #print(parameters)
    #print("")
    
    #testElGamal()
    #testSchnorr()

    #testSharedSecret()
    '''
#print("")
#print("Tests Ended with Success")


