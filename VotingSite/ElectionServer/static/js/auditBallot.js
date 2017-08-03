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

        $('.results').append("<h4>Question Answers</h4>");
        for(var i=0;i<data.length;i++){
            $('.results').append("<p> Question: "+ data[i]["question"] +"</p>");
            $('.results').append("<p> Answer: "+ data[i]["answer"]+"</p>");
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
            }

            var param = {
            fn:this.checkProofs,
            args:[],
            context: auditor,
            importFiles: auditor.scriptFiles
            }

            vkthread.exec(param).then(function(data){

                $('.results').append("<h4>Proofs Check</h4>");
                //console.log("Here")
                if(data[0]){
                    $('.results').append("<p>Proofs check passed</p>");
                }else{
                    $('.results').append("<p>Proof check failed on "+data[1]+" proof of question: "+data[2]+"</p>");
                }

                var param = {
                fn:this.checkSignature,
                args:[],
                context: auditor,
                importFiles: auditor.scriptFiles
                }

                vkthread.exec(param).then(function(data){
                    
                });
            });

        });

    
    });
}

function checkAnswers(){
    data = []
    for(var i=0;i<this.ballot['answerList'].length;i++){
        data.push({'question':this.questionList[i]["question"],'answer':this.questionList[i]["answers"][this.ballot['answerList'][i]['answerIndex']]});
    }
    return data
}

function checkEncryption(){
    this.electionPublicKey = new BigInteger(this.pk,16);
    this.p = new BigInteger(this.cryptoParameters['p'],10);
    this.g = new BigInteger(this.cryptoParameters['g'],10);
    this.elGamal = new ElGamal(this.p,this.g,this.electionPublicKey);
    var data = []
    for(var i=0;i<this.ballot['answerList'].length;i++){
        var question = this.questionList[i];
        for(var j=0;j<this.questionList[i]["answers"].length;j++){
            if(j==this.ballot['answerList'][i]['answerIndex']){
                var result = this.elGamal.encrypt(1,this.ballot['answerList'][i]['answers'][j]["randomness"]);
            }else{
                var result = this.elGamal.encrypt(0,this.ballot['answerList'][i]['answers'][j]["randomness"]);
            }
            if(result[0].toString(10) != this.ballot['answerList'][i]['answers'][j]["alpha"] && result[0].toString(10) != this.ballot['answerList'][i]['answers'][j]["beta"]){
                return question['question']
            }
        }
    }
    return ""
}

function checkProofs(){
    this.p = new BigInteger(this.cryptoParameters['p'],10);
    this.g = new BigInteger(this.cryptoParameters['g'],10);
    for(var i=0;i<this.ballot['answerList'].length;i++){
        var answers = this.ballot['answerList'][i]['answers']
        for(var j=0;j<answers.length;j++){
            var individualProof = answers[j]["individualProof"];
            //console.log("Here2")
            //console.log(this.randomProofs[i]["individual_random"][j])
            //console.log(((new BigInteger(individualProof[0]["challenge"]).add(new BigInteger(individualProof[1]["challenge"]))).mod(this.p)).toString(10))
            if(this.randomProofs[i]["individual_random"][j] != (new BigInteger(individualProof[0]["challenge"]).add(new BigInteger(individualProof[1]["challenge"]))).mod(this.p).toString(10)){
                return [false,"individual",this.questionList[i]["question"]]
            }
        }
        var overallProof = this.ballot['answerList'][i]["overall_proof"];
        if(this.randomProofs[i]["overall_random"] != (new BigInteger(overallProof[0]["challenge"]).add(new BigInteger(overallProof[1]["challenge"]))).mod(this.p).toString(10)){
            return [false,"overall",this.questionList[i]["question"]]
        }
    }
    return [true]
}

function checkSignature(){
    
}