# Frontend Documentation (Single Page Application)

This application uses pure JavaScript Single Page Application (SPA) architecture. All views are rendered dynamically in the `<main id="app"></main>` container without page refreshes.

## Architecture & State Managment

The frontend state is tracked globally in a single `state` object inside `static/js/script.js`:

- `token`: Stores the active JSON Web Token (JWT).
- `username`: Stores the logged-in user's handle.
- `currentView`: Dictates which component is active (`auth` or `chat`).

State values are syncronized with the browser's `localStorage` to persist the user session across browser tabs and page reloads.

## Dynamic Views

The interface switches components using a central `render()` engine triggered by state modifications:

1. **`renderAuthView()`**: Renders the credential forms. It toggles dynamically between **Login** and **Register** modes without hitting the backend yet.
2. **`renderChatView()`**: Renders the authenticated chat room interface, user display header and message stream box.

## Network & Authentication Flow

All requests target the `/api/*` endpoints and use asynchronous `fetch` calls:

- **Registration / Login**: Transmits JSON stringified payload data. On a successful login, the recieved `access_token` is injected directly into `localStorage`.
- **Logout**: Dispatches a `POST` request including the `Authorization: Bearer <token>` header to inform the backend token blocklist, then forcefully clears local state caches.

## Design Tokens (`style.css`)

UI styling uses CSS Custom Properties (Variables) located in the `:root` scope for global theme configuration:
- `--bg-main`: Page layout baseline background.
- `--primary` & `--primary-hover`: Interactive buttons and brand colouration.
- `--surface`: Containers and card backdrops.