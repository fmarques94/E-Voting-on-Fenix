function toggleTrusteeList(){
    $(".TrusteeList").toggle();
    if($(".TrusteeList").is(':hidden')){
        $("#toggleButton").text('Show Trustee List &#2207')
    }else{
        $("#toggleButton").text('Hide Trustee List &#2206')
    }
}

function removeTrustee(token,currentUrl,redirectUrl,trusteeId){
    payload={
        "trusteeList":[trusteeId]
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
        "trusteeList":[]
    };

    trusteeData = {}
    trusteeData['id'] = $('#addTrusteeForm input:text[name=identifier]').val();
    trusteeData['name'] = $('#addTrusteeForm input:text[name=name]').val()
    trusteeData['email'] = $('#addTrusteeForm input[type=email][name=email]').val()

    payload['trusteeList'].push(trusteeData);

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