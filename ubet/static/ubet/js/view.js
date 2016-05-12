/**
 * Adds a .input-field wrapper around forms inputs and labels so material design works correctly.
 * @return void
 */
var correct_forms = function() {
	"use strict";

	$('#form-fields li').not(".errorlist li").wrap("<div class='input-field'></div>");
};

/**
 * Shows a toast at the bottom of the screen containing the contents of {{ toast_msg }} variable from Django.
 * @return void
 */
var toast = function() {
	var toast = $('#toast').text();
	
	if (toast) {
		Materialize.toast(toast, 3000);
	}
};

$(document).ready(function() {
	//correct_forms();
	toast();
	
	$(".button-collapse").sideNav();
	$(".modal-trigger").leanModal();
	
	$('select').material_select();

	
	if ($('.datepicker')) {
		$('.datepicker').pickadate({
		selectMonths: true,
		selectYears: 60,
		max: true,
		hiddenName: true,
		formatSubmit: 'mm/dd/yyyy',
		});
	}

	if ($('#group-list-wrapper').length) {
		$('main').removeClass('container');
	}
});

