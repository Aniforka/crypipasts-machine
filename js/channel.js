// content.js

const copyNodeStyle = (sourceNode, targetNode) => {
    const computedStyle = window.getComputedStyle(sourceNode);
    for (const key of computedStyle) {
        targetNode.style.setProperty(key, computedStyle.getPropertyValue(key), computedStyle.getPropertyPriority(key))
    }
}

// Wait for the page to fully load before adding the button
window.addEventListener('load', function() {
    setTimeout(function() {
        var mainButton = document.querySelector("#tabsContent > tp-yt-paper-tab.style-scope.ytd-c4-tabbed-header-renderer.iron-selected")
        var channelControls = mainButton.parentNode;

        // Create the button element
        var button = document.createElement('button');
        button.innerHTML = 'Change channel';
        copyNodeStyle(mainButton, button);

        // Add an event listener to the button
        button.addEventListener('click', function() {
            // Get the current URL
            var url = window.location.href;
            let count_of_slash = (url.match(/\//g) || []).length;

            if (count_of_slash == 4)
            {
                url = url.slice(0, url.lastIndexOf('/'));
            }

            console.log(url);

            let set_channel_window = window.open(`http://192.168.0.195:60000/api/set_channel?target=${url}`);

            setTimeout(() => set_channel_window.close(), 150);
            
            update_data_window = window.open(`http://192.168.0.195:60000/api/update_data`);

            setTimeout(() => update_data_window.close(), 150);
        });


        channelControls.insertBefore(button, mainButton);
    }, 1000);
});
