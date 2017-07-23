function Booth(electionPublicKey,cryptoParameters,secretCredential,questionList,boothForm){
    this.electionPublicKey = new BigInteger(electionPublicKey,16);
    this.p = new BigInteger(cryptoParameters['p'],10);
    this.g = new BigInteger(cryptoParameters['g'],10);
    this.q = new BigInteger(cryptoParameters['q'],10);
    this.secretCredential = new BigInteger(credentials["secret"],16);
    this.publicCredential = new BigInteger(credentials["public"],16);
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
            encAndSign();
        }
    }

    var saveAnswer = function(){
        vote = {"questionId":this.questionList[this.currentQuestion]["id"],"answers:":[]};
        answerIndex = $('input:radio[name=answer]:checked').val();
        vote['answerIndex'] = answerIndex;
        //only do the encryption at the end of the ballot. just save the dirty answer as is so that we can put a loading symbol.
        /*for(i=0;i<this.questionList[this.currentQuestion]["answers"].length;i++){
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
        }*/
        this.ballot["answerList"].append(vote);
    }

    var encAndSign = function(){
        hash = new BigInteger(1,10);
        for(i=0;i<this.ballot['answerList'].length;i++){
            questionData = this.ballot['answerList'][i];
            answerIndex = questionData['answerIndex'];
            for(j=0;j<this.questionList[i]["answers"].length;i++){
                encAnswers = {};
                if(i==answerIndex){
                    result = this.elGamal.encrypt(1);
                }else{
                    result = this.elGamal.encrypt(0);
                }
                encAnswers['alpha'] = result[0].toString(10);
                encAnswers['beta'] = result[1].toString(10);
                encAnswers['randomness'] = result[2].toString(10);
                questionData['answers'].append(encAnswers);
                hash = hash.multiply(result[0])
                hash = hash.multiply(result[1])
            }
        }
        hash = hash.mod(this.p);
        signature = this.schnorr.sign(hash);

        //This goes for when the cast is done.

        /*for(i=0;i<this.ballot["answerList"].length;i++){
            questionAnswer = this.ballot["answerList"][i]
            for(j=0;j<questionAnswer["answers"].length;j++){
                answer = questionAnswer["answers"][j]
                delete answer["randomness"];
            }
        }*/


        console.log(this.ballot);
    }
}