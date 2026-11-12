from dotenv import load_dotenv

from imagekitio import ImageKit

import os

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE"),
    public_key=os.getenv("IMAGEKIT_PUBLIC"),
    url_endpoint=os.getenv("IMAGEKIT_URL")
)