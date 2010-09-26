$("#parameters_form input[id*='date']").datepicker({showOn: 'button', buttonImage: '/site_media/images/calendar.gif', buttonImageOnly: true, showButtonPanel: true});

$("#date_helpers-off").html("\
<ul>\
<li><input type='button' value='Hoy' /></li>\
<li><input type='button' value='Este mes' /></li>\
<li><input type='button' value='Mes previo' /></li>\
<li><input type='button' value='Este año' /></li>\
<li><input type='button' value='Año previo' /></li>\
<li><input type='button' value='Este año fiscal' /></li>\
<li><input type='button' value='Año fiscal previo' /></li>\
</ul>\
");
