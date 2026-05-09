const CACHE_NAME = "cropwise-cache-v2";
const OFFLINE_URL = "/offline";

const APP_SHELL = [
    "/",
    "/login",
    "/signup",
    "/offline",
    "/static/css/style.css",
    "/static/js/main.js",
    "/static/manifest.json",
    "/static/icons/cropwise-icon.svg",
    "/static/icons/cropwise-icon-192.png",
    "/static/icons/cropwise-icon-512.png"
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            );
        })
    );

    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    if (url.origin !== location.origin) {
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    return response;
                })
                .catch(() => {
                    return caches.match(request).then((cached) => {
                        return cached || caches.match(OFFLINE_URL);
                    });
                })
        );
        return;
    }

    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) {
                return cached;
            }

            return fetch(request)
                .then((response) => {
                    if (!response || response.status !== 200) {
                        return response;
                    }

                    const clone = response.clone();

                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, clone);
                    });

                    return response;
                })
                .catch(() => caches.match(OFFLINE_URL));
        })
    );
});