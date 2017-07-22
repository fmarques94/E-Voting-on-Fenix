function Booth(electionPublicKey,cryptoParameters,secretCredential,questionList,boothForm){
    this.electionPublicKey = new BigInteger(electionPublicKey,16);
    this.p = new BigInteger(cryptoParameters['p'],10);
    this.g = new BigInteger(cryptoParameters['g'],10);
    this.q = new BigInteger(cryptoParameters['q'],10);
    this.secretCredential = new BigInteger(secretCredential,16);
    this.questionList = questionList;
    this.currentQuestion = 0;
    this.boothForm = boothForm;
    this.elGamal = new ElGamal(this.p,this.g,this.electionPublicKey);
    this.schnorr = new Schnorr(this.p,this.q,this.g,this.secretCredential);
    this.ballot = {"answerList":[]}

    

    this.nextQuestion = function(){
        if(this.currentQuestion>0){
            saveAnswer();
        }
        if(this.currentQuestion<this.questionList.length){
            this.boothForm.html("");
        }else{
            signAndSend();
        }
    }

    var saveAnswer = function(){
        vote = {"questionId":this.questionList[this.currentQuestion]["id"],"answers:":[]};
        answerIndex = $('input:radio[name=answer]:checked').val();
        vote['answerIndex'] = answerIndex;
        for(i=0;i<this.questionList[this.currentQuestion]["answers"].length;i++){
            encAnswers = {};
            if(i==answerIndex){
                result = this.elGamal.encrypt(1);
            }else{
                result = this.elGamal.encrypt(0);
            }
            encAnswers['alpha'] = result[0].toString(10);
            encAnswers['beta'] = result[1].toString(10);
            encAnswers['randomness'] = result[2].toString(10);
            vote['answers'].append(encAnswers);
        }
        this.ballot["answerList"].append(vote);
    }

    var signAndSend = function(){
        hash = new BigInteger(1,10);
        for(i=0;i<this.ballot["answerList"].length;i++){
            questionAnswer = this.ballot["answerList"][i]
            for(j=0;j<questionAnswer["answers"].length;j++){
                answer = questionAnswer["answers"][j]
                hash = hash.multiply(new BigInteger(answer["alpha"],10));
                hash = hash.multiply(new BigInteger(answer["beta"],10));
            }
        }
        hash = hash.mod(this.p);
    }
}