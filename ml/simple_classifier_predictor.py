"""
Simple Classifier Predictor (EfficientNet only)
- Loads EfficientNet classifier checkpoint
- Classifies entire image without detection
"""
from pathlib import Path
import torch
from PIL import Image
import timm
import torchvision.transforms as T

class SimpleClassifierPredictor:
    def __init__(self, clf_ckpt: str, img_size: int = 384):
        self.clf_ckpt = clf_ckpt
        self.img_size = img_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load classifier
        print('Loading classifier checkpoint...')
        ckpt = torch.load(clf_ckpt, map_location='cpu')
        self.classes = ckpt.get('classes', None)
        self.clf = timm.create_model('efficientnet_b4', pretrained=False, num_classes=len(self.classes) if self.classes else None)
        self.clf.load_state_dict(ckpt['model_state_dict'])
        self.clf = self.clf.to(self.device).eval()

        self.transform = T.Compose([
            T.Resize(int(self.img_size*1.1)),
            T.CenterCrop(self.img_size),
            T.ToTensor(),
            T.Normalize(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225))
        ])

    def predict(self, image_file):
        # image_file: path or file-like
        if isinstance(image_file, (str, Path)):
            img = Image.open(image_file).convert('RGB')
        else:
            img = Image.open(image_file).convert('RGB')

        # Classify entire image
        t = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.clf(t)
            probs = torch.softmax(logits, dim=1)
            p, idx = probs.max(1)
            label = self.classes[idx.item()] if self.classes else str(idx.item())

        return {
            'items': [label], 
            'confidence': float(p.item()),
            'class': label
        }