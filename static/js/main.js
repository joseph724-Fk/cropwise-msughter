document.addEventListener("DOMContentLoaded", () => {
    initApp();
    setupSPARouter();
    setupSidebar();
    setupUserDropdown();
    setupCropWiseBot();
    setupCommunityChat();
    setupSplashScreen();
    setupPublicNav();
    setupThemeToggle();
});

const progressBar = document.createElement("div");
progressBar.id = "nprogress";
document.body.appendChild(progressBar);

function initApp(root = document) {
    bindAjaxForms(root);
    autoHideFlashes(root);
}

/* ================= THEME TOGGLE ================= */
function setupThemeToggle() {
    const toggleBtns = document.querySelectorAll(".theme-toggle");

    toggleBtns.forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = "true";

        btn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("cropwise_theme", newTheme);
        });
    });
}

/* ================= LAYOUT & NAV ================= */
function setupSidebar() {
    const sidebar = document.getElementById("appSidebar");
    const pinBtn = document.getElementById("pinSidebarBtn");
    const mobileBtn = document.getElementById("mobileMenuBtn");

    if (!sidebar) return;

    const isPinned = localStorage.getItem("sidebarPinned") === "true";
    if (isPinned) sidebar.classList.add("pinned");

    if (pinBtn && !pinBtn.dataset.bound) {
        pinBtn.dataset.bound = "true";
        pinBtn.addEventListener("click", () => {
            sidebar.classList.toggle("pinned");
            localStorage.setItem("sidebarPinned", sidebar.classList.contains("pinned"));
        });
    }

    if (mobileBtn && !mobileBtn.dataset.bound) {
        mobileBtn.dataset.bound = "true";
        mobileBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            sidebar.classList.toggle("mobile-open");
        });

        document.addEventListener("click", (event) => {
            if (
                window.innerWidth <= 980 &&
                sidebar.classList.contains("mobile-open") &&
                !sidebar.contains(event.target) &&
                event.target !== mobileBtn
            ) {
                sidebar.classList.remove("mobile-open");
            }
        });
    }
}

function setupPublicNav() {
    const toggleBtn = document.getElementById("publicMobileToggle");
    const navLinks = document.getElementById("publicNavLinks");

    if (!toggleBtn || !navLinks || toggleBtn.dataset.bound) return;

    toggleBtn.dataset.bound = "true";

    toggleBtn.addEventListener("click", function (event) {
        event.stopPropagation();
        navLinks.classList.toggle("open");
    });

    document.addEventListener("click", function (event) {
        if (navLinks.classList.contains("open") && !navLinks.contains(event.target) && event.target !== toggleBtn) {
            navLinks.classList.remove("open");
        }
    });
}

function setupUserDropdown() {
    const btn = document.getElementById("userMenuBtn");
    const dropdown = document.getElementById("userDropdown");

    if (!btn || !dropdown || btn.dataset.bound) return;

    btn.dataset.bound = "true";

    btn.addEventListener("click", function (event) {
        event.stopPropagation();
        dropdown.classList.toggle("open");
    });

    document.addEventListener("click", function () {
        dropdown.classList.remove("open");
    });
}

/* ================= SPA ROUTING ================= */
function setupSPARouter() {
    document.body.addEventListener("click", (event) => {
        const link = event.target.closest("a");

        if (
            link &&
            link.href &&
            link.href.startsWith(window.location.origin) &&
            !link.getAttribute("target") &&
            !link.href.includes("/logout")
        ) {
            event.preventDefault();
            navigate(link.href);
        }
    });

    window.addEventListener("popstate", () => {
        navigate(window.location.href, false);
    });
}

