# Image Dataset Curator

A web-based application for efficiently curating and organizing image datasets. This tool allows you to quickly sort images into different categories through an intuitive web interface with keyboard shortcuts for rapid classification.

## Features

- **Web-based Interface**: Clean, modern UI with dark theme optimized for image viewing
- **Keyboard Shortcuts**: Fast navigation and categorization using keyboard hotkeys
- **Multiple Categories**: Organize images into four categories:
  - **Base**: Initial/unsorted images
  - **Good (Bagus)**: High-quality/approved images
  - **Bad (Jelek)**: Low-quality/rejected images
  - **Scenery**: Landscape/scenery images
- **Image Navigation**: Browse through images with next/previous controls
- **Safe Deletion**: Images are moved to trash (not permanently deleted)
- **Supported Formats**: WebP, PNG, JPG, JPEG
- **Responsive Design**: Works on different screen sizes

## Directory Structure

```
pixiv_safe_batch_005/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── base/                 # Initial/unsorted images
├── bagus/               # Good/approved images
├── jelek/               # Bad/rejected images
├── scenery/             # Scenery/landscape images
├── static/              # Static assets (CSS, JS)
└── templates/           # HTML templates
    ├── index.html       # Main image viewer
    └── select_folder.html # Folder selection page
```

## Installation

1. **Clone/download this repository**

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure directories exist:**
   The application expects these directories to exist:
   - `base/` - for initial images
   - `bagus/` - for good images
   - `jelek/` - for bad images
   - `scenery/` - for scenery images

## Usage

1. **Start the application:**

   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**

   ```
   http://localhost:5051
   ```

3. **Select a folder** to start curating images from that category

4. **Use keyboard shortcuts for efficient sorting:**

### Keyboard Shortcuts

#### Navigation

- **Arrow Left** / **Arrow Right**: Navigate between images
- **Escape**: Return to folder selection

#### From Base folder:

- **G**: Move to Good (bagus)
- **B**: Move to Bad (jelek)
- **S**: Move to Scenery
- **Delete**: Delete image

#### From Good folder:

- **R**: Return to Base
- **B**: Move to Bad (jelek)
- **S**: Move to Scenery
- **Delete**: Delete image

#### From Bad folder:

- **R**: Return to Base
- **G**: Move to Good (bagus)
- **S**: Move to Scenery
- **Delete**: Delete image

#### From Scenery folder:

- **R**: Return to Base
- **G**: Move to Good (bagus)
- **B**: Move to Bad (jelek)
- **Delete**: Delete image

## Workflow

1. **Place images to sort in the `base/` directory**
2. **Start the application and select "Base" folder**
3. **Review each image and use keyboard shortcuts to categorize:**
   - Press **G** for good images
   - Press **B** for bad images
   - Press **S** for scenery images
   - Press **Delete** to remove unwanted images
4. **Navigate with arrow keys between images**
5. **Use Escape to switch between different folders**

## API Endpoints

- `GET /` - Main page (folder selection or image viewer)
- `GET /folder/<folder_name>` - Select working folder
- `GET /image` - Serve current image
- `GET /next` - Navigate to next image
- `GET /prev` - Navigate to previous image
- `GET /move?to=<destination>` - Move current image to destination folder
- `GET /delete` - Delete current image (move to trash)
- `GET /reset` - Reset session and return to folder selection

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript
- **Image Handling**: PIL-compatible formats
- **Safe Deletion**: Uses `send2trash` library
- **Logging**: Comprehensive debug logging

## Dependencies

- **Flask**: Web framework
- **Flask-Cors**: Cross-origin resource sharing
- **send2trash**: Safe file deletion
- **TailwindCSS**: UI styling (loaded via CDN)

## Development

The application runs in debug mode by default on port 5051. Logs are output to the console with detailed information about operations.

## Safety Features

- Images are moved to system trash instead of permanent deletion
- Comprehensive error handling and logging
- Input validation for file operations
- Safe file path handling

## Use Cases

- **Dataset Preparation**: Sort images for machine learning training
- **Photo Organization**: Quickly categorize large photo collections
- **Content Moderation**: Separate appropriate/inappropriate content
- **Quality Control**: Filter high/low quality images
- **Art Curation**: Organize artwork by type or quality

## License

This project is provided as-is for educational and personal use.
