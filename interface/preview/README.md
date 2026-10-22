# RetroVerse interface preview — v0.1

**Offline-first standalone HTML/CSS/JavaScript prototype. Not a bootable operating system.**

Open `interface/preview/index.html` in any current desktop browser to explore the initial UI. No server, account or internet connection is required.

## Present features
- Home screen, game library placeholder, Online lobby placeholders, Settings
- Keyboard arrow navigation, Enter selection and Escape to Home
- Basic gamepad D-pad/A/B input through the browser Gamepad API when available
- High-contrast setting for television readability
- Responsive layout for desktop and smaller screens

## Important limitations
- No real ROM scan, RetroArch launcher, account login, matchmaking, achievements, save-state integration or complete accessibility audit
- Gamepad browser support varies and must be tested with actual controllers
- Online lobby tiles are intentionally disabled
- Opening this HTML file does not test the ARM kernel, DRM/Wayland compositor, GPU drivers or actual GameBox video output
- This prototype does **not** modify system storage or boot media

## Engineering path
1. Review offline UX and input navigation using the preview.
2. Write a native Linux frontend or kiosk-based runtime integration once graphics initialization is validated.
3. Implement local library discovery and RetroArch launcher with safe paths and error handling.
4. Add offline save/config management and controller profiles.
5. Integrate with the GameBox boot image only after board-compatible display and bootloader testing.

Copyright/artwork: prototype uses text and CSS geometry only, no game ROMs, copyrighted box-art, or third-party branding assets.
