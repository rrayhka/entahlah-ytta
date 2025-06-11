// This file contains JavaScript code for the frontend functionality of the application. 
// It handles user interactions and dynamic content updates.

document.addEventListener('DOMContentLoaded', function() {
    const prevButton = document.querySelector('button[onclick*="prev"]');
    const nextButton = document.querySelector('button[onclick*="next"]');
    const deleteButton = document.querySelector('button[onclick*="delete"]');
    const moveButtons = document.querySelectorAll('button[onclick*="move"]');

    if (prevButton) {
        prevButton.addEventListener('click', function() {
            // Add any additional functionality for the previous button if needed
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function() {
            // Add any additional functionality for the next button if needed
        });
    }

    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this image?')) {
                fetch('/delete', { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('Error deleting image.');
                        }
                    });
            }
        });
    }

    moveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const destination = this.getAttribute('onclick').match(/to=(\w+)/)[1];
            fetch(`/move?to=${destination}`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Error moving image.');
                    }
                });
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight') {
            nextButton.click();
        } else if (e.key === 'ArrowLeft') {
            prevButton.click();
        } else if (e.key === 'Delete') {
            deleteButton.click();
        }
    });
});