//passar isto para outra thread.

function partialDecrypt(token,currentUrl,redirectUrl){
    $('.submitButton').css("display", "none");
    $('.loader').css("display", "block");

    var privKeyValue =$('#partialDecryptForm textarea[name=secret]').val();
    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }
    var param = {
        fn:function(aggregatedEncTally,privKeyValue,pValue,gValue,randoms){
            var privKey = new BigInteger(privKeyValue,16);
            var p = new BigInteger(pValue,10);
            var g = new BigInteger(gValue,10);
            var partialDecryption = {}
            for(var i=0;i<Object.keys(aggregatedEncTally).length;i++){
                var questionId = Object.keys(aggregatedEncTally)[i]
                partialDecryption[questionId] = {}
                for(var j=0;j<Object.keys(aggregatedEncTally[questionId]).length;j++){
                    var answerId = Object.keys(aggregatedEncTally[questionId])[j];
                    alpha = new BigInteger(aggregatedEncTally[questionId][answerId]["alpha"],10);
                    var k = null
                    while(k==null){
                        var array = new Uint32Array(32);
                        self.crypto.getRandomValues(array);
                        var result = ""
                        for(var n=0;n<32;n++){
                            result = result + array[n].toString();
                        }
                        k = new BigInteger(result,10);
                        if((k.max(p)).equals(k)){
                            k = null;
                        }
                    }
                    e = new BigInteger(randoms[questionId][answerId],10)
                    partialDecryption[questionId][answerId] = {
                        "alpha": (((alpha.modPow(p.subtract(new BigInteger('2',10)),p)).modPow(privKey,p)).mod(p)).toString(10),
                        "decryptionFactor": alpha.modPow(privKey,p).toString(10),
                        "A": g.modPow(k,p).toString(10),
                        "B": alpha.modPow(k,p).toString(10),
                        "response": (k.add(privKey.multiply(e))).toString(10)
                    }
                }
            }
            return partialDecryption;
        },
        args:[aggregatedEncTally,privKeyValue,pValue,gValue,randoms],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(data){
        console.log(data);
        url = window.location.toString();
        requestUrl = url.replace(currentUrl, redirectUrl);

        $.ajaxSetup({headers: { "X-CSRFToken": token }});
        console.log('Seding request now!');
        $.ajax({
        type: "POST",
        url: requestUrl,
        data: JSON.stringify(data),
        success: function(msg){
            window.location.reload();},
        error: function(xhr, ajaxOptions, thrownError){
            if(xhr){
                alert('Oops: ' + xhr.responseJSON['error']);
                $('.submitButton').css("display", "block");
                $('.loader').css("display", "none");
            }else{
                alert('Oops: An unexpected error occurred. Please contact the administrators');
                $('.submitButton').css("display", "block");
                $('.loader').css("display", "none");
            }
        },
        dataType: "json",
        contentType : "application/json",
        });
    });
}