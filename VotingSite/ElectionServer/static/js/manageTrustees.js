function toggleTrusteeList(){
    $(".TrusteeList").toggle();
    if($(".TrusteeList").is(':hidden')){
        $("#toggleButton").text('Show Trustee List')
    }else{
        $("#toggleButton").text('Hide Trustee List')
    }
}

function removeTrustee(token,currentUrl,redirectUrl,trusteeId){
    payload={
        "trusteeList":[trusteeId]
    };

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');
    $.ajax({
    type: "POST",
    url: requestUrl,
    data: JSON.stringify(payload),
    success: function(msg){
        window.location.reload();},
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
}

function submit(token,currentUrl,redirectUrl){
    payload={
        "trusteeList":[]
    };

    trusteeData = {}
    trusteeData['id'] = $('#addTrusteeForm input:text[name=identifier]').val();
    trusteeData['name'] = $('#addTrusteeForm input:text[name=name]').val()
    trusteeData['email'] = $('#addTrusteeForm input[type=email][name=email]').val()

    payload['trusteeList'].push(trusteeData);

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');
    $.ajax({
    type: "POST",
    url: requestUrl,
    data: JSON.stringify(payload),
    success: function(msg){
        window.location.reload();},
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
}

function aggregateKey(token,keyShares,cryptoParameters,currentUrl,redirectUrl){

    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }
    var param = {
        fn:function(cryptoParameters,keyShares){
            var electionPublicKey = new BigInteger('1',10);
            var p = new BigInteger(cryptoParameters['p'],10);
            var g = new BigInteger(cryptoParameters['g'],10);
            for(i=0;i<Object.keys(keyShares).length;i++){
                var share = keyShares[Object.keys(keyShares)[i]]
                var h = new BigInteger(share['pk'],16)
                var e = new BigInteger(share['proof']['e'],10)
                var s = new BigInteger(share['proof']['s'],10)

                var aux = (
                    g.modPow(s,p).multiply(
                        (h.modPow(p.subtract(new BigInteger('2',10)),p)).modPow(e,p)
                    )
                ).mod(p)

                if(aux.toString(10)==share['proof']['r']){
                    electionPublicKey = electionPublicKey.multiply(h);
                }else{ 
                    return [false,Object.keys(keyShares)[i]];
                }
            }
            return [true,electionPublicKey.toString(16)]
        },
        args:[cryptoParameters,keyShares],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(data){
        if(data[0]){
            var url = window.location.toString();
            var requestUrl = url.replace(currentUrl, redirectUrl);

            $.ajaxSetup({headers: { "X-CSRFToken": token }});
            console.log('Seding request now!');
            $.ajax({
            type: "POST",
            url: requestUrl,
            data: JSON.stringify({"pk":data[1]}),
            success: function(msg){
                window.location.reload();},
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
        }else{
            alert('Oops: The proof of trustee ' + data[1] + 'failed. Aborting...');
        }
    });

}

function convertKey(key){
    console.log("Test")
    $('#message').text("The election public key is" + (new BigInteger(key,10)).toString(16));
}