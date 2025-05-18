function showInfoModal(title, message) {
    document.getElementById('infoModalLabel').innerText = title; // Set the title
    document.getElementById('infoModalMessage').innerText = message; // Inject the message
    var infoModal = new bootstrap.Modal(document.getElementById('infoModal'));
    infoModal.show();
}

function showDecisionModal(title, message, callback) {
    document.getElementById('decisionModalLabel').innerText = title; // Set the title
    document.getElementById('decisionModalMessage').innerText = message; // Inject the message
    const yesButton = document.getElementById('decisionModalYesButton');

    // Set the callback for the Yes button
    yesButton.onclick = function () {
        callback(); // Execute callback (e.g., for logout)
        var decisionModal = new bootstrap.Modal(document.getElementById('decisionModal'));
        decisionModal.hide(); // Hide the modal after the action
    };

    // Show the modal
    var decisionModal = new bootstrap.Modal(document.getElementById('decisionModal'));
    decisionModal.show();
}


