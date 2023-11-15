// profile.js

// Get elements by their IDs
const editProfileButton = document.getElementById("edit-profile-button");
const editProfileForm = document.getElementById("edit-profile-form");
const profileForm = document.getElementById("profile-form");
const newUsernameInput = document.getElementById("new-username");
const newProfilePictureInput = document.getElementById("new-profile-picture");
const profilePicture = document.getElementById("profile-picture");
const userName = document.getElementById("user-name");

// Add a click event listener to the "Edit Profile" button
editProfileButton.addEventListener("click", function(event) {
    editProfileForm.style.display = "block";
    // Hide the user details while editing
    document.querySelector(".user-details").style.display = "none";
});

// Handle form submission
profileForm.addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the form from submitting traditionally

    // Get the new username and profile picture values from the form
    const newUsername = newUsernameInput.value;
    const newProfilePictureURL = newProfilePictureInput.value;

    // Update the user's name and profile picture
    userName.textContent = newUsername;
    profilePicture.src = newProfilePictureURL;

    // Hide the form after submission
    editProfileForm.style.display = "none";
    // Show the user details
    document.querySelector(".user-details").style.display = "block";
});
