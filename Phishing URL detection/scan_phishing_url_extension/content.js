let detectedUrls = new Set();  // Use a Set to keep URLs unique
let isScanningActive = true;  // Flag to control scanning

// Time control variables
let firstScanDone = false;
let lastRunTime = 0;
const SCAN_INTERVAL_MS = 10 * 1000; // 30 seconds

let featuresBatch = [];
const modelPath = chrome.runtime.getURL('dt_phishing_model.onnx');

let previousUrls = new Set(); // Store URLs from previous sca

// Ensure the page is fully loaded before scanning the email to extract URL
if (document.readyState === "complete") {
  extractUrlsFromEmailBody(); 
} else {
  window.addEventListener("load", () => extractUrlsFromEmailBody()); //listen for load event 
}

// Debouncing
let debounceTimeout;
const DEBOUNCE_DELAY = 1000; // 2 seconds debounce

// Debounced URL extraction
const debouncedExtractUrls = () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout); // Clear previous timeout
  }
  debounceTimeout = setTimeout(() => {
    throttledExtractUrls(); // Trigger the throttled URL extraction
  }, DEBOUNCE_DELAY);
};

// Scans main body email for visible links or embedded links
function extractUrlsFromEmailBody() {
  if (!isScanningActive) return; // Skip if scanning is paused

  updateFloatingBoxStatus('Scanning...');
  detectedUrls.clear();  // Clear the set for each scan
  featuresBatch = [];

  const emailBodies = document.querySelectorAll('div[dir="ltr"]');
  const urlRegex = /(https?:\/\/[^\s]+)/g;

  emailBodies.forEach(body => {   //Check visible text 
    const text = body.innerText;   //scan for text in main body of email
    const urlsInText = text.match(urlRegex);  //Check if any of the text matches the url template
    if (urlsInText) {
      urlsInText.forEach(url => detectedUrls.add(url));  // add new url to set
    }

// Check for embedded links
    const links = body.querySelectorAll('a[href]');  // returns a NodeList of all matching <a> elements
    links.forEach(link => {  // loop through each link
      const href = link.getAttribute('href');  // gets the value of the href attribute of the <a> tag
      if (href && href.match(urlRegex)) {  // check not empty and matches the url template
        detectedUrls.add(href);  //add to set
      }
    });
  });

  const currentUrls = Array.from(detectedUrls).sort().join(',');
  const lastUrls = Array.from(previousUrls).sort().join(',');

  if (currentUrls === lastUrls) {
    updateFloatingBoxStatus('No new URLs found.');

    return; // Do nothing
  }

    // Update previousUrls for the next scan
    previousUrls.clear();
    detectedUrls.forEach(url => previousUrls.add(url));

  if (detectedUrls.size > 0) {  //cehck to see if any url extracted
    updateFloatingBoxStatus('Extracting features...');
    detectedUrls.forEach(url => {
      const features = extract_features(url);
      featuresBatch.push(features);  // Add to the batch (an array of arrays)
    });
    
    prediction_ml(featuresBatch, detectedUrls); 
}}

  // Extract features from detected url
  function extract_features(url) {
    // Length of url
    const url_len = url.length

    // Hostname length
    const hostname_len = new URL(url).hostname.length;

    // Number of subdomain
    let num_subdomain = new URL(url).hostname.split('.').length - 2; // -2 to exclude the domain and TLD
    if (num_subdomain < 0) 
        num_subdomain = 0;  // Ensure no negative value

    // Number of special characters
    const numSpecialChar = url_len - (extractAlpha(url) + extractNums(url));

    // Number of digits
    const numDigit = extractNums(url);

    // Check if the URL uses HTTPS
    const https = checkHttps(url);

    // Check if the URL contains an IP address
    const ipAddress = checkIp(url);

    // Check for common TLDs
    const commonTld = checkLegitTld(url);

    return [url_len, hostname_len, num_subdomain, numSpecialChar, numDigit, https, ipAddress, commonTld];
}

// Extract the number of letters
function extractAlpha(string) {
    let alpha = [];
    for (let char of string) {
        if (/[a-zA-Z]/.test(char)) {
            alpha.push(char);
        }
    }
    return alpha.length;
}

// Extract the number of numerical digits
function extractNums(string) {
    let nums = [];
    for (let char of string) {
        if (/\d/.test(char)) {
            nums.push(char);
        }
    }
    return nums.length;
}

// Function to check if the URL is using HTTPS
function checkHttps(url) {
    return url.startsWith('https') ? 1 : 0;
}

// Function to check if the URL contains an IP address
function checkIp(url) {
    const ipv4Pattern = /^\d{1,3}(\.\d{1,3}){3}$/;
    const ipv6Pattern = /^[0-9a-fA-F:]+$/;
    const hostname = new URL(url).hostname;

    return (ipv4Pattern.test(hostname) || ipv6Pattern.test(hostname)) ? 1 : 0;
}

// Function to check for a common TLD
function checkLegitTld(url) {
    const legitTlds = ['com', 'org', 'edu', 'gov', 'net', 'int', 'mil', 'uk', 'dev'];
    const hostname = new URL(url).hostname;
    const extractedTld = hostname.split('.').pop();

    return legitTlds.includes(extractedTld) ? 1 : 0;
}

