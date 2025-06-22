  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-app.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
      apiKey: import.meta.env.VITE_FIREBASEAPI_KEY,
      authDomain: import.meta.env.VITE_AUTH_DOMAIN_KEY,
      projectId: import.meta.env.VITE_PROJECT_ID,
      storageBucket: import.meta.env.VITE_STORAGE_BUCKET,
      messagingSenderId: import.meta.env.VITE_MESSAGING_SENDERID,
      appId: import.meta.env.VITE_APPID,
      measurementId: import.meta.env.VITE_MEASUREMENTID
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);