async function navigate(url, push = true) {
    startLoader();
    setupUserDropdown();
    setupCropWiseBot();
    setupCommunityChat();
    setupPublicNav();
    setupThemeToggle();

    try {
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) throw new Error("Navigation failed.");

        const html = await response.text();
        progressLoader(70);

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");

        document.title = doc.title;

        const newMain = doc.querySelector("main.page");
        const currentMain = document.querySelector("main.page");

        if (newMain && currentMain) {
            currentMain.innerHTML = newMain.innerHTML;
            currentMain.style.animation = "none";
            currentMain.offsetHeight;
            currentMain.style.animation = "pageIn 0.45s ease both";
        }

        const newFooter = doc.querySelector(".site-footer");
        const currentFooter = document.querySelector(".site-footer");

        if (newFooter && currentFooter) {
            currentFooter.innerHTML = newFooter.innerHTML;
        }

        if (push) {
            history.pushState(null, "", response.url);
        }

        initApp(document);
        setupLgaDetection();
        setupLgaChat();

        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        console.error("SPA navigation failed. Hard reload:", error);
        window.location.href = url;
    } finally {
        finishLoader();
    }
}

/* ================= FORMS & ALERTS ================= */
function bindAjaxForms(root) {
    const forms = root.querySelectorAll(".ajax-form");

    forms.forEach((form) => {
        if (form.dataset.bound) return;
        form.dataset.bound = "true";

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const button = form.querySelector("button[type='submit']");
            const alertBox = form.querySelector(".ajax-alert") || document.getElementById("ajaxAlert");
            const formData = new FormData(form);

            if (button) {
                button.classList.add("loading");
                button.disabled = true;
            }

            if (alertBox) {
                alertBox.className = "ajax-alert";
                alertBox.textContent = "";
            }

            startLoader();

            try {
                const response = await fetch(form.action || window.location.href, {
                    method: form.method || "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const contentType = response.headers.get("content-type") || "";
                const data = contentType.includes("application/json")
                    ? await response.json()
                    : { ok: response.ok, redirect: response.url };

                progressLoader(80);

                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "Request failed.");
                }

                if (alertBox) {
                    alertBox.className = "ajax-alert success show";
                    alertBox.textContent = data.message || "Successful.";
                }

                if (data.redirect) {
                    setTimeout(() => navigate(data.redirect), 450);
                } else if (form.dataset.reload) {
                    setTimeout(() => navigate(window.location.href), 350);
                }
            } catch (error) {
                if (alertBox) {
                    alertBox.className = "ajax-alert error show";
                    alertBox.textContent = error.message || "Something went wrong.";
                }
            } finally {
                if (button) {
                    button.classList.remove("loading");
                    button.disabled = false;
                }

                finishLoader();
            }
        });
    });
}

function autoHideFlashes(root) {
    const flashMessages = root.querySelectorAll(".flash");

    flashMessages.forEach((flash) => {
        setTimeout(() => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-8px)";
            flash.style.transition = "opacity 0.3s ease, transform 0.3s ease";
            setTimeout(() => flash.remove(), 300);
        }, 4500);
    });
}

/* ================= LGA & LOCATION ================= */
function setupLgaDetection() {
    const detectLgaBtn = document.getElementById("detectLgaBtn");
    const lgaSelect = document.getElementById("lgaSelect");
    const lgaDetectStatus = document.getElementById("lgaDetectStatus");

    if (!detectLgaBtn || !lgaSelect || !lgaDetectStatus || detectLgaBtn.dataset.bound) return;

    detectLgaBtn.dataset.bound = "true";

    detectLgaBtn.addEventListener("click", function () {
        if (!navigator.geolocation) {
            lgaDetectStatus.textContent = "Your browser does not support location detection. Please select your LGA manually.";
            return;
        }

        detectLgaBtn.disabled = true;
        detectLgaBtn.textContent = "Detecting...";

        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const matched = estimateLagosLga(lat, lon);

                if (matched) {
                    lgaSelect.value = matched.name;
                    lgaDetectStatus.textContent = `Detected approximate LGA: ${matched.name}. You can change it if this is not correct.`;
                } else {
                    lgaDetectStatus.textContent = "CropWise could not match your location to Ikorodu, Epe, or Badagry. Please select manually.";
                }

                detectLgaBtn.disabled = false;
                detectLgaBtn.textContent = "Detect my LGA";
            },
            function () {
                lgaDetectStatus.textContent = "Location permission was denied or unavailable. Please select your LGA manually.";
                detectLgaBtn.disabled = false;
                detectLgaBtn.textContent = "Detect my LGA";
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    });
}

