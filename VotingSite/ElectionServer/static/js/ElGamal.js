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
        var k = this.generateNumberBelowP(this.p);
        var c1 = this.g.modPow(k,p)
        var value = new BigInteger(encrypt.toString(),10)
        var c2 = ((this.h.modPow(k,this.p)).multiply(this.g.modPow(value,this.p))).mod(this.p)
        return [c1,c2,k]
    }

    this.generateNumberBelowP = function(p){
        var k = null
        while(k==undefined){
            var array = new Uint32Array(32);
            window.crypto.getRandomValues(array);
            var result = ""
            for(var i=0;i<32;i++){
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