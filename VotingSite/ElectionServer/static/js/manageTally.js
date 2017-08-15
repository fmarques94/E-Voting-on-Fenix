var currentQuestion=0;
var paperResults = {}

function addPaperResuls(){
    $('.manageTallyContent').html(

        "<form class=\"PaperResultsForm\" action=\"javascript:nextQuestion()\">"+
        "</form>"
    );
    showNextQuestion();
}

function nextQuestion(){
    saveResults();
    currentQuestion++;
    if(currentQuestion<questionList['questionList'].length){
        showNextQuestion();
    }else{
        sendPaperResults();
    }
}

function saveResults(){
    var question = questionList['questionList'][currentQuestion];
    paperResults[question["id"]] = {};
    var inputs = $('input:text');
    for(var i=0;i<question["answers"].length;i++){
        paperResults[question["id"]][question["answers"][i]["id"]] = inputs[i].value;
    }
}

function showNextQuestion(){
    var question = questionList['questionList'][currentQuestion];
    var htmlCode = "<fieldset><legend><h3>Paper Results</h3></legend>"+
        "<p>"+question["question"]+"</p>"+
        "<table>";
    for(var i=0;i<question["answers"].length;i++){
        htmlCode = htmlCode + "<tr><td>"+question["answers"][i]["answer"]+"</td>"+
            "<td><input type=\"text\" autocomplete=\"off\" pattern=\"[0-9]+\" required></td>";
    }
    htmlCode = htmlCode + "</table><input class=\"button\" type=\"submit\" value=\"Next\">"
    $('.PaperResultsForm').html(htmlCode)
}

function sendPaperResults(){
    url = window.location.toString();
    requestUrl = url.replace(currentUrl, paperResultsUrl);
    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');
    $.ajax({
    type: "POST",
    url: requestUrl,
    data: JSON.stringify(paperResults),
    success: function(msg){
        window.location.reload();},
    error: function(xhr, ajaxOptions, thrownError){
        if(xhr){
            alert('Oops: ' + xhr.responseJSON['error']);
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
        }
        window.location.reload();
    },
    dataType: "json",
    contentType : "application/json",
    });
}

function paperVotersSubmit(token,currentUrl,redirectUrl){
    filename = $('#addPaperVoterForm input:file[name=csv]').val();
    if(filename.substr(filename.length - 4, 4).toLowerCase() != '.csv'){
        alert('Oops: The voters file must be a .csv file.');
        return;
    }

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');

    data = new FormData($('#addPaperVoterForm')[0])

    $.ajax({
    type: "POST",
    url: requestUrl,
    data: data,
    success: function(msg){
        window.location.reload();},
    error: function(xhr, ajaxOptions, thrownError){
        if(xhr){
            alert('Oops: ' + xhr.responseJSON['error']);
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
        }
    },
    dataType: "json",
    processData: false,
    contentType: false,
    });
}

function removePaperVoter(token,currentUrl,redirectUrl,voterId){
    payload={
        "voterList":[voterId]
    };

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');
    $.ajax({
    type: "POST",
    url: requestUrl,
    data: JSON.stringify(payload),
    success: function(msg){
        window.location.reload();},
    error: function(xhr, ajaxOptions, thrownError){
        if(xhr){
            alert('Oops: ' + xhr.responseJSON['error']);
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
        }
    },
    dataType: "json",
    contentType : "application/json",
    });
}

