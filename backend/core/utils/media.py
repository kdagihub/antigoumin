def build_media_url(request, file_field) -> str | None:
    if not file_field:
        return None
    return request.build_absolute_uri(file_field.url)
