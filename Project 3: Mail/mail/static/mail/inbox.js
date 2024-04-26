document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  if (document.querySelector('#email-view')) {
    document.querySelector('.container').removeChild(document.querySelector('#email-view'));
  }

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  if (document.querySelector('#email-view')) {
    document.querySelector('.container').removeChild(document.querySelector('#email-view'));
  }

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch request to views.mailbox "emails/<int:email_id>"
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emailsArr => {

      // Create a table, add the head, append the table to the document
      let table = document.createElement('table');
      table.className = ("table")
      let thead = document.createElement('thead')
      thead.innerHTML = '<tr><td>From</td><td>Subject</td><td>Time</td></tr>'
      table.appendChild(thead)
      document.querySelector('#emails-view').appendChild(table);

      // For every email
      emailsArr.forEach(email => {
        const sender = email.sender;
        const subject = email.subject;
        const timestamp = email.timestamp;

        // Create a div element and fill it with info from json
        let tr = document.createElement('tr');
        tr.id = email.id
        tr.innerHTML = `<td>${sender}</td><td>${subject}</td><td>${timestamp}</td>`;
        email.read ? tr.className = 'read' : tr.className = '';

        // Then append it to the table
        table.appendChild(tr);

        // Add event listener to every email
        tr.onclick = () => read_email(tr.id);
      })
    })
}


function read_email(email_id) {
  // Create email-view block and append it to the document
  let div = document.createElement('div');
  div.id = 'email-view';
  document.querySelector('.container').appendChild(div);

  // Hide all the divs except email-view
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';

  // Grab email info and place it into the div
  fetch(`/emails/${email_id}`)
    .then(response => response.json()) // This is a single email json
    .then(email => {
      div.innerHTML = `<h3>Subject: ${email.subject}</h3><h4>From: ${email.sender}</h4><h5>To: ${email.recipients}</h5><p>${email.timestamp}</p><p>${email.body}</p>`

      // Deal with the 'Archived' thing
      if (email.sender !== email.user) {
        if (email.archived === false) {
          displayAndToggleArchived(email_id, email.archived);
        } else {
          displayAndToggleArchived(email_id, email.archived);
        }
      }

      // Add 'Reply' button
      p = document.createElement('p')
      div.append(p)
      replyButton = document.createElement('button');
      replyButton.innerHTML = 'Reply';
      replyButton.className = 'btn btn-primary';
      div.append(replyButton);
      replyButton.onclick = () => reply(email.id);
    })

  // Mark the email as read
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}


function displayAndToggleArchived(email_id, archive_status) {
  button = document.createElement('button');
  button.className = 'btn btn-primary';
  document.querySelector('#email-view').append(button)

  // If 'archive_status' is 'add_to_archive', write 'Archive' on the button
  // and onclick archive the email. Otherwise - 'Unarchive' button
  if (archive_status === false) {
    button.innerHTML = 'Archive';
    button.onclick = () => {
      // Toggle status to 'Archived'
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        })
      })
        // After toggling the status, display the inbox
        .then(() => load_mailbox('inbox'))
    }
  } else {
    button.innerHTML = 'Unarchive';
    button.onclick = () => {
      // Toggle status to 'Unarchived'
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: false
        })
      })
        // After toggling the status, display the inbox
        .then(() => load_mailbox('inbox'))
    }
  }
}

function reply(email_id) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  if (document.querySelector('#email-view')) {
    document.querySelector('.container').removeChild(document.querySelector('#email-view'));
  }

  // Fill in composition fields
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then((email) => {
      document.querySelector('#compose-recipients').value = `${email.sender}`;
      document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
      subject = email.subject;
      if (subject.startsWith('Re:')) {
        document.querySelector('#compose-subject').value = `${email.subject}`;
      } else {
        document.querySelector('#compose-subject').value = `Re: ${email.body}`;
      }
    }
    )
}

function send_email() {
  // Save info to use in the request
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Make fetch request & process it
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
    .then(response => response.json())
    .then(result => {
      // load the user's sent mailbox;
      load_mailbox('sent');
    })
}


