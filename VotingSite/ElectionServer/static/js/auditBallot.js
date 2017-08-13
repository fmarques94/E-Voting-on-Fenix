function auditorVariable(electionPublicKey,cryptoParameters,ballot,questionList,randoms,scriptFiles){
    this.pk = electionPublicKey;
    this.cryptoParameters = cryptoParameters;
    this.ballot = ballot;
    this.questionList = questionList["questionList"];
    this.randomProofs = randoms['randomLists'];
    this.scriptFiles = scriptFiles;
}

var auditor = null;

function audit(){
    ballot = JSON.parse($('#auditForm textarea[name=ballot]').val());
    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }
    auditor = new auditorVariable(pk,cryptoParameters,ballot,questionList,proofRandoms,scriptFiles);

    $('.results').append("<h3>Audit Results</h3>");

    var param = {
        fn:this.checkAnswers,
        args:[],
        context: auditor,
        importFiles: auditor.scriptFiles
    }

    vkthread.exec(param).then(function(data){
        
        $('.results').append("<h4>Ballot Formation</h4>");
        console.log(data[1].length);
        if(data[0]){
            for(var i=0;i<(data[1]).length;i++){
                $('.results').append("<p> Question: "+ data[1][i]["question"] +"</p>");
                $('.results').append("<p> Answer: "+ data[1][i]["answer"]+"</p>");
            }
        }else{
            $('.results').append("<p> Ballot is not well formed.</p>");
            return;
        }

        var param = {
        fn:this.checkEncryption,
        args:[],
        context: auditor,
        importFiles: auditor.scriptFiles
        }
        
        vkthread.exec(param).then(function(data){

            $('.results').append("<h4>Encryption Check</h4>");

            if(data==""){
                $('.results').append("<p>Encryption check passed</p>");
            }else{
                $('.results').append("<p>Encryption check failed on question: "+data+"</p>");
                return;
            }

            var param = {
            fn:this.checkProofs,
            args:[],
            context: auditor,
            importFiles: auditor.scriptFiles
            }

            vkthread.exec(param).then(function(data){

                $('.results').append("<h4>Proofs Check</h4>");
                if(data[0]){
                    $('.results').append("<p>Proofs check passed</p>");
                }else{
                    $('.results').append("<p>Proof check failed on "+data[1]+" proof of question: "+data[2]+"</p>");
                    return;
                }

                var param = {
                fn:this.checkSignature,
                args:[],
                context: auditor,
                importFiles: auditor.scriptFiles
                }

                vkthread.exec(param).then(function(data){
                    $('.results').append("<h4>Signature Check</h4>");
                    if(data){
                        $('.results').append("<p>Signature check passed</p>");
                    }else{
                        $('.results').append("<p>Signature check failed</p>");
                        return;
                    }
                });
            });

        });

    
    });
}

function checkAnswers(){
    data = []
    data.push(true);
    ballotAnswers = [];
    for(var i=0;i<this.questionList.length;i++){
        if(this.questionList[i]["id"] in this.ballot){
            for(var j=0;j<this.questionList[i]["answers"].length;j++){
                if(this.questionList[i]["answers"][j]["id"] in this.ballot[this.questionList[i]["id"]]["answers"]){
                    if(j==this.ballot[this.questionList[i]["id"]]["answer"]){
                        ballotAnswers.push({
                            "question":this.questionList[i]["question"],
                            "answer":this.questionList[i]["answers"][j]["answer"]
                        })
                    }
                }else{
                    data[0] = false;
                    return data;
                }
            }
        }else{
            data[0] = false;
            return data;
        }
    }
    data.push(ballotAnswers);
    return data
}

function checkEncryption(){
    this.electionPublicKey = new BigInteger(this.pk,16);
    this.p = new BigInteger(this.cryptoParameters['p'],10);
    this.g = new BigInteger(this.cryptoParameters['g'],10);
    this.elGamal = new ElGamal(this.p,this.g,this.electionPublicKey);
    var data = []
    for(var i=0;i<this.questionList.length;i++){
        var questionId = this.questionList[i]["id"];
        for(var j=0;j<this.questionList[i]["answers"].length;j++){
            var answerId = this.questionList[i]["answers"][j]["id"]
            var answerData = this.ballot[questionId]["answers"][answerId];
            if(j == this.ballot[questionId]["answer"]){
                var result = this.elGamal.encrypt(1,answerData["randomness"]);
            }else{
                var result = this.elGamal.encrypt(0,answerData["randomness"]);
            }
            console.log(result[0].toString(10))
            if(result[0].toString(10) != answerData["alpha"] && result[1].toString(10) != answerData["beta"]){
                return this.questionList[i]["question"]
            }
        }
    }

    return ""
}

