// Helper functions
function strip_whitespace(string) {

	// the approach to loading a program input by the user will be to:
	// 0. VALIDATE the input, must be a proper program
	// 1. strip all whitespace from value in text field
	// 2. split input program up into sets of two characters
		// so, it'll be an array of two-char long strings
	// 3. translate strings into numbers via "hex string"-to-decimal
	// 4. load that array into the program variable (pass it in or something)

}

// Initialize on load

$(document).ready(function() {
	console.log('starting...');
	initialize_chip8();
});

// Targets

game_screen = $('#screen-canvas');

run_button = $('#run-program');

stop_button = $('#stop-program');

input_form = $('#program-input');

submit_button = $('#submit-program');

// Behavior

run_button.click(function(e) {
	e.preventDefault();
	set_run_status(true);
});

stop_button.click(function(e) {
	e.preventDefault();
	set_run_status(false);
}); 

input_form.submit(function(e) {
	e.preventDefault();
	console.log(input_form.val());
});

submit_button.click(function(e) {
	e.preventDefault();
	input_form.submit();
});

$(document).keydown(function(e) {
	e.preventDefault();

	if (!keys[e.which] && keys.hasOwnProperty(e.which)) {
		keys[e.which] = true;
	}

});

$(document).keyup(function(e) {
	e.preventDefault();

	if (keys[e.which] && keys.hasOwnProperty(e.which)) {
		keys[e.which] = false;
	}

});

// Misc