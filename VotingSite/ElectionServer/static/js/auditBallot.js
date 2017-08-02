function auditorVariable(electionPublicKey,cryptoParameters,ballot,questionList,randoms){
    this.pk = electionPublicKey;
    this.cryptoParameters = cryptoParameters;
    this.ballot = ballot;
    this.questionList = questionList["questionList"];
    this.randomProofs = randoms;
}

var auditor = null;

function audit(){
    ballot = JSON.parse($('#auditForm textarea[name=ballot]').val());
    auditor = new auditorVariable(pk,cryptoParameters,ballot,questionList,proofRandoms);
}

function checkAnswers(){

}

function checkEncryption(){

}

function checkSignatures(){
    
}