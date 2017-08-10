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
    paperResults[question["question"]] = {};
    var inputs = $('input:text');
    for(var i=0;i<question["answers"].length;i++){
        paperResults[question["question"]][question["answers"][i]] = inputs[i].value;
    }
}

function showNextQuestion(){
    var question = questionList['questionList'][currentQuestion];
    var htmlCode = "<fieldset><legend><h3>Paper Results</h3></legend>"+
        "<p>"+question["question"]+"</p>"+
        "<table>";
    for(var i=0;i<question["answers"].length;i++){
        htmlCode = htmlCode + "<tr><td>"+question["answers"][i]+"</td>"+
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