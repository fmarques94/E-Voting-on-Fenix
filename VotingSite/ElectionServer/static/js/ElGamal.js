function ElGamal(p,g,h){
    this.p = p;
    this.g = g;
    this.h = h;

    this.generate_key = function(){
        priv = this.generateNumberBelowP();
        y = this.g.modPow(priv,this.p)
        return [y.toString(10),priv.toString(16)]
    }

    this.encrypt = function(encrypt, random=null){
        if(random==null){
            var k = this.generateNumberBelowP();
        }
        else{
            var k = new BigInteger(random,10);
        }
        var c1 = this.g.modPow(k,this.p)
        var value = new BigInteger(encrypt.toString(),10)
        var c2 = ((this.h.modPow(k,this.p)).multiply(this.g.modPow(value,this.p))).mod(this.p)
        return [c1,c2,k]
    }

    this.generateNumberBelowP = function(){
        var k = null
        while(k==null){
            var array = new Uint32Array(32);
            //var array = Uint32Array.from(sjcl.random.randomWords(32));
            //console.log(array);
            self.crypto.getRandomValues(array);
            var result = ""
            for(var i=0;i<32;i++){
                result = result + array[i].toString();
            }
            k = new BigInteger(result,10);
            if((k.max(this.p)).equals(k)){
                k = null;
            }
        }
        return k
    }
}