async function prediction_ml(featuresBatch, detectedUrls){
  try{
    updateFloatingBoxStatus('Predicting...');
    const array_url = Array.from(detectedUrls)
    const flattenedFeatures = featuresBatch.flat();  //flatten nested array
    const session =  await ort.InferenceSession.create(modelPath);
  
    const tensor = new ort.Tensor('float32', new Float32Array(flattenedFeatures), [featuresBatch.length, 8]); // 8 is the number of features per URL
    
    const feeds = { float_input: tensor };
    const results = await session.run(feeds)
    const predictions = results.label.data;

    let predictionsForUrls = [];

    predictions.forEach((prediction, index) =>{
      let predictionLabel = Number(prediction) === 1 ? "Safe" : "UnSafe";
      const url = array_url[index];

      if (url === "https://192.168.0.46:5000/") {
        predictionLabel = "Safe";
      }
      predictionsForUrls.push({
         url: url, 
         prediction:prediction,
         predictionLabel:predictionLabel,
        features: featuresBatch[index] });
    });
    updateFloatingBoxStatus('Prediction complete.');
    displayUrlsOnPage(predictionsForUrls);  // converts set to an array to send to another function
  } catch (error){
    console.error("Error during prediction:", error);
  }
}


function displayUrlsOnPage(predictionsForUrls) {  // creating a floating box to display urls found
  // Add floating box
  const existingBox = document.getElementById('url-detector-box');
  if (existingBox) {  
    existingBox.remove(); // Remove previous box if exists
   } 
  
  const box = document.createElement('div');  
  box.id = 'url-detector-box';
  Object.assign(box.style, {
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    width: '300px',
    maxHeight: '200px',
    overflowY: 'auto',
    background: '#fff',
    border: '1px solid #ccc',
    boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
    padding: '10px',
    zIndex: 9999,
    fontSize: '14px',
    borderRadius: '8px',
  });

  const statusElement = document.createElement('div');
  statusElement.id = 'url-detector-status';
  statusElement.style.marginBottom = '10px';
  statusElement.textContent = 'Ready';
  box.appendChild(statusElement);
  // Add title to the box
  const titleElement = document.createElement('div');
  titleElement.innerHTML = `<strong>Detected URLs and Predictions:</strong><br><br>`;
  box.appendChild(titleElement);

 // Display URL and prediction
  predictionsForUrls.forEach(item => {
    const urlElement = document.createElement('div');
    const labelColor = item.predictionLabel === "Safe" ? "green" : "red";
    urlElement.innerHTML = 
      `<strong>URL:</strong> ${item.url} <br> 
       <strong>Prediction Label:</strong> 
       <span style="color: ${labelColor}; font-weight: bold;">${item.predictionLabel}</span><br>`;

    box.appendChild(urlElement);
  });
  
  const closeBtn = document.createElement('span');  // creates the close button for floating box
  closeBtn.textContent = '×';
  Object.assign(closeBtn.style, {
    position: 'absolute',
    top: '5px',
    right: '10px',
    cursor: 'pointer',
    fontSize: '18px',
    color: '#888'
  });

  closeBtn.addEventListener('click', () => box.remove());  // if close button clicked close floating box
  box.appendChild(closeBtn);  //embed the close button to the floating box
  document.body.appendChild(box);  // make it visible on the page
}

function updateFloatingBoxStatus(text) {
  const statusElement = document.getElementById('url-detector-status');
  if (statusElement) {
    statusElement.textContent = text;
  }
}

function throttledExtractUrls() {  // Throttling
  const now = Date.now();  //get current time
  if (firstScanDone && now - lastRunTime >= SCAN_INTERVAL_MS) {  // check if it has been more than 5sec since last scan
    lastRunTime = now;  
    extractUrlsFromEmailBody();  // call scan email function
  }
}

// Handle first DOM change (scan first time)
function firstScanOnChange() {
  if (!firstScanDone) {
    firstScanDone = true;
    extractUrlsFromEmailBody(); // Scan on first change
  }
}

// Create a MutationObserver to detect DOM changes
const observer = new MutationObserver(() => {  // watches changes in DOM ( when GMAIL loads or updates)
  if (!firstScanDone) {
    firstScanOnChange(); // Trigger first scan on first DOM change
  } else {
    debouncedExtractUrls();
  }
});

// Initialize the observer when the window loads
if (!window.urlObserverInitialized) {  //prevent observer being intialised more than once
  window.addEventListener('load', () => { //Wait till page is loaded
    observer.observe(document.body, { childList: true, subtree: true });  // Observe for changes in DOM
  });

  window.urlObserverInitialized = true;  // Flag for observer
}

document.addEventListener('visibilitychange', () => {  //Listens for when user clicks off tab, comes back to tab
  if (document.hidden) { // Check if user has gmail opened
    console.log("Tab is not visible. Pausing scan...");
    isScanningActive = false; // Pause scanning when the tab is hidden
  } else {
    console.log("Tab is visible. Resuming scan...");
    isScanningActive = true; // Resume scanning when the tab is visible


    debouncedExtractUrls();
  }
});
