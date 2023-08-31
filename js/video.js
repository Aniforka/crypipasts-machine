// content.js

// Wait for the page to fully load before adding the button
window.addEventListener('load', function() {
    setTimeout(function() {
        // Find the container element for the video controls
        var videoControls = document.querySelector('#top-level-buttons-computed');

        var url = window.location.href;

        // Create the button element
        var button = document.createElement('button');
        button.innerHTML = 'Add to queue';
        button.style.backgroundColor = 'blue';
        button.style.color = 'white';
        button.style.borderRadius = '4px';
        button.style.padding = '8px 16px';

        // Add an event listener to the button
        button.addEventListener('click', function() {
            // Get the current URL
            let add_video_window = window.open(`http://192.168.0.195:60000/api/queue_add_video?target=${url}`);

            setTimeout(() => add_video_window.close(), 150)
        });

        // Find the Share button
        var shareButton = videoControls.querySelector('ytd-share-button-renderer');
        console.log(shareButton);

        // Insert the button before the Share button
        videoControls.insertBefore(button, shareButton);
    }, 1000);
});