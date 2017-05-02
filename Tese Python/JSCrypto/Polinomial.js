function Polinomial(degree,p){
    
    this.p = p
    this.coeficients = []
    while(degree!=0){
        this.coeficients.push(generateNumber());
    }

    this.calculate = function(x){
        result = this.coeficients[0];
        for(i=1;i<this.coeficients.length;i++){
            result = result.multiply(this.coeficients[i].pow(new BigInteger(""+i,10)));
        }
        return result
    }

    var generateNumber = function(){
        k = null
        while(k==undefined){
            var array = new Uint32Array(32);
            window.crypto.getRandomValues(array);
            result = ""
            for(i=0;i<4;i++){
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