function checkProofs(){
    this.p = new BigInteger(this.cryptoParameters['p'],10);
    this.g = new BigInteger(this.cryptoParameters['g'],10);
    this.electionPublicKey = new BigInteger(this.pk,16);

    for(var i=0;i<this.questionList.length;i++){
        var questionId = this.questionList[i]["id"];
        var totalAlpha = new BigInteger('1',10);
        var totalBeta = new BigInteger('1',10);
        for(var j=0;j<this.questionList[i]["answers"].length;j++){
            var answerId = this.questionList[i]["answers"][j]["id"];
            var answerData = this.ballot[questionId]["answers"][answerId];
            var alpha = new BigInteger(answerData["alpha"],10);
            var beta = new BigInteger(answerData["beta"],10);
            totalAlpha = totalAlpha.multiply(alpha)
            totalBeta = totalBeta.multiply(beta)
            var individualProof = answerData["individualProof"];
            if(this.randomProofs[i]["individual_random"][j] != (new BigInteger(individualProof[0]["challenge"],10).add(new BigInteger(individualProof[1]["challenge"],10))).mod(this.p).toString(10)){
                return [false,"individual",this.questionList[i]["question"]]
            }
            for(var n=0;n<individualProof.length;n++){
                var challenge = new BigInteger(individualProof[n]["challenge"],10)
                var response = new BigInteger(individualProof[n]["response"],10)
                var A = (this.g.modPow(response,this.p).multiply((alpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge,this.p))).mod(this.p)
                var B = ((this.electionPublicKey.modPow(response,this.p).multiply((beta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge,this.p))).multiply(this.g.modPow(challenge.multiply(new BigInteger(parseInt(n),10)),this.p))).mod(this.p);
                if(A.toString(10) != individualProof[n]["A"] && B.toString(10) != individualProof[n]["B"]){
                    return [false,"individual",this.questionList[i]["question"]]
                }
            }
        }

        var overallProof = this.ballot[questionId]["overall_proof"];
        if(this.randomProofs[i]["overall_random"] != (new BigInteger(overallProof[0]["challenge"],10).add(new BigInteger(overallProof[1]["challenge"],10))).mod(this.p).toString(10)){
            return [false,"overall",this.questionList[i]["question"]]
        }
        for(var n=0;n<overallProof.length;n++){
            var challenge = new BigInteger(overallProof[n]["challenge"],10)
            var response = new BigInteger(overallProof[n]["response"],10)
            var A = (this.g.modPow(response,this.p).multiply((totalAlpha.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge,this.p))).mod(this.p)
            var B = ((this.electionPublicKey.modPow(response,this.p).multiply((totalBeta.modPow(this.p.subtract(new BigInteger('2',10)),this.p)).modPow(challenge,this.p))).multiply(this.g.modPow(challenge.multiply(new BigInteger(parseInt(n),10)),this.p))).mod(this.p);
            if(A.toString(10) != overallProof[n]["A"] && B.toString(10) != overallProof[n]["B"]){
                return [false,"overal",this.questionList[i]["question"]]
            }
        }
    }
    return [true]
}

function checkSignature(){
    this.p = new BigInteger(this.cryptoParameters['p'],10);
    this.g = new BigInteger(this.cryptoParameters['g'],10);
    this.q = new BigInteger(this.cryptoParameters['q'],10);
    var publicCredential = new BigInteger(this.ballot["publicCredential"],10)
    var signature = this.ballot["signature"]
    this.schnorr = new Schnorr(this.p,this.q,this.g,null);
    var hash = new BigInteger('1',10);
    
    for(var i=0;i<this.questionList.length;i++){
        var questionId = this.questionList[i]["id"];
        for(var j=0;j<this.questionList[i]["answers"].length;j++){
            var answerId = this.questionList[i]["answers"][j]["id"];
            var answerData = this.ballot[questionId]["answers"][answerId];
            var alpha = new BigInteger(answerData["alpha"],10);
            var beta = new BigInteger(answerData["beta"],10);
            hash = hash.multiply(alpha);
            hash = hash.multiply(beta);
        }
    }
    hash = hash.mod(this.p)
    return this.schnorr.verify(hash,signature,publicCredential);
}