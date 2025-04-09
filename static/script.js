//const API_BASE = "http://127.0.0.1:5000";

const urlParams = new URLSearchParams(window.location.search);
const API_BASE = urlParams.get('apiBase') || window.location.origin;
console.log('Using API Base:', API_BASE);  // print current API base


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
    console.log("[DEBUG] showLogin() used");

    document.getElementById('register-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-login-section').style.display = 'none';

    // clear input fields
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}


// load transactions from API
function loadTransactions() {
    fetch(`${API_BASE}/transactions`,{
        method: "GET",
        credentials: "include"  // include cookies in the request
    })
    .then(response => {
        if (response.status === 401) {
            alert('Session expired or unauthorized. Please login again.');
            showLogin();
            return null;
    }
    return response.json();
    })
    .then(data => {
        if (!data) return; // no data to display

        const tableBody = document.querySelector('#transactions-table tbody');
        tableBody.innerHTML = ''; // clear existing rows

        data.forEach(txn => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${txn.TransactionID}</td>
                <td>${txn.CustomerID}</td>
                <td>${txn['TransactionAmount (INR)']}</td>
                <td>${txn.TransactionDate || '-'}</td>
                <td>${txn.CustAccountBalance || '-'}</td>
                `;
            tableBody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error fetching transactions:', error);
        alert('Server error. Please try again later.'); 
    });
}

// Collect fingerprint data
function collectFingerprint() {
    return {
        // Basic information
        browser: navigator.userAgent,
        os: navigator.platform,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        
        // Additional screen properties
        colorDepth: window.screen.colorDepth,
        pixelRatio: window.devicePixelRatio,
        
        // Browser capabilities
        cookiesEnabled: navigator.cookieEnabled,
        doNotTrack: navigator.doNotTrack,
        
        // Browser plugins and MIME types
        plugins: Array.from(navigator.plugins).map(p => ({
            name: p.name,
            description: p.description
        })),
        
        // Hardware info
        cpuCores: navigator.hardwareConcurrency || 'unknown',
        
        // Connection info
        connectionType: navigator.connection ? 
            navigator.connection.effectiveType : 'unknown',
            
        // Date/Time for request timing
        timestamp: new Date().toString(),
        
        // Canvas fingerprinting (creates a hash based on how the browser renders)
        canvasHash: (() => {
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 200;
                canvas.height = 50;
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillText('Fingerprint', 0, 0);
                return canvas.toDataURL().slice(0, 100);
            } catch (e) {
                return 'canvas-unsupported';
            }
        })()
    };
}

// login button click
function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const fingerprint = JSON.stringify(collectFingerprint());

    if (!username || !password) {
        alert("Please enter username and password.");
        return;
    }

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'include', // include cookies in the request
        body: JSON.stringify({ username, password, fingerprint }) // Send full fingerprint data
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
    const email = document.getElementById('register-email').value.trim();
    const code = document.getElementById('register-email-code').value.trim();
    const password = document.getElementById('register-password').value.trim();
    const confirmPassword = document.getElementById('confirm-password').value.trim();

    if (!username || !email || !code || !password || !confirmPassword) {
        alert("Please fill in all fields.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    fetch(`${API_BASE}/verify_register_code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            username: username, 
            email: email, 
            code: code, 
            password: password 
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
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
    // send logout request to server and clear session
    fetch('/logout', {
        method: 'POST',
        credentials: 'include'  // include cookies in the request
    })
    .then(response => response.json())
    .then(data => { 
        if (data.success) {
            console.log('Logout successful');
        } else {
            console.warn('Logout failed:', data.message);
        }
        document.getElementById('dashboard-section').style.display = 'none';
        document.getElementById('auth-box').style.display = 'block';

        // change background
        document.body.classList.remove('no-bg');
        document.body.classList.add('with-bg');
        showLogin(); 
    })
    .catch(error => {
        console.error('Error during logout:', error);
    });
}


// email login button click
function showEmailLogin() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-login-section').style.display = 'block';

    // clear input fields
    document.getElementById('login-email').value = '';
    document.getElementById('email-code').value = '';
}

//send login email code
function sendCode() {

    const email = document.getElementById('login-email').value.trim();
    if (!email) {
        alert("Please enter your email.");
        return;
    }

    fetch(`${API_BASE}/send-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Verification code sent.");
    })
    .catch(err => {
        console.error("Send code error:", err);
        alert("Server error while sending code.");
    });
}

// verify email code and login
function verifyCode() {
    const email = document.getElementById('login-email').value.trim();
    const code = document.getElementById('email-code').value.trim();

    if (!email || !code) {
        alert("Please enter both email and code.");
        return;
    }

    fetch(`${API_BASE}/verify-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // include cookies in the request
        body: JSON.stringify({ email: email, code: code })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('auth-box').style.display = 'none';
            document.getElementById('dashboard-section').style.display = 'block';
            loadTransactions(); // load transactions after login

            // change background
            document.body.classList.remove('with-bg');
            document.body.classList.add('no-bg');

            // display user email
            document.getElementById('user-display').innerText = email;
        } else {
            alert(data.message || "Invalid code or email");
        }
    })
    .catch(err => {
        console.error("Verify error:", err);
        alert("Server error during verification");
    });
}

// send register code
function sendRegisterCode(){
    const email = document.getElementById('register-email').value.trim();
    
    if (!email) {
        alert("Please enter your email.");
        return;
    }

    fetch(`${API_BASE}/register_email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Verification code sent.");
        document.getElementById('register-section').style.display = 'block';
    })
    .catch(err => {
        console.error("Send code error:", err);
        alert("Server error while sending code.");
    });
}

