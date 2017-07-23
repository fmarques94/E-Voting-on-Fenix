var BOOTH = null;

function getCredentials(){
    credentials = {}
    credentials["secret"] = $('#ballotBoxForm textarea[name=secret]').val();
    credentials["public"] = $('#ballotBoxForm textarea[name=public]').val();

    BOOTH = new Booth(pk,cryptoParameters,credentials,questionList,$('#ballotBoxForm'))
    $('#ballotBoxForm').attr("action","javascript:BOOTH.nextQuestion();")
    BOOTH.nextQuestion();

}