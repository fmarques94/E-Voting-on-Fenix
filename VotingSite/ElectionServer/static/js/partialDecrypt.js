var partialDecryption = {}


//passar isto para outra thread.
function partialDecrypt(token,currentUrl,redirectUrl){
    var privKey = new BigInteger($('#partialDecryptForm textarea[name=secret]').val(),16);
    for(var i=0;i<Object.keys(aggregatedEncTally).length;i++){
        var questionId = Object.keys(aggregatedEncTally)[i]
        partialDecryption[questionId] = {}
        for(var j=0;j<Object.keys(aggregatedEncTally[questionId]).length;j++){
            var answerId = Object.keys(aggregatedEncTally[questionId])[j];
            console.log(aggregatedEncTally[questionId])
            console.log(answerId)
            alpha = new BigInteger(aggregatedEncTally[questionId][answerId]["alpha"],10);
            partialDecryption[questionId][answerId] = {
                "alpha": ((alpha.modPow(p.subtract(new BigInteger('2',10)),p)).modPow(privKey,p)).toString(10)
            }
        }
    }
}