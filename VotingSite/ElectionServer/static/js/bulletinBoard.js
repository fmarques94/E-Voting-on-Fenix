$(document).ready(function() {
    $('#eligibleVoters').hide();
    $('#trusteesPublicShares').hide();
});

function togglePublicKeyShares(){
    $("#trusteesPublicShares").toggle();
    if($("#trusteesPublicShares").is(':hidden')){
        $("#toggleButtonTrustees").text('Show Trustees Public Shares')
    }else{
        $("#toggleButtonTrustees").text('Hide Trustees Public Shares')
    }

    if(!$("#eligibleVoters").is(':hidden')){
        $("#eligibleVoters").toggle();
        $("#toggleButtonVoters").text('Show Eligible Voters');
    }
}

function toggleEligibleVoters(){
    $("#eligibleVoters").toggle();
    if($("#eligibleVoters").is(':hidden')){
        $("#toggleButtonVoters").text('Show Eligible Voters')
    }else{
        $("#toggleButtonVoters").text('Hide Eligible Voters')
    }

    if(!$("#trusteesPublicShares").is(':hidden')){
        $("#trusteesPublicShares").toggle();
        $("#toggleButtonTrustees").text('Show Trustees Public Shares')
    }
}

