 $(document).ready(function() {
    $('.datepicker').datepicker({ dateFormat: 'dd-mm-yy' });
    $('.timePicker').timepicker({ 'timeFormat': 'H:i','step': 15, useSelect: true });
 });

function enableCastTimes(){
     $('.castTime select').prop('disabled', false);
}

function disableCastTimes(){
     $('.castTime select').prop('disabled', true);
}