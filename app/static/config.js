// Optional deployment setting.
//
// Normally the IB Marker server serves this page itself and this value stays empty.
// If you host the page somewhere else (for example on Netlify) and run the API on
// another host (for example Render), put the API's full address here, without a
// trailing slash, and set IB_CORS_ORIGINS on the API server to the page's address.
//
//   window.IB_MARKER_API = "https://ib-marker.onrender.com";
window.IB_MARKER_API = "";