function aggregateEncTally(token,currentUrl,redirectUrl){

    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }

    var param = {
        fn:function(questionList,ballots,pValue){
            var p = new BigInteger(pValue,10)
            var aggregatedEncTally = {}
            for(var i=0;i<questionList['questionList'].length;i++){
                question = questionList['questionList'][i];
                aggregatedEncTally[question['id']] = {}
                for(var j=0;j<question["answers"].length;j++){
                    answer = question["answers"][j]
                    for(var ballotIndex=0;ballotIndex<ballots.length;ballotIndex++){
                        ballotAnswers = ballots[ballotIndex][question["id"]]["answers"][answer["id"]];
                        if(answer["id"] in aggregatedEncTally[question['id']]){
                            var alpha = aggregatedEncTally[question['id']][answer['id']]["alpha"]
                            var beta = aggregatedEncTally[question['id']][answer['id']]["beta"]
                            var aux = {
                                "alpha": (alpha.multiply(new BigInteger(ballotAnswers['alpha'],10))).mod(p),
                                "beta": (beta.multiply(new BigInteger(ballotAnswers['beta'],10))).mod(p)
                            }
                        }else{
                            var aux = {
                                "alpha": new BigInteger(ballotAnswers['alpha'],10),
                                "beta": new BigInteger(ballotAnswers['beta'],10)
                            }
                        }
                        aggregatedEncTally[question['id']][answer['id']] = aux;
                    }
                    aggregatedEncTally[question['id']][answer['id']]["alpha"] = aggregatedEncTally[question['id']][answer['id']]["alpha"].toString(10)
                    aggregatedEncTally[question['id']][answer['id']]["beta"] = aggregatedEncTally[question['id']][answer['id']]["beta"].toString(10)
                }
            }
            return aggregatedEncTally;
        },
        args:[questionList,ballots,pValue],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(data){
        url = window.location.toString();
        requestUrl = url.replace(currentUrl, redirectUrl);

        $.ajaxSetup({headers: { "X-CSRFToken": token }});
        console.log('Seding request now!');
        $.ajax({
        type: "POST",
        url: requestUrl,
        data: JSON.stringify(data),
        success: function(msg){
            window.location.reload();},
        error: function(xhr, ajaxOptions, thrownError){
            if(xhr){
                alert('Oops: ' + xhr.responseJSON['error']);
            }else{
                alert('Oops: An unexpected error occurred. Please contact the administrators');
            }
        },
        dataType: "json",
        contentType : "application/json",
        });
    });
}

var lookup;

function publishResults(){
    var scriptFiles = []
    var scripts = document.getElementsByClassName("import")
    for(var i = 0; i<scripts.length;i++){
        scriptFiles.push(scripts[i].src);
    }

    var param = {
        fn:generate_lookup_table,
        args:[pValue,gValue,numberOfEBallots],
        importFiles: scriptFiles
    }

    vkthread.exec(param).then(function(table){
        lookup = $.extend({}, table);
        var param = {
            fn:calculateResults,
            args:[pValue,questionList,partialDecryptions,aggregatedEncTally,lookup],
            importFiles:scriptFiles
        }
        vkthread.exec(param).then(function(results){
            console.log(results);
        });
    });
}

function calculateResults(pValue,questionList,partialDecryptions,aggregatedEncTally,table){
    var results = {}
    var p = new BigInteger(pValue)
    for(var i=0;i<questionList['questionList'].length;i++){
        var question = questionList['questionList'][i];
        results[question["id"]] = [question["question"],{}]
        for(var j=0;j<question["answers"].length;j++){
            var answer = question["answers"][j]
            var alpha = new BigInteger(1,10)
            for(var n=0;n<partialDecryptions.length;n++){
                alpha = alpha.multiply(new BigInteger(partialDecryptions[n][question["id"]][answer["id"]]["alpha"]));
            }
            var decryption = (new BigInteger(aggregatedEncTally[question["id"]][answer["id"]]["beta"]).multiply(alpha)).mod(p)
            results[question["id"]][1][answer["id"]]=[answer["answer"],table[decryption.toString(10)]]
        }
    }
    return results
}

function generate_lookup_table(pValue,gValue,maxValueOfTable){
    var p = new BigInteger(pValue,10);
    var g = new BigInteger(gValue,10);
    var table=[]
    var c;
    for(var i=0;i<=maxValueOfTable;i++){
        if(i==0){
            c = new BigInteger('1',10).mod(p).toString(10)
            table[c] = i
        }else{
            c = (new BigInteger(c,10).multiply(g)).mod(p).toString(10)
            table[c] = i
        }
    }
    return table;
}