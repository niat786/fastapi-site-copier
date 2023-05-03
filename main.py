from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import subprocess, os, shutil, zipfile, random, string
from urllib.parse import urlparse, quote

app = FastAPI()


@app.get("/download-website")
async def download_website(url: str):
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    extension = os.path.splitext(basename)[1]

    if extension == "" or extension == ".html" or extension == ".htm":
        random_string = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=5)
        )
        folder = "templates/" + random_string + "/" + parsed_url.netloc

        try:
            subprocess.run(["node", "copy.js", url, folder])
            if os.path.isdir(folder):
                return {
                    "message": "success",
                    "status": 200,
                    "folder": folder,
                }
            else:
                return {"message": "error", "status": 404}
        except:
            return {"message": "error", "status": 404}
    else:
        return {"message": "error", "status": 404}


@app.get("/zip-folder")
async def zip_folder(folder_path: str):
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    # Create a temporary directory to store the zip file
    tmp_dir = os.path.join(os.path.dirname(folder_path), "__tmp__")
    os.makedirs(tmp_dir, exist_ok=True)

    # Get the name of the folder to use as the zip file name
    folder_name = os.path.basename(folder_path)

    # Create the zip file
    zip_file_path = os.path.join(tmp_dir, f"{folder_name}.zip")
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

    # Read the zip file contents
    with open(zip_file_path, "rb") as zip_file:
        zip_file_contents = zip_file.read()

    # Remove the temporary directory and zip file
    # shutil.rmtree(tmp_dir)

    # Return the zip file as a streaming response
    file_like = open(zip_file_path, mode="rb")
    headers = {"Content-Disposition": f'attachment; filename="{folder_name}.zip"'}
    return StreamingResponse(file_like, media_type="application/zip", headers=headers)
