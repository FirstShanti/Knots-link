$(function() {
	$(window).scroll(function() {
		console.log($(this).scrollTop())
		if($(this).scrollTop() > 250) {
			$('#toTop').fadeIn();
		} else {
			$('#toTop').fadeOut();
		}
	});
	$('#toTop').click(function() {
		$('body,html').animate({scrollTop:0}, 800);
	});
	
});
