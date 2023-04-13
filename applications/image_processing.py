from PIL import Image
from base64 import b64decode, b64encode
import io
from utils import current_milli_time
from protos import benchmark_pb2 as pb2


def resize_image(request, request_received_time_ms):
    byte_array = bytearray(request.image, encoding='utf-8')
    decoded_bytes = b64decode(byte_array)
    # Create an in-memory stream
    stream = io.BytesIO(decoded_bytes)

    # Open the image using PIL
    pil_image = Image.open(stream)
    resized_im = pil_image.resize((400, 400))

    # Create an in-memory stream
    stream = io.BytesIO()

    # Save the image to the stream in PNG format
    resized_im.save(stream, format="PNG")

    # Get the raw bytes of the image from the stream
    image_bytes = stream.getvalue()

    # Encode the image bytes as base64
    encoded_image = b64encode(image_bytes).decode("utf-8")

    processing_response = pb2.ImageProcessingResponse()
    processing_response.resized_image = encoded_image
    processing_response.request_time_ms = request.request_time_ms
    processing_response.request_received_time_ms = request_received_time_ms
    processing_response.response_time_ms = current_milli_time()

    return processing_response
