function register(token,currentUrl,redirectUrl,voterEmail){

    $('.registerButton').css("display", "none");
    $('.loader').css("display", "block");

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');
    $.ajax({
    type: "GET",
    url: requestUrl,
    success: function(msg){
        $(".registerButton").remove();
        $(".loader").remove();
        $(".content").append(
            "<p>The credentials have been sent to your email address at "+voterEmail+"</p>"+
            "<a class=\"registerButton\" href=\"javascript:refresh()\">Click here to vote</a>"
        )
    },
    error: function(xhr, ajaxOptions, thrownError){
        if(xhr){
            alert('Oops: ' + xhr.responseJSON['error']);
            $('.registerButton').css("display", "block");
            $('.loader').css("display", "none");
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
            $('.registerButton').css("display", "block");
            $('.loader').css("display", "none");
        }
    },
    dataType: "json",
    });
}

function refresh(){
    window.location.reload();
}