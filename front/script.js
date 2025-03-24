// dislpay login or register section
function showRegister() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';

    // clear input fields
    document.getElementById('register-username').value = '';
    document.getElementById('register-password').value = '';
    document.getElementById('confirm-password').value = '';
}

// display login, ignore register section
function showLogin() {
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    // clear input fields
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// login button click
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (username && password) {

        document.getElementById('auth-box').style.display = 'none';
        //document.getElementById('login-section').style.display = 'none';
        //document.getElementById('register-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'block';

        // change background
        document.body.classList.remove('with-bg');
        document.body.classList.add('no-bg');

        // display username
        document.getElementById('user-display').innerText = username;

        // display balance
        document.getElementById('balance').innerText = '1000.00';
    } else {
        alert("Please enter username and password");
    }

}

// register button click
function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!username || !password || !confirmPassword) {
        alert("Please fill in all fields.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    alert("Registration successful! Please log in.");
    showLogin();
}

function logout() {
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('auth-box').style.display = 'block';

    // change background
    document.body.classList.remove('no-bg');
    document.body.classList.add('with-bg');
    showLogin(); 
    //document.getElementById('dashboard-section').style.display = 'none';
}