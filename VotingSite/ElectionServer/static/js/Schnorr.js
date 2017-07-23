function Schnorr(p,q,g,a){
    this.p = p
    this.q = q
    this.g = g
    this.a = a

    this.sign = function(value){
        var value = new BigInteger(value.toString(10),10);
        var k = generateNumber()
        var aux = this.g.modPow(k,this.p)
        var s1 = new BigInteger(sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(value.toString(10)+aux.toString(10))),16);
        s2 = ((this.a.multiply(s1)).add(k)).mod(this.q)
        return [s1,s2]
    }

    var generateNumber = function(){
        k = null
        while(k==undefined){
            var array = new Uint32Array(4);
            window.crypto.getRandomValues(array);
            result = ""
            for(i=0;i<4;i++){
                result = result + array[i].toString();
            }
            k = new BigInteger(result,10);
            if(k.toString(10)>q.toString(10)){
                k = null;
            }
        }
        return k
    }
}