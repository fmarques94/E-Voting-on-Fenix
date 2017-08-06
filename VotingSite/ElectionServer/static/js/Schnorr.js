function Schnorr(p,q,g,a){
    this.p = p
    this.q = q
    this.g = g
    this.a = a

    this.sign = function(value){
        var value = new BigInteger(value.toString(10),10);
        var k = this.generateNumber()
        var aux = this.g.modPow(k,this.p)
        var s1 = new BigInteger(sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(value.toString(10)+aux.toString(10))),16);
        s2 = ((this.a.multiply(s1)).add(k)).mod(this.q)
        return [s1,s2]
    }

    this.generateNumber = function(){
        k = null
        while(k==undefined){
            //var array = Uint32Array.from(sjcl.random.randomWords(32));
            var array = new Uint32Array(4);
            self.crypto.getRandomValues(array);
            result = ""
            for(i=0;i<4;i++){
                result = result + array[i].toString();
            }
            k = new BigInteger(result,10);
            //console.log(k.toString(10));
            //console.log(this.q.toString(10));
            if((k.max(this.q)).equals(k)){
                k = null;
            }
        }
        return k
    }

    this.verify = function(message,signature,pCredential){
        var s1 = new BigInteger(signature[0],10);
        var s2 = new BigInteger(signature[1],10);

        var aux = ((this.g.modPow(s2,this.p)).multiply((pCredential.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(s1,this.p))).mod(this.p);
        
        return s1.toString(16)==sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(message.toString(10)+aux.toString(10)));
    }
}