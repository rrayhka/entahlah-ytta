from flask import Flask, send_file, request, render_template_string, redirect, url_for
import os
import shutil
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "base")
GOOD_DIR = os.path.join(ROOT_DIR, "bagus")
BAD_DIR = os.path.join(ROOT_DIR, "jelek")
SCENERY_DIR = os.path.join(ROOT_DIR, "scenery")
ALLOWED_EXT = ('.webp', ".png", ".jpg", ".jpeg")

def get_images_from_directory(directory):
    """
    Mengambil semua file gambar dari direktori yang diberikan.
    
    Parameters:
    directory (str): Jalur direktori yang akan di-scan untuk mencari file gambar.
    
    Returns:
    list: Daftar nama file gambar yang ada di direktori tersebut.
    """
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

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Image Viewer</title></head>
<body style="background-color:black; color:white; text-align:center; font-family:sans-serif;">
    <h1>{{ filename }}</h1>
    <img src="/image" style="max-width:90vw;max-height:80vh"/><br><br>
    <button onclick="location.href='/prev'">Prev</button>
    <button onclick="location.href='/next'">Next</button>
    {% if folder_type == "base" %}
    <button onclick="fetch('/move?to=good')">Good (G)</button>
    <button onclick="fetch('/move?to=bad')">Bad (B)</button>
    <button onclick="fetch('/move?to=scenery')">Scenery (S)</button>
    {% elif folder_type == "good" %}
    <button onclick="fetch('/move?to=base')">Base (R)</button>
    <button onclick="fetch('/move?to=bad')">Bad (B)</button>
    <button onclick="fetch('/move?to=scenery')">Scenery (S)</button>
    {% elif folder_type == "bad" %}
    <button onclick="fetch('/move?to=base')">Base (R)</button>
    <button onclick="fetch('/move?to=good')">Good (G)</button>
    <button onclick="fetch('/move?to=scenery')">Scenery (S)</button>
    {% elif folder_type == "scenery" %}
    <button onclick="fetch('/move?to=base')">Base (R)</button>
    <button onclick="fetch('/move?to=good')">Good (G)</button>
    <button onclick="fetch('/move?to=bad')">Bad (B)</button>
    {% endif %}
    <button onclick="fetch('/delete')">Delete (Del)</button>
<script>
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') window.location.href = '/next';
    else if (e.key === 'ArrowLeft') window.location.href = '/prev';
    {% if folder_type == "base" %}
    else if (e.key === 'g') fetch('/move?to=good').then(() => location.reload());
    else if (e.key === 'b') fetch('/move?to=bad').then(() => location.reload());
    else if (e.key === 's') fetch('/move?to=scenery').then(() => location.reload());
    {% elif folder_type == "good" %}
    else if (e.key === 'r') fetch('/move?to=base').then(() => location.reload());
    else if (e.key === 'b') fetch('/move?to=bad').then(() => location.reload());
    else if (e.key === 's') fetch('/move?to=scenery').then(() => location.reload());
    {% elif folder_type == "bad" %}
    else if (e.key === 'r') fetch('/move?to=base').then(() => location.reload());
    else if (e.key === 'g') fetch('/move?to=good').then(() => location.reload());
    else if (e.key === 's') fetch('/move?to=scenery').then(() => location.reload());
    {% elif folder_type == "scenery" %}
    else if (e.key === 'r') fetch('/move?to=base').then(() => location.reload());
    else if (e.key === 'g') fetch('/move?to=good').then(() => location.reload());
    else if (e.key === 'b') fetch('/move?to=bad').then(() => location.reload());
    {% endif %}
    else if (e.key === 'Delete') fetch('/delete').then(() => location.reload());
    else if (e.key === 'Escape') {
        e.preventDefault();
        window.location.href = '/reset';
    }
});
</script>
</body>
</html>
'''

SELECT_FOLDER_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Choose Folder</title></head>
<body style="background-color:black; color:white; text-align:center; font-family:sans-serif;">
    <h1>Select Folder</h1>
    <button onclick="window.location.href='/folder/good'">Good</button>
    <button onclick="window.location.href='/folder/bad'">Bad</button>
    <button onclick="window.location.href='/folder/scenery'">Scenery</button>
    <button onclick="window.location.href='/folder/base'">Base</button>
</body>
</html>
'''