function estimateLagosLga(lat, lon) {
    const areas = [
        { name: "Ikorodu", minLat: 6.55, maxLat: 6.75, minLon: 3.40, maxLon: 3.70 },
        { name: "Epe", minLat: 6.45, maxLat: 6.75, minLon: 3.85, maxLon: 4.20 },
        { name: "Badagry", minLat: 6.35, maxLat: 6.60, minLon: 2.70, maxLon: 3.10 }
    ];

    return areas.find((area) => {
        return lat >= area.minLat &&
               lat <= area.maxLat &&
               lon >= area.minLon &&
               lon <= area.maxLon;
    });
}

/* ================= LGA COMMUNITY CHAT ================= */
function setupLgaChat() {
    const chatFab = document.getElementById("chatFab");
    const chatPanel = document.getElementById("chatPanel");
    const chatCloseBtn = document.getElementById("chatCloseBtn");
    const chatMessages = document.getElementById("chatMessages");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");

    if (!chatFab || !chatPanel) return;

    if (!chatFab.dataset.bound) {
        chatFab.dataset.bound = "true";
        chatFab.addEventListener("click", () => {
            chatPanel.classList.add("open");
            loadLgaMessages();
        });
    }

    if (chatCloseBtn && !chatCloseBtn.dataset.bound) {
        chatCloseBtn.dataset.bound = "true";
        chatCloseBtn.addEventListener("click", () => {
            chatPanel.classList.remove("open");
        });
    }

    if (chatForm && chatInput && !chatForm.dataset.bound) {
        chatForm.dataset.bound = "true";

        chatForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const formData = new FormData(chatForm);

            try {
                const response = await fetch("/chat/messages", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "Message failed.");
                }

                chatInput.value = "";
                await loadLgaMessages();
            } catch (error) {
                alert(error.message || "Could not send message.");
            }
        });
    }

    async function loadLgaMessages() {
        if (!chatMessages) return;

        try {
            const response = await fetch("/chat/messages", {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (!data.ok) throw new Error("Could not load messages.");

            if (!data.messages.length) {
                chatMessages.innerHTML = `<p class="chat-empty">No messages yet. Start the discussion for ${escapeHtml(data.lga)} farmers.</p>`;
                return;
            }

            chatMessages.innerHTML = data.messages.map((item) => {
                return `
                    <div class="chat-message">
                        <div class="chat-meta">
                            <strong>${escapeHtml(item.name)}</strong>
                            <span>${escapeHtml(item.created_at)}</span>
                        </div>
                        <p>${escapeHtml(item.message)}</p>
                    </div>
                `;
            }).join("");

            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            chatMessages.innerHTML = `<p class="chat-empty">Unable to load chat messages.</p>`;
        }
    }
}

function setupCommunityChat() {
    const messagesBox = document.getElementById("communityMessages");
    const form = document.getElementById("communityForm");
    const input = document.getElementById("communityInput");
    const refreshBtn = document.getElementById("communityRefreshBtn");

    if (!messagesBox || !form || !input) return;

    async function loadMessages() {
        try {
            const response = await fetch("/community/messages", {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (!response.ok || !data.ok) {
                throw new Error(data.message || "Could not load messages.");
            }

            if (!data.messages.length) {
                messagesBox.innerHTML = `<p class="community-empty">No messages yet. Start the discussion for ${escapeHtml(data.lga)} farmers.</p>`;
                return;
            }

            messagesBox.innerHTML = data.messages.map((item) => {
                return `
                    <div class="community-message ${item.is_me ? "mine" : ""}">
                        <div class="community-message-meta">
                            <strong>${escapeHtml(item.name)}</strong>
                            <span>${escapeHtml(item.created_at)}</span>
                        </div>
                        <p>${escapeHtml(item.message)}</p>
                    </div>
                `;
            }).join("");

            messagesBox.scrollTop = messagesBox.scrollHeight;
        } catch (error) {
            messagesBox.innerHTML = `<p class="community-empty">Unable to load community messages.</p>`;
        }
    }

    if (!form.dataset.bound) {
        form.dataset.bound = "true";

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const text = input.value.trim();

            if (!text) return;

            const formData = new FormData();
            formData.append("message", text);

            input.value = "";

            try {
                const response = await fetch("/community/messages", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "Message failed.");
                }

                await loadMessages();
            } catch (error) {
                alert(error.message || "Could not send message.");
            }
        });
    }

    if (refreshBtn && !refreshBtn.dataset.bound) {
        refreshBtn.dataset.bound = "true";
        refreshBtn.addEventListener("click", loadMessages);
    }

    loadMessages();

    if (!messagesBox.dataset.polling) {
        messagesBox.dataset.polling = "true";

        window.setInterval(function () {
            if (document.getElementById("communityMessages")) {
                loadMessages();
            }
        }, 8000);
    }
}

