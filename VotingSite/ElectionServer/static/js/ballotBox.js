var BOOTH = null;

function getCredentials(){
    credentials = {}
    credentials["secret"] = $('#ballotBoxForm textarea[name=secret]').val();
    credentials["public"] = $('#ballotBoxForm textarea[name=public]').val();

    //var p = new BigInteger(cryptoParameters['p'],10);
    //var g = new BigInteger(cryptoParameters['g'],10);

    //var elgamal = new ElGamal(p,g,null);
    //console.log(elgamal.generateNumberBelowP(p));


    //ar myWorker = 

    //test(window.crypto.getRandomValues);

    BOOTH = new Booth(pk,cryptoParameters,credentials,questionList,$('#ballotBoxForm'),randoms)
    $('#ballotBoxForm').attr("action","javascript:BOOTH.nextQuestion();")
    BOOTH.nextQuestion();

}