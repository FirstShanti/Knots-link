$(function() {
	$('select#category-value-select').on('change', function() {
		var url = $(this).attr('data-url').replace('empty', this.value)
		var category = toString($(this).attr('data-url').split('/')[3])
		var page = $('li.active > a.page-link').val()
		$.ajax({
			cache: false,
			url,
			type: 'GET',
			dataType: 'json',
			headers: {'api_header': 'true'},
			async: false,
			success: function (response) {	 
            	if (response) {
            		updatePosts(response, category, page)
                } else {
                	alert('Category not found')
		        }
            },
            error: function(error) {
                console.log(error);
            }
		})
	})
});

function updatePosts (response, category) {
	var posts = response.items
	var pages = response.pages
	var category = $()
	var new_posts = ''
	var paginate = ''
	for (var i in posts) {
        new_posts += `<div class="post_container">
				<div class="post_paragraph">
					<a class="post_title" href="/blog/${posts[i].slug}"> 
						${posts[i].title}
					</a>
					<div class="posts-index">
						${posts[i].preview}
					</div>
				</div>
			</div>` 
	}
	$('.post-main-container').empty().append(new_posts)
	if (response.has_prev) {
		paginate += `<li id='prev-page'>
                    <a class="page-link" href="./?page=${response.prev_num}" tabindex="-1">&#171;<span class="sr-only">(current)</span></a>
                </li>`
	}
	 else {
		$('li#prev-page').empty()
	}
	paginate += `<li class="page-item active">
                <a id='current-page' class="page-link" href="./?page=1&q=&c=${category}" value=1>1<span class="sr-only">1</span></a></li>`
	if (response.has_next) {
		paginate += `<li>
                    <a id='current-page' class="page-link" href="./?page=${response.next_num}&q=&c=${category}" value=${response.next_num}>${response.next_num}<span class="sr-only">(current)</span></a></li>`
	} else {
		$('li#next-page').empty()
	}
	$('ul.pagination').empty().append(paginate)
}	