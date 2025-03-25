const API_BASE = "http://127.0.0.1:5000";

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


// load transactions from API
function loadTransactions() {
    fetch(`${API_BASE}/transactions`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#transactions-table tbody');
            tableBody.innerHTML = ''; // clear existing rows

            data.forEach(txn => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${txn.TransactionID}</td>
                    <td>${txn.CustomerID}</td>
                    <td>${txn['TransactionAmount (INR)']}</td>
                    <td>${txn.TransactionDate || '-'}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching transactions:', error));
}

// login button click
function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!username || !password) {
        alert("Please enter username and password.");
        return;
    }

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('auth-box').style.display = 'none';
            loadTransactions(); // load transactions after login
            document.getElementById('dashboard-section').style.display = 'block';

            // change background
            document.body.classList.remove('with-bg');
            document.body.classList.add('no-bg');

            document.getElementById('user-display').innerText = username;
        
        } else {
            alert(data.message || "Login failed");
        }
    })
    .catch(err => {
        console.error("Login error:", err);
        alert("Server error during login");
    });

}



// register button click
function register() {
    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value.trim();
    const confirmPassword = document.getElementById('confirm-password').value.trim();

    if (!username || !password || !confirmPassword) {
        alert("Please fill in all fields.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Registration successful! Please log in.");
            showLogin();
        } else {
            alert(data.message || "Registration failed");
        }
    })
    .catch(err => {
        console.error("Register error:", err);
        alert("Server error during registration");
    });
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