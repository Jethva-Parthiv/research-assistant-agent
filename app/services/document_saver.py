from app.core.logging import logger
import uuid
from datetime import datetime
from pathlib import Path
from app.core.settings import MD_FILE_STORE_LOCATION



def save_document(
    data: str,
    prefix: str = "Research_Data",
    metadata: dict | None = None,
) -> Path:
    """
    Save research content into a unique markdown file.

    Args:
        data: Markdown content to save.
        prefix: File name prefix.
        metadata: Optional metadata to include at top of file.

    Returns:
        Path to saved markdown file.

    Raises:
        ValueError: If content is empty.
        OSError: If file write fails.
    """

    if not data or not data.strip():
        raise ValueError("Document content cannot be empty.")

    # ----------------------------------
    # Create storage directory
    # ----------------------------------
    save_dir = Path(MD_FILE_STORE_LOCATION)
    save_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------
    # Generate unique filename
    # ----------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6].upper()

    filename = f"{prefix}_{timestamp}_{unique_id}.md"
    file_path = save_dir / filename

    # ----------------------------------
    # Build markdown content
    # ----------------------------------
    md_content = ""

    if metadata:
        md_content += "# Metadata\n\n"

        for key, value in metadata.items():
            md_content += f"- **{key}**: {value}\n"

        md_content += "\n---\n\n"

    md_content += data

    # ----------------------------------
    # Write file
    # ----------------------------------
    try:
        file_path.write_text(
            md_content,
            encoding="utf-8",
        )

        logger.info(
            "Research document saved successfully: %s",
            file_path,
        )

        return file_path

    except Exception as e:
        logger.exception(
            "Failed to save markdown file."
        )
        raise e