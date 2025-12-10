const tabbar = document.getElementById("tabbar");
const urlInput = document.getElementById("url");
let tabs = [];
let activeTab = 0;

function createTab(url = "https://duckduckgo.com") {
    const index = tabs.length;
    tabs.push({ url });

    const tabElement = document.createElement("div");
    tabElement.className = "tab";
    tabElement.textContent = "New Tab";
    tabElement.onclick = () => switchTab(index);
    tabbar.appendChild(tabElement);

    switchTab(index);
}

function switchTab(index) {
    activeTab = index;
    tabs.forEach((t, i) => {
        tabbar.children[i].classList.toggle("active", i === index);
    });
    urlInput.value = tabs[index].url;
}

function openURL() {
    let input = urlInput.value.trim();
    if (!input) return;

    let url = "";

    if (input.startsWith("http://") || input.startsWith("https://")) {
        url = input;
    } else if (input.includes(".")) {
        url = "https://" + input;
    } else {
        url = "https://duckduckgo.com/?q=" + encodeURIComponent(input);
    }

    tabs[activeTab].url = url;
    tabbar.children[activeTab].textContent = url.replace(/^https?:\/\//, "");

    window.open(url, "_blank");
}

document.getElementById("go").onclick = openURL;
urlInput.addEventListener("keypress", e => {
    if (e.key === "Enter") openURL();
});

document.getElementById("back").onclick = () => alert("Use device back button");
document.getElementById("forward").onclick = () => alert("Use device forward");
document.getElementById("reload").onclick = () => location.reload();

document.getElementById("newtab").onclick = () => createTab();

createTab();
