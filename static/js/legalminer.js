$(document).ready(function(){
    $('#search-filters').hide();
});

function showFilters(){
    $('#search-filters').slideToggle('fast');
};

$( function() {
  $( "#id_fecha_from" ).datepicker({
      dateFormat: "dd/mm/yy"
  });
  $( "#id_fecha_to" ).datepicker({
      dateFormat: "dd/mm/yy"
  });

});
