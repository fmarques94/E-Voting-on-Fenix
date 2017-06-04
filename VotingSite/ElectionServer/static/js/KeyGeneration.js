

function generateKeyShare(token,p,g){
    var e = new ElGamal(new BigInteger(p,10),new BigInteger(g,10),null);
    var keys = e.generate_key();
    var data = JSON.stringify({'keyShare':keys[0]});
    $.ajaxSetup({
        headers: { "X-CSRFToken": token }
    });
    console.log('Going to send post request')
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: data,
        success: function(){
            console.log("Success");
            $(".main").prepend(
                '<div style="background-color:#99ff99; width:100%;text-align:center;word-wrap: break-word;">'+
                    '<p> Your public key share was inputed with success.</p>'+
                    '<p> Please save the following private key until the end of the election</p>'+
                    '<h3>'+keys[1]+'</h3>'+
                '</div>'
            );
            $(".createKeysButton").attr('disabled', 'disabled');
        },
        dataType: "json",
        contentType : "application/json"
        });

}