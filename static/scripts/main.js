$(function() {
	$('select#category-value-select').on('change', async function() {
		var url = $(this).attr('data-url').replace('empty', this.value)
		var category = this.value
		var page = $('li.active > a.page-link').val()
		let data = await request('GET', url)
		updatePosts(data, category, page)
	})
	fixDropdownMenu()
});

fixDropdownMenu = function () {
	if ($('i#user_button').hasClass('with_user')) {
		$('.dropdown-menu').css('left', '0px')
	}
}

function updatePosts (response, category) {
	var posts = response.posts
	var pages = response.pages
	var new_posts = ''
	var paginate = ''
	if (posts.length == 0) {
		$('.post_not_found').empty().append(
			`<button
                id='btn-create'
                value="blog/create"
                type="submit"
                class="btn btn-success"
                onclick="document.location.href='/blog/create/${category}'">
                    Add post
            </button>`
		)
	} else {
		$('.post_not_found').empty()
	}
	for (var i in posts) {
        new_posts += `<div class="post_container">
				<div class="post_paragraph">
					<a class="post_title" href="/blog/${posts[i].id}"> 
						${posts[i].title}
					</a>
					<div class="posts-index">
						${posts[i].preview}
					</div>
					<div class='post_meta_detail'>
						<div style='margin-right: auto;'>
							<a style="color: grey;" href="/knot/${posts[i].author || 'anonymous'}">
								<i class="fas fa-user"></i>
								${posts[i].author}
							</a>
							<a style="color: grey;" href="/blog/${posts[i].id}#comments">
								<i class="fas fa-comments"></i>
								${posts[i].comments.length}
							</a>
						</div>
						<div style="margin-left: auto;">
							<i class="fas fa-clock"></i>
							${moment(posts[i].created).format('DD-MM-YYYY')}
						</div>
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
	paginate += `<li class="page-item active"><a id='current-page' class="page-link" href="./?page=1&q=&c=${category}" value=1>1<span class="sr-only">1</span></a></li>`
	if (response.has_next) {
		paginate += `<li><a id='current-page' class="page-link" href="./?page=${response.next_num}&q=&c=${category}" value=${response.next_num}>${response.next_num}<span class="sr-only">(current)</span></a></li>`
	} else {
		$('li#next-page').empty()
	}
	$('ul.pagination').empty().append(paginate)
}