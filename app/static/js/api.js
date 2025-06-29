// api.js
// Central API request utility for GAIA frontend

function logAPI(msg, level = "info") {
  const prefix = "[API]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 📡 ${msg}`);
  }
}

/**
 * Unified API request handler
 * @param {string} url - API endpoint
 * @param {"GET"|"POST"} method - HTTP method
 * @param {Object} [payload] - Data to send for POST
 * @returns {Promise<Object|null>} - Parsed JSON or null
 */
async function apiRequest(url, method = "GET", payload = null) {
  try {
    const options = {
      method,
      headers: { "Content-Type": "application/json" }
    };
    if (method === "POST" && payload) {
      options.body = JSON.stringify(payload);
    }

    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    logAPI(`Success: ${url}`);
    return data;
  } catch (err) {
    logAPI(`Request failed: ${err}`, "error");
    return null;
  }
}
