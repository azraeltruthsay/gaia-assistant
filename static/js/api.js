// api.js - Handles API communications with GAIA backend

export async function fetchServerStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching server status:', error);
        throw error;
    }
}

export async function sendChatMessage(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        if (!response.ok) {
            throw new Error(`Chat message failed: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error sending chat message:', error);
        throw error;
    }
}

// Future example:
// export async function fetchDocuments() { ... }
// export async function uploadFile(file) { ... }
