$(document).ready(function() {
    $('.loader').height($('.button').height());
    $('.loader').width($('.loader').height());
});


function toggleVoterList(){
    $(".VoterList").toggle(0,function(){
        if($(".VoterList").is(':hidden')){
            $("#toggleButton").text('Show Trustee List')
        }else{
            $("#toggleButton").text('Hide Trustee List')
        }
    });
}

function submit(token,currentUrl,redirectUrl){
    $('#addVoterButton').hide();
    $('#addVoterFileButton').hide();
    $('.loader').css("display", "block");
    payload={
        "voterList":[]
    };

    VoterData = {}
    VoterData['id'] = $('#addVoterForm input:text[name=identifier]').val();
    VoterData['email'] = $('#addVoterForm input[type=email][name=email]').val()

    payload['voterList'].push(VoterData);

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
            $('#addVoterButton').show();
            $('#addVoterFileButton').show();
            $('.loader').css("display", "none");
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
            $('#addVoterButton').show();
            $('#addVoterFileButton').show();
            $('.loader').css("display", "none");
        }
    },
    dataType: "json",
    contentType : "application/json",
    });
}


function fileSubmit(token,currentUrl,redirectUrl){
    $('#addVoterFileButton').hide();
    $('#addVoterButton').hide();
    $('.loader').css("display", "block");
    filename = $('#addVoterFileForm input:file[name=csv]').val();
    if(filename.substr(filename.length - 4, 4).toLowerCase() != '.csv'){
        alert('Oops: The voters file must be a .csv file.');
        return;
    }

    url = window.location.toString();
    requestUrl = url.replace(currentUrl, redirectUrl);

    $.ajaxSetup({headers: { "X-CSRFToken": token }});
    console.log('Seding request now!');

    data = new FormData($('#addVoterFileForm')[0])

    $.ajax({
    type: "POST",
    url: requestUrl,
    data: data,
    success: function(msg){
        window.location.reload();},
    error: function(xhr, ajaxOptions, thrownError){
        if(xhr){
            alert('Oops: ' + xhr.responseJSON['error']);
            $('#addVoterFileButton').show();
            $('#addVoterButton').show();
            $('.loader').css("display", "none");
        }else{
            alert('Oops: An unexpected error occurred. Please contact the administrators');
            $('#addVoterFileButton').show();
            $('#addVoterButton').show();
            $('.loader').css("display", "none");
        }
    },
    dataType: "json",
    processData: false,
    contentType: false,
    });
}

function removeVoter(token,currentUrl,redirectUrl,voterId){
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