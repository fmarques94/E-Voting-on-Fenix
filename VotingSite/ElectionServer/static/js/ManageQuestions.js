
answer_count=2

template = "<tr><td>Answer 2:</td><td><input type=\"text\" name=\"Answer_2\"></td></tr>"

function add_answers(){
    answer_count++;
    $( ".QuestionAnswerTable" ).append("<tr><td>Answer "+answer_count+":</td><td><input type=\"text\" name=\"Answer_"+answer_count+"\"></td></tr>");
}

function add_question(token){
    $.ajaxSetup({
        headers: { "X-CSRFToken": token }
    });
    form = $(".QuestionAnswerForm").serializeArray()
    var arr = {}
    arr['question'] = form[0].value
    arr['answer'] = {}
    for(var i=1; i < form.length; i++){
        arr['answer'][i] = form[i].value
    }
    console.log(arr)
    var formData = JSON.stringify(arr);
    console.log(formData)
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: formData,
        success: function(){window.location.reload();},
        dataType: "json",
        contentType : "application/json"
        });
}