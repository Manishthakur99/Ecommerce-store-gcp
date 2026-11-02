"""
Shared helpers for images stored as base64 in MongoDB (product photos, avatars).
"""
import base64


async def encode_upload_to_base64(upload_file) -> tuple[str, str]:
    """Read a FastAPI UploadFile and return (base64_data, content_type)."""
    image_data = await upload_file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    content_type = upload_file.content_type or "image/jpeg"
    return base64_image, content_type


def to_data_url(image_data: str, content_type: str) -> str:
    """Build a data: URL from base64 image data plus its content type."""
    return f"data:{content_type};base64,{image_data}"


def resolve_image_field(document: dict) -> None:
    """
    Mutate `document` in place: ensure `image` is a usable URL, then strip the
    raw binary/base64 fields from the document. `document["id"]` must already be set.

    Uses the existing http(s) URL if there is one, otherwise points at this
    product's dedicated image endpoint rather than embedding the raw binary or base64
    bytes inline — a product list response would otherwise fail serialization or
    ship huge image payloads.
    """
    has_url = bool(document.get("image")) and isinstance(document["image"], str) and document["image"].startswith("http")
    if not has_url:
        has_embedded = (
            (document.get("image_data") and document.get("image_content_type"))
            or (isinstance(document.get("image"), dict) and document["image"].get("data"))
        )
        if has_embedded:
            document["image"] = f"/products/{document['id']}/image"
        elif not isinstance(document.get("image"), str):
            document["image"] = ""
    document.pop("image_data", None)
    document.pop("image_content_type", None)
