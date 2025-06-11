from flask import Flask, send_file, request, render_template, redirect, url_for
import os
import shutil
import logging
from send2trash import send2trash 

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "base")
GOOD_DIR = os.path.join(ROOT_DIR, "bagus")
BAD_DIR = os.path.join(ROOT_DIR, "jelek")
SCENERY_DIR = os.path.join(ROOT_DIR, "scenery")
ALLOWED_EXT = ('.webp', ".png", ".jpg", ".jpeg")

def get_images_from_directory(directory):
    try:
        images = [f for f in os.listdir(directory) if f.lower().endswith(ALLOWED_EXT)]
        logging.debug(f"Images in {directory}: {images}")
        return images
    except Exception as e:
        logging.error(f"Error getting images from {directory}: {str(e)}")
        return []

current_folder = None
images = []
index = 0
app = Flask(__name__)

@app.route("/")
def index_view():
    if not current_folder:
        logging.debug("No folder selected, showing folder selection page.")
        return render_template("select_folder.html")
    if not images:
        logging.debug("No images found in the current folder.")
        return render_template("index.html", message="No images found in this directory")
    folder_type = ""
    if current_folder == BASE_DIR:
        folder_type = "base"
    elif current_folder == GOOD_DIR:
        folder_type = "good"
    elif current_folder == BAD_DIR:
        folder_type = "bad"
    elif current_folder == SCENERY_DIR:
        folder_type = "scenery"
    logging.debug(f"Current folder: {current_folder}, Current image: {images[index]}, Folder type: {folder_type}")
    return render_template("index.html", filename=images[index], folder_type=folder_type)

@app.route("/folder/<folder_name>")
def select_folder(folder_name):
    global current_folder, images, index
    if folder_name == "good":
        current_folder = GOOD_DIR
    elif folder_name == "bad":
        current_folder = BAD_DIR
    elif folder_name == "scenery":
        current_folder = SCENERY_DIR
    elif folder_name == "base":
        current_folder = BASE_DIR
    else:
        logging.error(f"Invalid folder selected: {folder_name}")
        return render_template("index.html", message="No images found in this directory")
    logging.debug(f"Selected folder: {current_folder}")
    images = get_images_from_directory(current_folder)
    index = 0
    if not images:
        logging.debug(f"No images found in this directory: {current_folder}")
        return render_template("index.html", message="No images found in this directory")
    logging.debug(f"Redirecting to index_view with current_folder: {current_folder}")
    return redirect(url_for('index_view'))

@app.route("/reset")
def reset():
    global current_folder, images, index
    current_folder = None
    images = []
    index = 0
    logging.debug("State reset: returning to folder selection.")
    return redirect(url_for("index_view"))

@app.route("/image")
def image():
    if not images or not current_folder:
        logging.debug("No images available to display or current_folder is None.")
        return "", 404
    logging.debug(f"Serving image: {images[index]} from {current_folder}")
    return send_file(os.path.join(current_folder, images[index]), mimetype='image/webp')

@app.route("/next")
def next_image():
    global index
    if images:
        index = (index + 1) % len(images)
        logging.debug(f"Moved to next image: {images[index]}")
    else:
        logging.debug("No images to navigate.")
    return redirect(url_for('index_view'))

@app.route("/prev")
def prev_image():
    global index
    if images:
        index = (index - 1) % len(images)
        logging.debug(f"Moved to previous image: {images[index]}")
    else:
        logging.debug("No images to navigate.")
    return redirect(url_for('index_view'))

@app.route("/move")
def move():
    global images, index, current_folder
    if not images:
        logging.debug("No images to move.")
        return "", 400
    dest = request.args.get("to")
    allowed_moves = {
        BASE_DIR: {"good": GOOD_DIR, "bad": BAD_DIR, "scenery": SCENERY_DIR},
        GOOD_DIR: {"base": BASE_DIR, "bad": BAD_DIR, "scenery": SCENERY_DIR},
        BAD_DIR: {"base": BASE_DIR, "good": GOOD_DIR, "scenery": SCENERY_DIR},
        SCENERY_DIR: {"base": BASE_DIR, "good": GOOD_DIR, "bad": BAD_DIR}
    }
    if current_folder not in allowed_moves or dest not in allowed_moves[current_folder]:
        logging.error(f"Invalid move from {current_folder} to {dest}")
        return "Invalid move", 400
    target_dir = allowed_moves[current_folder][dest]
    src_path = os.path.join(current_folder, images[index])
    dst_path = os.path.join(target_dir, images[index])
    try:
        shutil.move(src_path, dst_path)
        logging.debug(f"Moved file from {src_path} to {dst_path}")
    except Exception as e:
        logging.error(f"Error moving file: {str(e)}")
        return f"Error moving file: {str(e)}", 500
    del images[index]
    if index >= len(images):
        index = max(0, len(images) - 1)
    logging.debug(f"Updated index: {index}")
    return "OK"

@app.route("/delete")
def delete():
    global images, index, current_folder
    if not images or not current_folder:
        logging.debug("No images to delete or current_folder is None.")
        return "", 400
    try:
        file_path = os.path.join(current_folder, images[index])
        send2trash(file_path)
        logging.debug(f"Deleted file: {images[index]} from {current_folder}")
    except Exception as e:
        logging.error(f"Error deleting file: {str(e)}")
        return f"Error deleting file: {str(e)}", 500
    del images[index]
    if index >= len(images):
        index = max(0, len(images) - 1)
    logging.debug(f"Updated index: {index}")
    return "Deleted"

if __name__ == "__main__":
    app.run(debug=True, port=5051)
