$(document).ready(function(){
	$("button#dropdownMenuButton").click(function(){
		var mrValue = parseInt($("#category-value-select").css('margin-right'))
		var menuDisplay = String($(".dropdown-menu").css('display'))
		console.log(menuDisplay, mrValue)
		if (menuDisplay == 'none') {
			if (mrValue < 45) {
				$("#category-value-select").css('margin-right', '+=45')
			}
		} else {
			if (mrValue > 0) {
				$("#category-value-select").css('margin-right', '-=45')
			}
		}
	});
});