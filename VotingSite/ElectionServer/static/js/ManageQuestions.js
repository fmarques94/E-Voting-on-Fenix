var answerCounter = 2;

function addMoreAnswers(){
    answerCounter++;
    $(".inputTable").append("<tr><td><b>Answer #"+answerCounter+":</b></td>"+
                "<td><input type=\"text\" name=\"answer_"+answerCounter+"\"></td></tr>");
}

function toggleQuestionList(){
    $(".QuestionList dl").toggle();
    if($(".QuestionList dl").is(':hidden')){
        $(".toggleButton").text('Show Question List')
    }else{
        $(".toggleButton").text('Hide Question List')
    }
}