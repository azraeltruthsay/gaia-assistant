// chat.js - Handles chat input and response display

import { sendChatMessage } from './api.js';

export function initializeChat() {
    console.log('💬 Initializing chat UI');

    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');

    if (!sendButton || !chatInput || !chatMessages) {
        console.warn('⚠️ Missing one or more chat UI elements.');
        return;
    }

    sendButton.addEventListener('click', async () => {
        const input = chatInput.value.trim();
        if (!input) return;

        appendMessage('user', input);
        chatInput.value = '';
        sendButton.disabled = true;

        try {
            const response = await sendChatMessage(input);
            appendMessage('system', response.response || '[No response]');
        } catch (e) {
            console.error('❌ Chat message failed:', e);
            appendMessage('system', '❌ Error processing your request.');
        } finally {
            sendButton.disabled = false;
        }
    });

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.innerHTML = `<div class="message-content"><p>${text}</p></div>
                         <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>`;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}
