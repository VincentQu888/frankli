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

const genre = document.getElementById("genre");
const template = document.getElementById("template");

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
    genre.placeholder = genrePlaceholders[genreIndex];
    genreIndex = (genreIndex + 1) % genrePlaceholders.length;
    
}, 2000); // change every 2 seconds

setInterval(() => {
    template.placeholder = templatePlaceholders[templateIndex];
    templateIndex = (templateIndex + 1) % templatePlaceholders.length;
    
}, 2000); // change every 2 seconds


// Function to get message history (returns mock data as backup.

async function get_message_history(email) {
    // Try to fetch from API first

    // try {
    //     const response = await fetch('/api/message-history', {
    // // the above URL MUSST BE REPLACED WITH THE ACTUAL API URL
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify({"email":email}) // Add body if needed
    //     });
    //     if (response.ok) {
    //         const data = await response.json();
    //         return data.emails;
    //     }
    // } catch (error) {
    //     console.log('API not available, using mock data:', error);
    // }

    // Fallback to mock data if API is not available
    return [
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
}

// async function get_message_history(email) {
//     // Try to fetch from API first

//     try {
//         const response = await fetch('/api/message-history'),{
//             method: 'POST',
//             headers:{
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({"email":email})
//         }); 
//         alert(response)
//         if (response.ok) {
//             const data = await response.json();
//             return data;
//         }
//     } catch (error) {
//         console.log('API not available, using mock data:', error);
//     }

//     // Fallback to mock data if API is not available
//     return [
//         {
//             company: "TechStartup Inc.",
//             email: "hello@techstartup.com",
//             subject: "Partnership Opportunity",
//             dateSent: "2024-01-15",
//             status: "sent"
//         },
//         {
//             company: "Digital Agency Co.",
//             email: "contact@digitalagency.com", 
//             subject: "Design Services Proposal",
//             dateSent: "2024-01-14",
//             status: "sent"
//         },
//         {
//             company: "Innovation Labs",
//             email: "info@innovationlabs.com",
//             subject: "Collaboration Request",
//             dateSent: "2024-01-13",
//             status: "sent"
//         }
//     ];
// })

// // Function to load and display message history
async function loadMessageHistory(email) {
    try {
        const messageHistory = await get_message_history(email);

        displayMessageHistory(messageHistory);
    } catch (error) {
        console.error('Error loading message history:', error);
        displayError();
    }
}

// Function to display message history in the UI
function displayMessageHistory(messages) {

    const statsPreview = document.querySelector('.stats-preview');
    const statCards = statsPreview.querySelector('.stat-cards');
    
    if (!messages || messages.length === 0) {
        statCards.innerHTML = '<p class="text-gray">No messages sent yet...</p>';
        return;
    }
    

//------------------------------------



//------------------------------------







    // Clear existing content
    statCards.innerHTML = '';
    
    // Create message cards
    messages.forEach(message => {
        const messageCard = createMessageCard(message);
        statCards.appendChild(messageCard);
    });
}

function createMessageCard(message) {
    const card = document.createElement('div');
    card.className = 'message-card';
    
    const statusClass = getStatusClass(message.status);
    
    card.innerHTML = `
        <div class="message-header">
            <h4 class="company-name">${message.company}</h4>
            <span class="status ${statusClass}">${message.status}</span>
        </div>
        <p class="email-address">${message.email}</p>
        <p class="subject">${message.subject}</p>
        <p class="date">${formatDate(message.dateSent)}</p>
    `;
    
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
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

function displayError() {
    const statCards = document.querySelector('.stat-cards');
    statCards.innerHTML = '<p class="text-error">Error loading message history. Please try again.</p>';
} 

document.addEventListener('DOMContentLoaded', () => {
     onAuthStateChanged(auth, async (user) => {
      if (!user) {
        window.location.href = "/";
        return;
      }
          loadMessageHistory(user.email);
    })

}); 