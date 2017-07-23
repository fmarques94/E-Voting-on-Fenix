function Booth(electionPublicKey,cryptoParameters,credentials,questionList,boothForm){
    this.electionPublicKey = new BigInteger(electionPublicKey,16);
    this.p = new BigInteger(cryptoParameters['p'],10);
    this.g = new BigInteger(cryptoParameters['g'],10);
    this.q = new BigInteger(cryptoParameters['q'],10);
    this.secretCredential = new BigInteger(credentials["secret"],10);
    this.publicCredential = new BigInteger(credentials["public"],10);
    this.questionList = questionList["questionList"];
    this.currentQuestion = 0;
    this.boothForm = boothForm;
    this.elGamal = new ElGamal(this.p,this.g,this.electionPublicKey);
    this.schnorr = new Schnorr(this.p,this.q,this.g,this.secretCredential);
    this.ballot = {"answerList":[]}

    //<input type="radio" name="castTimeRadioButton" onclick="enableCastTimes()" value="true" checked>Yes

    this.nextQuestion = function(){
        if(this.currentQuestion>0){
            this.saveAnswer();
        }
        if(this.currentQuestion<this.questionList.length){
            var question = this.questionList[this.currentQuestion];
            htmlCode = "<fieldset><legend><h3>"+question["question"]+"</h3></legend>";
            for(i=0;i<question["answers"].length;i++){
                htmlCode = htmlCode + "<input type=\"radio\" name=\"answer\" value=\""+i+"\">"+question["answers"][i]+"<br>";
            }
            htmlCode = htmlCode+"<input type=\"submit\" class=\"submitButton\" value=\"Next\"></fieldset>";
            this.boothForm.html(htmlCode);
            this.currentQuestion++;
        }else{
            this.encAndSign();
        }
    }

    this.saveAnswer = function(){
        console.log(this.currentQuestion)
        vote = {"questionId":this.questionList[this.currentQuestion-1]["id"],"answers":[]};
        answerIndex = $('input:radio[name=answer]:checked').val();
        vote['answerIndex'] = parseInt(answerIndex);
        this.ballot["answerList"].push(vote);
    }

    this.encAndSign = function(){
        hash = new BigInteger(1,10);
        for(var i=0;i<this.ballot['answerList'].length;i++){
            var questionData = this.ballot['answerList'][i];
            var answerIndex = questionData['answerIndex'];
            console.log(i)
            console.log(this.questionList[i])
            for(var j=0;j<this.questionList[i]["answers"].length;j++){
                console.log(this.questionList[i])
                encAnswers = {};
                if(j==answerIndex){
                    result = this.elGamal.encrypt(1);
                }else{
                    result = this.elGamal.encrypt(0);
                }
                
                encAnswers['alpha'] = result[0].toString(10);
                encAnswers['beta'] = result[1].toString(10);
                encAnswers['randomness'] = result[2].toString(10);
                console.log(questionData)
                console.log(questionData["answers"])
                questionData['answers'].push(encAnswers);
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