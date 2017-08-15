//passar isto para outra thread.

function partialDecrypt(token,currentUrl,redirectUrl){
    var privKeyValue =$('#partialDecryptForm textarea[name=secret]').val();
    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }
    var param = {
        fn:function(aggregatedEncTally,privKeyValue,pValue){
            var privKey = new BigInteger(privKeyValue,16);
            var p = new BigInteger(pValue,10);
            var partialDecryption = {}
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
            return partialDecryption;
        },
        args:[aggregatedEncTally,privKeyValue,pValue],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(data){
        console.log(data);
    });
}