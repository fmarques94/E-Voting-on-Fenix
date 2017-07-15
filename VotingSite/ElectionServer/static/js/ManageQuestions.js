var answerCounter = 2;

function addMoreAnswers(){
    answerCounter++;
    $(".inputTable").append("<tr><td><b>Answer #"+answerCounter+":</b></td>"+
                "<td><input type=\"text\" name=\"answer_"+answerCounter+"\"></td></tr>");
}

function toggleQuestionList(){
    $(".QuestionList").toogle();
    if($(".QuestionList").is(':hidden')){
        $(".toggleButton").text('Show Question List &#2207')
    }else{
        $(".toggleButton").text('Hide Question List &#2206')
    }
}