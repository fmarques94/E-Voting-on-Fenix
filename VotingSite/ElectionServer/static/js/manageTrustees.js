function addTrustees(form,token){
    var arr = {}
    arr["addTrustees"] = []
    for(var i=0; i<form.elements.length-1;i = i+3){
        trustee = {};
        trustee['trusteeId'] = form.elements[i].value;
        trustee['name'] = form.elements[i+1].value;
        trustee['email'] = form.elements[i+2].value;
        arr["addTrustees"].push(trustee);
    }
    var formData = JSON.stringify(arr);
    $.ajaxSetup({
        headers: { "X-CSRFToken": token }
    });
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: formData,
        success: function(){window.location.reload();},
        dataType: "json",
        contentType : "application/json",
        error: function(xhr, ajaxOptions, thrownError) {
                alert('Oops: ' + xhr.responseJSON['err']);
            }
    });
    return true;
}

function removeTrustee(trusteeId,token){
    var arr = {}
    arr["removeTrustee"] = trusteeId
    var formData = JSON.stringify(arr);
    $.ajaxSetup({
        headers: { "X-CSRFToken": token }
    });
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: formData,
        success: function(){window.location.reload();},
        dataType: "json",
        contentType : "application/json",
        error: function(xhr, ajaxOptions, thrownError) {
                alert('Oops: ' + xhr.responseJSON['err']);
            }
    });
    return true;
}