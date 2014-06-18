$('#run-program').click(function(e) {
	e.preventDefault();
	set_run_status(true);
});

$('#stop-program').click(function(e) {
	e.preventDefault();
	set_run_status(false);
});

$('#program-input').submit(function(e) {
	e.preventDefault();
});