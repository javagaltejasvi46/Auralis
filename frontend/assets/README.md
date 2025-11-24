# Assets Folder

## Logo Instructions

Place your logo file here with the name: **`logo.png`**

### Recommended Specifications:

- **Format**: PNG (with transparent background preferred)
- **Size**: 512x512 pixels or 1024x1024 pixels
- **File name**: `logo.png` (exactly this name)

### Where the logo appears:

- Login Screen (120x120 pixels)
- Register Screen (80x80 pixels)

### If you want to use a different file name or format:

Edit these files:

- `frontend/src/screens/LoginScreen.tsx` (line with `require('../../assets/logo.png')`)
- `frontend/src/screens/RegisterScreen.tsx` (line with `require('../../assets/logo.png')`)

Change `logo.png` to your filename (e.g., `logo.jpg`, `my-logo.png`, etc.)

### Supported formats:

- PNG (recommended)
- JPG/JPEG
- SVG (requires additional setup)
