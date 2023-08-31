// background.js

const functionToExecute = () =>
{
    console.log("SUUUUUUUUUUUUKAAAAAAAAAAAAA");
};

chrome.webNavigation.onHistoryStateUpdated.addListener(function(details) {
    // Check if the URL matches a specific pattern
    if (details.url.includes("youtube.com/watch")) {
        // Inject a content script into the page to run a specific script
        chrome.tabs.executeScript({
            target: { tabId: details.tabId },
            function: functionToExecute
        },);
        //chrome.tabs.executeScript(details.tabId, {file: "video.js"});
    } else if (details.url.includes("youtube.com/channel") || details.url.includes("youtube.com/@")) {
        chrome.tabs.executeScript(details.tabId, {file: "channel.js"});
    }
  }, {url: [{hostSuffix: "youtube.com"}]});

//"service_worker": "js/background.js"