/* ================= CROPWISE BOT ================= */
function setupCropWiseBot() {
    const botFab = document.getElementById("botFab");
    const botPanel = document.getElementById("botPanel");
    const botCloseBtn = document.getElementById("botCloseBtn");
    const botMessages = document.getElementById("botMessages");
    const botForm = document.getElementById("botForm");
    const botInput = document.getElementById("botInput");

    if (!botFab || !botPanel || !botMessages || !botForm || !botInput) return;

    if (!botFab.dataset.bound) {
        botFab.dataset.bound = "true";

        botFab.addEventListener("click", function () {
            botPanel.classList.add("open");
            botInput.focus();
        });
    }

    if (botCloseBtn && !botCloseBtn.dataset.bound) {
        botCloseBtn.dataset.bound = "true";

        botCloseBtn.addEventListener("click", function () {
            botPanel.classList.remove("open");
        });
    }

    if (!botForm.dataset.bound) {
        botForm.dataset.bound = "true";

        botForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const text = botInput.value.trim();

            if (!text) return;

            appendBotMessage("user", text);
            botInput.value = "";

            const thinking = appendBotMessage("assistant", "Thinking...");

            try {
                const formData = new FormData();
                formData.append("message", text);

                const response = await fetch("/bot/message", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "Assistant failed.");
                }

                thinking.querySelector("p").textContent = data.reply;
            } catch (error) {
                thinking.querySelector("p").textContent = error.message || "I could not answer that.";
            }

            botMessages.scrollTop = botMessages.scrollHeight;
        });
    }

    function appendBotMessage(type, text) {
        const div = document.createElement("div");
        div.className = `bot-message ${type}`;

        const p = document.createElement("p");
        p.textContent = text;

        div.appendChild(p);
        botMessages.appendChild(div);
        botMessages.scrollTop = botMessages.scrollHeight;

        return div;
    }
}

/* ================= UTILS & LOADERS ================= */
function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function startLoader() {
    progressBar.style.opacity = "1";
    progressBar.style.width = "30%";
}

function progressLoader(percentage) {
    progressBar.style.width = `${percentage}%`;
}

function finishLoader() {
    progressBar.style.width = "100%";

    setTimeout(() => {
        progressBar.style.opacity = "0";

        setTimeout(() => {
            progressBar.style.width = "0";
        }, 300);
    }, 300);
}

function setupSplashScreen() {
    const splash = document.getElementById("appSplash");

    if (!splash) return;

    const minimumDisplayTime = 900;

    window.setTimeout(function () {
        splash.classList.add("hide");

        window.setTimeout(function () {
            splash.remove();
        }, 500);
    }, minimumDisplayTime);
}