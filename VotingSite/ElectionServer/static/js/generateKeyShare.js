function generateKeyShare(cryptoParam,random,token){
    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }
    var param = {
        fn:function(cryptoParam,random){
            var p = new BigInteger(cryptoParam['p'],10);
            var g = new BigInteger(cryptoParam['g'],10);


            var elgamal = new ElGamal(
                p,
                g,
                null
            );

            var keys = elgamal.generate_key();

            x = new BigInteger(keys[1],16);
            h = new BigInteger(keys[0],10);
            e = new BigInteger(random,10);

            /*Calculate proof*/

            k = elgamal.generateNumberBelowP(p);
            r = g.modPow(k,p)
            s = k.add(x.multiply(e))

            return [h.toString(16),keys[1],r.toString(10),s.toString(10)]
        },
        args:[cryptoParam,random],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(data){
        payload = {
            "pk": data[0],
            "proof":{
                "r": data[2],
                "s": data[3]
            }
        }

        $.ajaxSetup({headers: { "X-CSRFToken": token }});
        console.log('Seding request now!');
        $.ajax({
        type: "POST",
        url: window.location.toString(),
        data: JSON.stringify(payload),
        success: function(msg){
            $('#generateKeyShareButton').remove();
            $('#keyShare').addClass("message");
            $('.message').append(
                "<p>Your private key share is:</p>"+
                "<p>"+data[1]+"</p>"+
                "<p><b>Please save this key until the end of the election process</b></p>"
            );
        },
        error: function(xhr, ajaxOptions, thrownError){
            if(xhr){
                alert('Oops: ' + xhr.responseJSON['error']);
            }else{
                alert('Oops: An unexpected error occurred. Please contact the administrators');
            }
        },
        dataType: "json",
        contentType : "application/json",
        });
    });

}