def render_countdown_redirect(message, seconds=5, redirect_url="/reset"):
    """
    Menampilkan pesan perhitungan mundur sebelum melakukan redirect ke URL yang ditentukan.
    
    Parameters:
    message (str): Pesan yang akan ditampilkan selama perhitungan mundur.
    seconds (int): Jumlah detik sebelum dilakukan redirect. Defaultnya adalah 5.
    redirect_url (str): URL yang akan dituju setelah perhitungan mundur selesai. Defaultnya adalah "/reset".
    
    Returns:
    str: HTML string untuk halaman perhitungan mundur.
    """
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head><title>Redirecting...</title></head>
    <body style="background-color:black; color:white; text-align:center; font-family:sans-serif;">
        <h1>{message}</h1>
        <p>Redirecting in <span id="countdown">{seconds}</span> seconds...</p>
        <script>
            let seconds = {seconds};
            const countdown = document.getElementById("countdown");
            const interval = setInterval(() => {{
                seconds--;
                countdown.textContent = seconds;
                if (seconds <= 0) {{
                    clearInterval(interval);
                    window.location.href = "{redirect_url}";
                }}
            }}, 1000);
        </script>
    </body>
    </html>
    ''')

@app.route("/")
def index_view():
    """
    Tampilan utama aplikasi yang menampilkan gambar saat ini dan tombol navigasi serta opsi untuk memindahkan atau menghapus gambar.
    
    Returns:
    str: Halaman HTML yang menampilkan gambar saat ini dan tombol navigasi.
    """
    if not current_folder:
        logging.debug("No folder selected, showing folder selection page.")
        return render_template_string(SELECT_FOLDER_HTML)
    if not images:
        logging.debug("No images found in the current folder.")
        return render_countdown_redirect("No images found in this directory")
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
    return render_template_string(HTML, filename=images[index], folder_type=folder_type)

@app.route("/folder/<folder_name>")
def select_folder(folder_name):
    """
    Memilih folder yang akan digunakan untuk menampilkan gambar.
    
    Parameters:
    folder_name (str): Nama folder yang akan dipilih. Dapat berupa "good", "bad", "scenery", atau "base".
    
    Returns:
    str: Redirect ke halaman tampilan utama dengan folder yang dipilih.
    """
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
        return render_countdown_redirect("No images found in this directory")
    logging.debug(f"Selected folder: {current_folder}")
    images = get_images_from_directory(current_folder)
    index = 0
    if not images:
        logging.debug(f"No images found in this directory: {current_folder}")
        return render_countdown_redirect("No images found in this directory")
    logging.debug(f"Redirecting to index_view with current_folder: {current_folder}")
    return redirect(url_for('index_view'))

@app.route("/reset")
def reset():
    """
    Mengatur ulang state aplikasi ke kondisi awal.
    
    Returns:
    str: Redirect ke halaman pemilihan folder.
    """
    global current_folder, images, index
    current_folder = None
    images = []
    index = 0
    logging.debug("State reset: returning to folder selection.")
    return redirect(url_for("index_view"))

@app.route("/image")
def image():
    """
    Mengembalikan gambar saat ini dalam bentuk HTTP response.
    
    Returns:
    werkzeug.wrappers.response.Response: Gambar yang diminta dalam format HTTP response.
    """
    if not images:
        logging.debug("No images available to display.")
        return "", 404
    logging.debug(f"Serving image: {images[index]} from {current_folder}")
    return send_file(os.path.join(current_folder, images[index]), mimetype='image/webp')

@app.route("/next")
def next_image():
    """
    Pergi ke gambar berikutnya dalam daftar gambar.
    
    Returns:
    str: Redirect ke halaman tampilan utama.
    """
    global index
    if images:
        index = (index + 1) % len(images)
        logging.debug(f"Moved to next image: {images[index]}")
    else:
        logging.debug("No images to navigate.")
    return redirect(url_for('index_view'))

@app.route("/prev")
def prev_image():
    """
    Pergi ke gambar sebelumnya dalam daftar gambar.
    
    Returns:
    str: Redirect ke halaman tampilan utama.
    """
    global index
    if images:
        index = (index - 1) % len(images)
        logging.debug(f"Moved to previous image: {images[index]}")
    else:
        logging.debug("No images to navigate.")
    return redirect(url_for('index_view'))

@app.route("/move")
def move():
    """
    Memindahkan gambar saat ini ke folder yang ditentukan.
    
    Returns:
    str: "OK" jika pindah berhasil, atau pesan kesalahan jika gagal.
    """
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
    """
    Menghapus gambar saat ini dari folder.
    
    Returns:
    str: "Deleted" jika penghapusan berhasil, atau pesan kesalahan jika gagal.
    """
    global images, index, current_folder
    if not images:
        logging.debug("No images to delete.")
        return "", 400
    try:
        os.remove(os.path.join(current_folder, images[index]))
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
