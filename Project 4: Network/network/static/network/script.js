
let counter = 0;

// When DOM loads, render the first page
document.addEventListener("DOMContentLoaded", function () {

    if (document.querySelector('#previous') || document.querySelector('#next')) {
        const h1 = document.querySelector('h1');
        const page_name = h1.id;
        load('next', page_name);
        // if next or previous button clicked, load these pages
        document.querySelector('#previous').onclick = () => load('previous', page_name);
        document.querySelector('#next').onclick = () => load('next', page_name);
    }
    setTimeout(editText, 1000); // Instead, makethe previous function asynchron
    // If it's a page with edit buttons, get all "edit" buttons and add onclick event
});


function editText() {
    if (document.querySelector('.edit')) {
        document.querySelectorAll('.edit').forEach(edit_button => {
            edit_button.onclick = () => {
                const postid = edit_button.dataset.postid.slice(1)

                // Identify the post to be edited
                const textToEdit = document.querySelector(`#p${postid}`)

                fetch(`/edit/${postid}`)
                    .then(response => response.json())
                    // Work with the text of the post
                    .then(data => {
                        // Replace its text tag with textarea+save button
                        textToEdit.innerHTML = `<form><textarea>${data.post_text}</textarea><p></p><input type="submit" value="Save" class="btn btn-info"></form>`;

                        // When the form is submitted
                        document.querySelector('form').onsubmit = () => {
                            // Get text from the form
                            newText = document.querySelector('textarea').value;
                            // a) display the updated text field on the page
                            textToEdit.innerHTML = newText;
                            // b) put request - replace text in post obj on server
                            fetch(`/replace_text/${postid}`, {
                                method: 'PUT',
                                body: JSON.stringify({
                                    text: newText
                                })
                            })
                            return false;
                        }
                    })
            }
        })
    }
}

function load(next_or_previous, page_name) {
    // Figure out which page to load
    if (next_or_previous === 'next') {
        counter += 1
    } else {
        counter -= 1
    }
    // First, clean the div with posts and hide buttons
    document.querySelector('#posts').innerHTML = '';
    document.querySelector('#previous').hidden = true;
    document.querySelector('#next').hidden = true;
    const page_num = counter;
    // Get 10 new posts and add them
    fetch(`/posts/${page_num}/${page_name}`)
        .then(response => response.json())
        .then(data => {
            // 1 - add posts
            data.posts.forEach(add_one_post);
            // 2 - add/remove buttons
            if (data.btn_info.previous_btn) {
                document.querySelector('#previous').hidden = false;
            }
            if (data.btn_info.next_btn) {
                document.querySelector('#next').hidden = false;
            }
        })
};



function add_one_post(post) {

    // Create the card div
    const post_div = document.createElement('div');
    post_div.className = 'card'
    post_div.innerHTML = `<a href=""><h5 class="card-header">${post.author_name}</h5></a>`

    const post_body_div = document.createElement('div');
    post_body_div.className = 'card-body';

    // Create all small elements in the card body then add them to card div               
    const text = document.createElement('p');
    text.className = 'foredit card-text';
    text.id = `p${post.id}`;
    text.innerHTML = post.text;
    const time = document.createElement('p');
    time.className = 'card-text text-muted';
    time.innerHTML = `<small>${post.time}</small>`;
    const like = document.createElement('p');
    like.id = `l${post.id}`;
    like.onclick = () => toggleLike(post.id);
    // if post is liked_by current user
    if (post.liked_by_current_user) {
        like.innerHTML = `&#10084;&#65039; <span>${post.like_count}</span>`;
    } else {
        like.innerHTML = `&#129293; <span>${post.like_count}</span>`;
    }

    // Add the small elements to the card body
    post_body_div.append(text);
    post_body_div.append(time);
    post_body_div.append(like);

    // Add edit button for user's own posts
    if (post.edit_btn) {
        const edit_button = document.createElement('button');
        edit_button.innerHTML = `Edit`;
        edit_button.className = 'btn btn-primary edit';
        edit_button.dataset.postid = `e${post.id}`;
        post_body_div.append(edit_button);
    }

    // Add the card body inside the card + an empty line
    post_div.append(post_body_div);

    // Add card inside posts div
    document.querySelector('#posts').append(post_div)
    const p = document.createElement('p');
    document.querySelector('#posts').append(p);
}

function toggleLike(post_id) {
    // First, we toggle like status on the server
    fetch(`/replace_text/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            "like": 1
        })
    })
        // Toggle like button & update likes count on the page
        .then(response => {
            fetch(`/post/${post_id}`)
                .then(response2 => response2.json())
                .then(post => {
                    let likeBtn = document.querySelector(`#l${post_id}`)
                    if (post.liked_by_current_user) {
                        likeBtn.innerHTML = `&#10084;&#65039; <span>${post.like_count}</span>`;

                    } else {
                        likeBtn.innerHTML = `&#129293; <span>${post.like_count}</span>`;
                    }
                })
        })
}

