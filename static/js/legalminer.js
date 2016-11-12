$(document).ready(function(){
    $('#search-filters').hide();
});

// Display advance filters.
function showFilters(){
    $('#search-filters').slideToggle('fast');
};

//Display case details.
function expand_desc(){
    $('#desc_container').slideToggle('slow')
}

// Display datepicker.
$( function() {
  $( "#id_fecha_from" ).datepicker({
      dateFormat: "dd/mm/yy"
  });
  $( "#id_fecha_to" ).datepicker({
      dateFormat: "dd/mm/yy"
  });
});
