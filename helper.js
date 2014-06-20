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
	input_form.submit();
	set_run_status(true);
});

stop_button.click(function(e) {
	e.preventDefault();
	set_run_status(false);
}); 

input_form.submit(function(e) {
	e.preventDefault();
	parsed_program = input_form.val().replace(/ /g, '').match(/.{1,2}/g);
	for (var i = 0; i < parsed_program.length; i++) {
		parsed_program[i] = parseInt(parsed_program[i], 16);
	}
	program = parsed_program;
	console.log(parsed_program);

});

submit_button.click(function(e) {
	e.preventDefault();
	input_form.submit();
});

// Key logging

$(document).keydown(function(e) {

	// console.log(e.which);

	if (!keys[e.which] && keys.hasOwnProperty(e.which)) {
		// keydown_event = true;
		// captured_key = key_reverse[e.which];

		// keydown_event = false;
		// captured_key = 0;

		keys[e.which] = true;

		if (waiting_for_key) {
			captured_key = key_reverse[e.which];
			waiting_for_key = false;
		}

		// console.log(keys);
	}

});

$(document).keyup(function(e) {

	if (keys[e.which] && keys.hasOwnProperty(e.which)) {
		keys[e.which] = false;
		// console.log(keys);
	}

});