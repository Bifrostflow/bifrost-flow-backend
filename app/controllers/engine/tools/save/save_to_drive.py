async def save_to_g_drive(creds, filename, filepath, mime_type):
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": filename}
    media = MediaFileUpload(filepath, mimetype=mime_type)

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"File ID: {file.get('id')}")
    return file.get("id")
