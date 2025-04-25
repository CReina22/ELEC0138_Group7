//const API_BASE = "http://127.0.0.1:5000";

const urlParams = new URLSearchParams(window.location.search);
const API_BASE = urlParams.get('apiBase') || window.location.origin;
console.log('Using API Base:', API_BASE);  // print current API base


// display login, ignore register section
function showLogin() {
    console.log("[DEBUG] showLogin() used");

    document.getElementById('login-section').style.display = 'block';

    // clear input fields
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

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
    const fingerprint = JSON.stringify(collectFingerprint()); // Used for Anomaly Detection

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'include', // include cookies in the request
        body: JSON.stringify({ username, password, fingerprint }) 
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Redirect to transactions page
            window.location.href = 'https://192.168.0.46:5000/transactions';
        } else {
            alert(data.message);
        }
    })
    .catch(err => {
        // Log detailed error information
        console.error("Login error details:", {
            error: err,
            message: err.message,
            stack: err.stack,
            url: `${API_BASE}/login`,
            requestData: { username, password: "REDACTED", fingerprint: "REDACTED" }
        });
        console.error("Login error:", err);
        alert("Server error during login");
    });

}
    