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
                    var message = 1;
                }else{
                    result = this.elGamal.encrypt(0);
                    var message = 0;
                }
                
                encAnswers['alpha'] = result[0].toString(10);
                encAnswers['beta'] = result[1].toString(10);
                encAnswers['randomness'] = result[2].toString(10);
                encAnswers['individualProof'] = this.generateProof(message,result);
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

    this.generateProof = function(message,result,e){
        var proof = []
        var alpha = result[0]
        var beta = result[1]
        var r = result[2]
        if(message == 0){
            var challenge1 = this.elGamal.generateNumberBelowP(this.p);
            var response1 = this.elGamal.generateNumberBelowP(this.p);  
            var A1 = (this.g.modPow(response1,this.p).multiply((alpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge1,this.p))).mod(this.p)
            var B1 = ((this.electionPublicKey.modPow(response1,this.p).multiply((beta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge1,this.p))).multiply(this.g.modPow(challenge1.multiply(new BigInteger('1',10)),this.p))).mod(this.p)
            var w = this.elGamal.generateNumberBelowP(this.p);
            var A0 = this.g.modPow(w,this.p);
            var B0 = this.electionPublicKey.modPow(w,this.p);
            var challenge0 = (e.subtract(challenge1)).mod(this.p);
            var response0 = w.add(r.multiply(challenge0));
        }else{
            var challenge0 = this.elGamal.generateNumberBelowP(this.p);
            var response0 = this.elGamal.generateNumberBelowP(this.p);  
            var A0 = (this.g.modPow(response0,this.p).multiply((alpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge0,this.p))).mod(this.p)
            var B0 = ((this.electionPublicKey.modPow(response0,this.p).multiply((beta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge0,this.p))).multiply(this.g.modPow(challenge0.multiply(new BigInteger('0',10)),this.p))).mod(this.p)
            var w = this.elGamal.generateNumberBelowP(this.p);
            var A1 = this.g.modPow(w,this.p);
            var B1 = this.electionPublicKey.modPow(w,this.p);
            var challenge1 = (e.subtract(challenge0)).mod(this.p);
            var response1 = w.add(r.multiply(challenge1));
        }

        proof.push({
            "challenge":challenge0,
            "A":A0,
            "B":B0,
            "response":response0
        });
        proof.push({
            "challenge":challenge1,
            "A":A1,
            "B":B1,
            "response":response1
        });
    }
}