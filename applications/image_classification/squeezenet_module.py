import base64
from io import BytesIO
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models


class SqueezeNet(nn.Module):
    def __init__(self, num_classes=2):
        super(SqueezeNet, self).__init__()
        self.model = models.squeezenet1_1(pretrained=True)
        self.model.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=(1, 1), stride=(1, 1))
        self.transform = None

    def forward(self, x):
        img = Image.open(BytesIO(base64.b64decode(x)))
        img = self.transform(img).unsqueeze(0)
        x = self.model.features(img)
        x = self.model.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.model.classifier(x)
        return x
