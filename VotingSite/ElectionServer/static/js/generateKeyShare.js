function generateKeyShare(cryptoParam,publicKeyShare,token){

    p = new BigInteger(cryptoParam['p'],10);
    g = new BigInteger(cryptoParam['g'],10);


    elgamal = new ElGamal(
        p,
        g,
        null
    );

    keys = elgamal.generate_key();


    payload = {"pk":keys[0]}

    x = new BigInteger(keys[1],16);
    h = new BigInteger(keys[0],10);
    e = new BigInteger(publicKeyShare["random"],10);

    /*Calculate proof*/

    k = elgamal.generateNumberBelowP(p);
    r = g.modPow(k,p)
    s = k.add(x.multiply(e))

    //Isto é para mover para a zona de verificação da prova.
    //aux = (
    //    g.modPow(s,p).multiply(
    //        (h.modPow(p.subtract(new BigInteger('2',10)),p)).modPow(e,p)
    //    )
    //).mod(p)

    //console.log(aux.toString(10)==r.toString(10))

    payload = {
        "pk": h.toString(16),
        "proof":{
            "e": publicKeyShare["random"],
            "r": r.toString(10),
            "s": s.toString(10)
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
               "<p>"+keys[1]+"</p>"+
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

}