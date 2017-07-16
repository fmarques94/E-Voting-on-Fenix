function toggleTrusteeList(){
    $(".TrusteeList").toggle();
    if($(".TrusteeList").is(':hidden')){
        $("#toggleButton").text('Show Trustee List &#2207')
    }else{
        $("#toggleButton").text('Hide Trustee List &#2206')
    }
}