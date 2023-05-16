from utils import current_milli_time
from applications.image_classification.squeezenet_module import SqueezeNet
from protos import benchmark_pb2 as pb2
import base64
from io import BytesIO
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models

squeezenet = models.squeezenet1_0(pretrained=True)
torch.save(squeezenet.state_dict(), 'squeezenet.pth')


def classify_image(request, request_received_time_ms):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    model = SqueezeNet(num_classes=1000)
    # Load the state dictionary into the model
    model.load_state_dict(torch.load('squeezenet.pth', map_location=torch.device('cpu')))


    output = model(request.image)
    prob, predicted = torch.max(output, 1)

    classification_response = pb2.ImageClassificationResponse()
    classification_response.top_category_id = int(predicted.item())
    classification_response.top_category_probability = int(prob.item() * 100)
    classification_response.request_time_ms = request.request_time_ms
    classification_response.request_received_time_ms = request_received_time_ms
    classification_response.response_time_ms = current_milli_time()

    return classification_response
