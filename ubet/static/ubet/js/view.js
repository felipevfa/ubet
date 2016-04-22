/**
 * Adds a .input-field wrapper around forms inputs and labels so material design works correctly.
 * @return void
 */
var correct_forms = function() {
	"use strict";

	$('#form-fields li').wrap("<div class='input-field'></div>");
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

correct_forms();
toast();

$(document).ready(function() {
	$(".button-collapse").sideNav();
	$('select').material_select();
});

