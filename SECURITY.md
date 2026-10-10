# Security and privacy notes

This repository contains a static, browser-side application. HTML and JavaScript delivered to a browser are public to that browser's user; they cannot keep embedded credentials confidential.

## Important limitations

- The optional Google Gemini API key is entered by the user and stored in browser `localStorage`. It is not a server-side secret store. Any script executing on the same origin may be able to read browser storage. Never commit a real key or use a privileged production key in this front end.
- When the optional Gemini integration is used, diagnostic text or image content is sent from the browser to Google's Generative Language API. Do not submit sensitive personal, customer, or confidential data unless the data owner and applicable privacy requirements permit it.
- Booking, remote-support, and credit-related state is client-side `localStorage`; it is not shared across devices and is not authoritative for payments, identity, or service operations. The current workspace has no application backend.

## Reporting a vulnerability

Do not post credentials, personal data, or an exploitable vulnerability in a public issue. After the repository is created, the owner should enable GitHub private vulnerability reporting or provide another private contact route. If a credential is ever exposed, revoke/rotate it immediately; deleting the current file does not remove it from Git history.
