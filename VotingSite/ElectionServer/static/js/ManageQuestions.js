var answerCounter = 2;

 $(document).ready(function() {
    $(".removeAnswersButton").hide();
 });

function addMoreAnswers(){
    answerCounter++;
    $(".inputTable").append("<tr><td><b>Answer #"+answerCounter+":</b></td>"+
                "<td><input type=\"text\" name=\"answer_"+answerCounter+"\" required></td></tr>");
    $(".removeAnswersButton").show();
}

function removeAnswers(){
    if(answerCounter>2){
        $(".inputTable tr")[answerCounter].remove();
        answerCounter--;
        if(answerCounter==2){
            $(".removeAnswersButton").hide();
        }
    }
}

function toggleQuestionList(){
    $(".QuestionList dl").toggle();
    if($(".QuestionList dl").is(':hidden')){
        $(".toggleButton").text('Show Question List')
    }else{
        $(".toggleButton").text('Hide Question List')
    }
}

function removeQuestion(token,currentUrl,redirectUrl,questionId){
    payload={
        "questionList":[questionId]
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

function submit(token,currentUrl,redirectUrl){
    payload={
        "questionList":[]
    };

    questionData = {}
    questionData['question'] = $('#addQuestionForm input:text[name=question]').val();
    questionData['answers'] = []
    for(i=1;i<=answerCounter;i++){
        questionData['answers'].push($('#addQuestionForm input:text[name=answer_'+i+']').val());
    }

    payload['questionList'].push(questionData);

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