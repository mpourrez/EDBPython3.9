from utils import current_milli_time
from protos import benchmark_pb2 as pb2
import torch
from PIL import Image
import io
import base64
from torchvision import transforms
import torchvision.models as models

# define the transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# load the alexnet model
alexnet = models.alexnet(pretrained=True)

# set the model to evaluation mode
alexnet.eval()

def classify(request, request_received_time_ms):
    # decode the base64string to bytes
    image_data = base64.b64decode(request.image)

    # read bytes data into a PIL Image object
    image = Image.open(io.BytesIO(image_data))

    # apply the transforms to the image
    input_image = transform(image).unsqueeze(0)

    # classify the input image
    with torch.no_grad():
        output = alexnet(input_image)

    # get the class probabilities
    probabilities = torch.nn.functional.softmax(output[0], dim=0)

    # get the top 5 predictions
    top_prob, top_catid = torch.topk(probabilities, 1)

    classification_response = pb2.ImageClassificationResponse()
    classification_response.top_category_id = top_catid[0]
    classification_response.top_category_probability = top_prob[0] * 100
    classification_response.request_time_ms = request.request_time_ms
    classification_response.request_received_time_ms = request_received_time_ms
    classification_response.response_time_ms = current_milli_time()

    return classification_response



