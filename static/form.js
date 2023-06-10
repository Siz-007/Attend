
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword} from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
  measurementId: ""
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// console.log(app);
const auth = getAuth(app);

var email, password, signupPassword, confirmSignupEmail, confirmSignUpPassword;
const submitButton = document.getElementById("submit");
const emailInput = document.getElementById("email");

const passwordInput = document.getElementById("password");


submitButton.addEventListener("click", function() {
    email = emailInput.value;
    console.log(email);
    password = passwordInput.value;
    console.log(password);
  
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in
        const user = userCredential.user;
        const dic={email};
        const s=JSON.stringify(dic);
        swal("Congrats !", "Successfully Login","success");
        // window.alert("Success! Welcome back!");
        window.location.replace("upload1");
        $.ajax({
          url:"/upload",
          type:"POST",
          contentType:"application/json",
          data:JSON.stringify(s)
        })
        
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.log("Error occurred. Try again.");
        // window.alert("Error occurred. Try again.");
        sweetAlert("Oops...", "Something went wrong!", "error");
      });

      
  });

  