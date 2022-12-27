$(document).ready(function() {
	let navButton = $("button#dropdownMenuButton")
	if (!!navButton) {
		$("button#dropdownMenuButton").click(function(){
			var mrValue = parseInt($("#category-value-select").css('margin-right'))
			var menuDisplay = String($(".dropdown-menu").css('display'))
			if (menuDisplay == 'none') {
				if (mrValue <= 45) {
					$("#category-value-select").css('margin-right', '+=45')
				}
			} else {
				if (mrValue > 0) {
					$("#category-value-select").css('margin-right', '0')
				}
			}
		});
		$(document).click(function(){
			var menuDisplay = String($(".dropdown-menu").css('display'))
			var mrValue = parseInt($("#category-value-select").css('margin-right'))
			if (menuDisplay == 'none' && mrValue > 0) {
				$("#category-value-select").css('margin-right', '0')
			}
		})
	}
});