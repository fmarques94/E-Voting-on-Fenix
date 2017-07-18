function ElGamal(p,g,h){
    this.p = p;
    this.g = g;
    this.h = h;

    this.generate_key = function(){
        priv = this.generateNumberBelowP(this.p);
        y = this.g.modPow(priv,this.p)
        return [y.toString(10),priv.toString(16)]
    }

    this.encrypt = function(encrypt){
        k = this.generateNumberBelowP(this.p);
        c1 = this.g.modPow(k,p)
        value = new BigInteger(encrypt.toString(),10)
        c2 = ((this.h.modPow(k,this.p)).multiply(this.g.modPow(value,this.p))).mod(this.p)
        return [c1,c2]
    }

    this.generateNumberBelowP = function(p){
        k = null
        while(k==undefined){
            var array = new Uint32Array(32);
            window.crypto.getRandomValues(array);
            result = ""
            for(i=0;i<32;i++){
                result = result + array[i].toString();
            }
            k = new BigInteger(result,10);
            if(k.toString(10)>p.toString(10)){
                k = null;
            }
        }
        return k
    }
}