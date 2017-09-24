function Booth(electionPublicKey,cryptoParameters,credentials,questionList,boothForm,randoms){
    this.pk = electionPublicKey;
    this.cryptoParameters = cryptoParameters;
    this.credentials = credentials;
    this.questionList = questionList["questionList"];
    this.currentQuestion = 0;
    this.boothForm = boothForm;
    this.ballot = {}
    this.ballotToSend = {}
    this.randoms = randoms

    //<input type="radio" name="castTimeRadioButton" onclick="enableCastTimes()" value="true" checked>Yes

    this.nextQuestion = function(){
        if(this.currentQuestion>0){
            this.saveAnswer();
        }
        if(this.currentQuestion<this.questionList.length){
            var question = this.questionList[this.currentQuestion];
            htmlCode = "<fieldset><legend><h3>"+question["question"]+"</h3></legend>";
            for(i=0;i<question["answers"].length;i++){
                htmlCode = htmlCode + "<input type=\"radio\" name=\"answer\" value=\""+i+"\" required>"+question["answers"][i]["answer"]+"<br>";
            }
            htmlCode = htmlCode+"<input type=\"submit\" class=\"submitButton\" value=\"Next\"></fieldset>";
            this.boothForm.html(htmlCode);
            this.currentQuestion++;
        }else{
            this.boothForm.html("<div class=\"bar\"></div><p>Sealing the ballot. This might take some time.</p>");
            var scriptFiles = []
            var scripts = document.getElementsByClassName("import")
            for(var i = 0; i<scripts.length;i++){
                scriptFiles.push(scripts[i].src);
            }
            var param = {
                fn:this.encAndSign,
                args:[],
                context: this,
                importFiles: scriptFiles
            }
            vkthread.exec(param).then(function(data){
                BOOTH.ballot = data[0];
                BOOTH.ballotToSend = data[1];
                BOOTH.boothForm.attr("action","javascript:BOOTH.castBallot();");
                BOOTH.boothForm.html("<p>Your smart ballot tracker is</p>"+
                "<p><b>"+data[2]+"</b></p>"+
                "<p>Save this value in order to verify your ballot on the bulletin board.</p>"+
                "<p>If you wish to audit the ballot you may do so but you will need to do a new ballot after.</p>"+
                "<input type=\"submit\" class=\"submitButton\" value=\"Cast Ballot\">"+
                "<a class=\"submitButton\" target=\"_blank\" href=\"javascript:BOOTH.audit()\">Audit Ballot</a>");
            });
            //this.encAndSign();
        }
    }

    this.audit = function(){
        BOOTH.boothForm.attr("action","");
        BOOTH.boothForm.html(
            "<p>To audit the ballot, copy it from bellow and go to the <a href=\""+auditor+"\">ballot auditor</a>.</p>"+
            "There you just need to paste the ballot and click the audit button."+
            "<textarea rows=\"20\" style=\"width:100%\">"+JSON.stringify(this.ballot)+"</textarea>"
        );
    }

    this.castBallot = function(){
        this.boothForm.html("<div class=\"bar\"></div><p>Casting the ballot. This might take some time.</p>");
        $.ajaxSetup({headers: { "X-CSRFToken": token }});
        console.log('Seding request now!');
        $.ajax({
        type: "POST",
        url: window.location.href,
        data: JSON.stringify(BOOTH.ballotToSend),
        success: function(msg){
            BOOTH.boothForm.html("<fieldset><p>Ballot successfully cast.</p></fieldset>")},
        error: function(xhr, ajaxOptions, thrownError){
            if(xhr){
                alert('Oops: ' + xhr.responseJSON['error']);
            }else{
                alert('Oops: An unexpected error occurred. Please contact the administrators');
            }
            BOOTH.boothForm.html("<input type=\"submit\" class=\"submitButton\" value=\"Cast Ballot\">")
        },
        dataType: "json",
        contentType : "application/json",
        });
    }

    this.saveAnswer = function(){
        var answerIndex = $('input:radio[name=answer]:checked').val();
        this.ballot[this.questionList[this.currentQuestion-1]["id"]] = {}
        this.ballotToSend[this.questionList[this.currentQuestion-1]["id"]] = {}
        this.ballot[this.questionList[this.currentQuestion-1]["id"]]["answer"] = parseInt(answerIndex);
    }

    this.encAndSign = function(){
        this.electionPublicKey = new BigInteger(this.pk,16);
        this.p = new BigInteger(this.cryptoParameters['p'],10);
        this.g = new BigInteger(this.cryptoParameters['g'],10);
        this.q = new BigInteger(this.cryptoParameters['q'],10);
        this.secretCredential = new BigInteger(this.credentials["secret"],10);
        this.publicCredential = new BigInteger(this.credentials["public"],10);
        this.elGamal = new ElGamal(this.p,this.g,this.electionPublicKey);
        this.schnorr = new Schnorr(this.p,this.q,this.g,this.secretCredential);
        hash = new BigInteger(1,10);
        for(var i=0;i<Object.keys(this.ballot).length;i++){
            var answerIndex = this.ballot[Object.keys(this.ballot)[i]]["answer"];
            var currentQuestion = this.questionList[i]
            var alpha = new BigInteger('1',10);
            var beta = new BigInteger('1',10);
            var random = new BigInteger('0',10);
            var encAnswers = {}
			var encAnswersClone = {};
            for(var j=0;j<currentQuestion["answers"].length;j++){
                encAnswers[currentQuestion["answers"][j]["id"]] = {}
				encAnswersClone[currentQuestion["answers"][j]["id"]] = {}
                if(j==answerIndex){
                    result = this.elGamal.encrypt(1);
                    var message = 1;
                }else{
                    result = this.elGamal.encrypt(0);
                    var message = 0;
                }
                encAnswers[currentQuestion["answers"][j]["id"]]['alpha'] = result[0].toString(10);
				encAnswersClone[currentQuestion["answers"][j]["id"]]['alpha'] = result[0].toString(10);
                encAnswers[currentQuestion["answers"][j]["id"]]['beta'] = result[1].toString(10);
				encAnswersClone[currentQuestion["answers"][j]["id"]]['beta'] = result[1].toString(10);
                encAnswers[currentQuestion["answers"][j]["id"]]['randomness'] = result[2].toString(10);
                var randomNumber = new BigInteger(this.randoms[currentQuestion["id"]][currentQuestion["answers"][j]["id"]],10)
				var proof = this.generateProof(message,result,randomNumber);
                encAnswers[currentQuestion["answers"][j]["id"]]['individualProof'] = proof;
				encAnswersClone[currentQuestion["answers"][j]["id"]]['individualProof'] = proof;
                hash = hash.multiply(result[0])
                hash = hash.multiply(result[1])
                alpha = alpha.multiply(result[0]);
                beta = beta.multiply(result[1]);
                random = random.add(result[2]);
            }
            this.ballot[Object.keys(this.ballot)[i]]["answers"] = encAnswers;
            this.ballotToSend[Object.keys(this.ballot)[i]]["answers"] = encAnswersClone;
            var overall_random = new BigInteger(this.randoms[currentQuestion["id"]]["overall"],10)
            var proof = this.generateProof(1,[alpha,beta,random],overall_random)
            this.ballot[Object.keys(this.ballot)[i]]["overall_proof"] = proof;
            this.ballotToSend[Object.keys(this.ballot)[i]]['overall_proof'] = proof;
        }
        hash = hash.mod(this.p);
        this.ballot["signature"] = []
        signature = this.schnorr.sign(hash);
        this.ballot["signature"].push(signature[0].toString(10))
        this.ballot["signature"].push(signature[1].toString(10))
        this.ballot["publicCredential"] = this.publicCredential.toString(10);
        this.ballotToSend["signature"] = this.ballot["signature"] 
        var payload = {'ballot':this.ballotToSend,'publicCredential':this.credentials["public"]}
        
        return [this.ballot,payload,sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(JSON.stringify(payload)))];        
    }

    this.generateProof = function(message,result,e){
        var proof = []
        var alpha = result[0]
        var beta = result[1]
        var r = result[2]
        if(message == 0){
            var challenge1 = this.elGamal.generateNumberBelowP();
            var response1 = this.elGamal.generateNumberBelowP();  
            var A1 = (this.g.modPow(response1,this.p).multiply((alpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge1,this.p))).mod(this.p)
            var B1 = ((this.electionPublicKey.modPow(response1,this.p).multiply((beta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge1,this.p))).multiply(this.g.modPow(challenge1.multiply(new BigInteger('1',10)),this.p))).mod(this.p)
            var w = this.elGamal.generateNumberBelowP();
            var A0 = this.g.modPow(w,this.p);
            var B0 = this.electionPublicKey.modPow(w,this.p);
            var challenge0 = (e.subtract(challenge1)).mod(this.p);
            var response0 = w.add(r.multiply(challenge0));
        }else{
            var challenge0 = this.elGamal.generateNumberBelowP();
            var response0 = this.elGamal.generateNumberBelowP();  
            var A0 = (this.g.modPow(response0,this.p).multiply((alpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge0,this.p))).mod(this.p)
            var B0 = ((this.electionPublicKey.modPow(response0,this.p).multiply((beta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge0,this.p))).multiply(this.g.modPow(challenge0.multiply(new BigInteger('0',10)),this.p))).mod(this.p)
            var w = this.elGamal.generateNumberBelowP();
            var A1 = this.g.modPow(w,this.p);
            var B1 = this.electionPublicKey.modPow(w,this.p);
            var challenge1 = (e.subtract(challenge0)).mod(this.p);
            var response1 = w.add(r.multiply(challenge1));
        }

        proof.push({
            "challenge":challenge0.toString(10),
            "A":A0.toString(10),
            "B":B0.toString(10),
            "response":response0.toString(10)
        });
        proof.push({
            "challenge":challenge1.toString(10),
            "A":A1.toString(10),
            "B":B1.toString(10),
            "response":response1.toString(10)
        });

        return proof;
    }
}