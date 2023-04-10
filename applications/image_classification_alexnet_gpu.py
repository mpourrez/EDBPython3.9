from utils import current_milli_time
from protos import benchmark_pb2 as pb2
import torch
from PIL import Image
import io
import base64
import torchvision

# Load AlexNet pre-trained model
model = torchvision.models.alexnet(pretrained=True)

# Set the model to evaluation mode
model.eval()

# Check if CUDA is available
if torch.cuda.is_available():
    # If CUDA is available, use GPU
    device = torch.device("cuda")
    print("GPU was Found!")
else:
    # If CUDA is not available, use CPU
    device = torch.device("cpu")
    print("Only CPU was Found!")

# Move the model to the GPU
model.to(device)


def classify(request, request_received_time_ms):
    # decode the base64string to bytes
    image_data = base64.b64decode(request.image)

    # read bytes data into a PIL Image object
    image = Image.open(io.BytesIO(image_data))
    image = torchvision.transforms.ToTensor()(image)
    image = image.unsqueeze(0)

    # apply the transforms to the image
    input_image = torchvision.transforms.transform(image).unsqueeze(0)

    # Move the input image to the GPU
    image = input_image.to(device)

    # Make a prediction
    with torch.no_grad():
        output = model(image)

    # Get the predicted class index
    top_prob, predicted = torch.max(output.data, 1)

    classification_response = pb2.ImageClassificationResponse()
    classification_response.top_category_id = predicted
    classification_response.top_category_probability = top_prob[0] * 100
    classification_response.request_time_ms = request.request_time_ms
    classification_response.request_received_time_ms = request_received_time_ms
    classification_response.response_time_ms = current_milli_time()

    return classification_response
