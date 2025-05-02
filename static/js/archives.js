// archives.js - Handles conversation archives for GAIA

// Import anything else you want from conversation_archives.js later
// import { saveConversation, loadConversations } from './conversation_archives.js'; (future)

let archives = [];

export function initializeArchives() {
    console.log('🗃️ Archives system initialized.');
    // Optionally load existing archives here
}

export function saveConversationArchive(conversation) {
    if (!conversation || conversation.length === 0) {
        console.warn('⚠️ Tried to save empty conversation.');
        return;
    }

    const timestamp = new Date().toISOString();
    const archiveEntry = {
        timestamp,
        conversation,
    };

    archives.push(archiveEntry);
    console.log('✅ Conversation archived:', archiveEntry);

    // TODO: Persist archives to localStorage, server, or database
}

export function getArchives() {
    return archives;
}

export function clearArchives() {
    archives = [];
    console.log('🧹 All conversation archives cleared.');
}
