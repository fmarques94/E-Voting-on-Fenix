function deleteElection(token,requestUrl){
    if(window.confirm('Are you sure you want to delete this election?')){
        $(".content").html("<div class=\"bar\"></div>");
        $.ajaxSetup({headers: { "X-CSRFToken": token }});
        console.log('Seding request now!');

        $.ajax({
        type: "POST",
        url: requestUrl,
        success: function(msg){
            $(".content").html(
                "<p>Election deleted with success</p>"
            )
        },
        error: function(xhr, ajaxOptions, thrownError){
            if(xhr){
                alert('Oops: ' + xhr.responseJSON['error']);
            }else{
                alert('Oops: An unexpected error occurred. Please contact the administrators');
            }
        },
        dataType: "json",
        });
    }else{
        return;
    }
}