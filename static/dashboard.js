//imports for firebase auth
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyCtwLNNi28MnBT_GO5NDcD4-_hFuMDidcQ",
    authDomain: "authpoo.firebaseapp.com",
    projectId: "authpoo",
    storageBucket: "authpoo.firebasestorage.app",
    messagingSenderId: "1034827872639",
    appId: "1:1034827872639:web:7831081124bcd90513424a",
    measurementId: "G-BEZ3KX3000"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Wait for DOM to be ready before accessing elements
document.addEventListener('DOMContentLoaded', () => {
    const statsPreview = document.querySelector('.stats-preview');
    const statCards = document.querySelector('.stat-cards');
    
    if (!statsPreview || !statCards) {
        return;
    }

    // Initialize placeholder functionality
    const genre = document.getElementById("genre");
    const template = document.getElementById("template");

    if (genre && template) {
        const genrePlaceholders = [
            "A newly established restaurant...",
            "A computer repair startup...",
            "Any business...",
            "A gaming company that makes indie RPG games..."
        ];

        const templatePlaceholders = [
            "Asks for a collaboration between our companies...",
            "Requests funding from a startup...",
            "Reaches out to companies to connect...",
            "Advertises our product design services..."
        ];

        let genreIndex = 0;
        let templateIndex = 0;

        setInterval(() => {
            if (genre) {
                genre.placeholder = genrePlaceholders[genreIndex];
                genreIndex = (genreIndex + 1) % genrePlaceholders.length;
            }
        }, 2000);

        setInterval(() => {
            if (template) {
                template.placeholder = templatePlaceholders[templateIndex];
                templateIndex = (templateIndex + 1) % templatePlaceholders.length;
            }
        }, 2000);
    }

    // Firebase auth state change handler
    onAuthStateChanged(auth, async (user) => {
        if (!user) {
            window.location.href = "/";
            return;
        }
        
        const statsPreviewCheck = document.querySelector('.stats-preview');
        const statCardsCheck = document.querySelector('.stat-cards');
        
        if (!statsPreviewCheck || !statCardsCheck) {
            return;
        }
        
        try {
            await loadMessageHistory(user.email);
        } catch (error) {
            // Handle error silently or implement proper error handling
        }
    });
});

// Function to get message history
async function get_message_history(email) {
    try {
        const response = await fetch('/api/message-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"email": email})
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.emails) {
                return data.emails;
            } else if (Array.isArray(data)) {
                return data;
            } else {
                return data;
            }
        }
    } catch (error) {
        // Fall through to mock data
    }

    // Fallback to mock data if API is not available
    const mockData = [
        {
            company: "TechStartup Inc.",
            email: "hello@techstartup.com",
            subject: "Partnership Opportunity",
            dateSent: "2024-01-15",
            status: "sent"
        },
        {
            company: "Digital Agency Co.",
            email: "contact@digitalagency.com", 
            subject: "Design Services Proposal",
            dateSent: "2024-01-14",
            status: "sent"
        },
        {
            company: "Innovation Labs",
            email: "info@innovationlabs.com",
            subject: "Collaboration Request",
            dateSent: "2024-01-13",
            status: "sent"
        }
    ];
    
    return mockData;
}

// Function to load and display message history
async function loadMessageHistory(email) {
    try {
        const messageHistory = await get_message_history(email);
        
        // Handle different response formats
        let messages = messageHistory;
        if (messageHistory && messageHistory.emails) {
            messages = messageHistory.emails;
        } else if (Array.isArray(messageHistory)) {
            messages = messageHistory;
        } else {
            messages = messageHistory;
        }
        
        displayMessageHistory(messages || []);
        
    } catch (error) {
        displayError();
    }
}

// Function to display message history in the UI
function displayMessageHistory(messages) {
    const statsPreview = document.querySelector('.stats-preview');
    if (!statsPreview) {
        return;
    }
    
    const statCards = statsPreview.querySelector('.stat-cards');
    if (!statCards) {
        return;
    }
    
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
        statCards.innerHTML = '<p class="text-gray">No messages sent yet... START EMAILING!</p>';
        return;
    }
    
    // Clear existing content
    statCards.innerHTML = '';
    
    // Create message cards
    messages.forEach((message) => {
        try {
            const messageCard = createMessageCard(message);
            statCards.appendChild(messageCard);
        } catch (error) {
            // Handle individual card creation errors silently
        }
    });
}

function createMessageCard(message) {
    const card = document.createElement('div');
    card.className = 'message-card';
    
    const statusClass = getStatusClass(message.status);
    
    // Handle both 'email' and 'to' fields
    const emailAddress = message.email || message.to || 'No email';
    
    const cardHTML = `
        <div class="message-header">
            <h4 class="company-name">${message.company || 'Unknown Company'}</h4>
            <span class="status ${statusClass}">${message.status || 'unknown'}</span>
        </div>
        <p class="email-address">${emailAddress}</p>
        <p class="subject">${message.subject || 'No subject'}</p>
        <p class="date">${formatDate(message.dateSent)}</p>
    `;
    
    card.innerHTML = cardHTML;
    return card;
}

function getStatusClass(status) {
    switch(status) {
        case 'sent': return 'status-sent';
        case 'opened': return 'status-opened';
        case 'replied': return 'status-replied';
        default: return 'status-default';
    }
}

function formatDate(dateString) {
    if (!dateString) {
        return 'No date';
    }
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
    } catch (error) {
        return 'Invalid date';
    }
}

function displayError() {
    const statCards = document.querySelector('.stat-cards');
    if (statCards) {
        statCards.innerHTML = '<p class="text-error">Error loading message history. Please try again.</p>';
    }
}
