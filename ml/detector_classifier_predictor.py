"""
Detector + Classifier Predictor
- Loads YOLOv5 detection weights (via torch.hub) and EfficientNet classifier checkpoint
- Exposes predict(file-like) -> dict with items (list of predicted labels) and confidence
"""
from pathlib import Path
import torch
from PIL import Image
import timm
import torchvision.transforms as T
import numpy as np

class DetectorClassifierPredictor:
    def __init__(self, yolo_weights: str, clf_ckpt: str, img_size: int = 384):
        self.yolo_weights = yolo_weights
        self.clf_ckpt = clf_ckpt
        self.img_size = img_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load YOLO model
        print('Loading YOLO model...')
        self.yolo = torch.hub.load('ultralytics/yolov5', 'custom', path=yolo_weights, force_reload=False)

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

        results = self.yolo([np.array(img)])
        xyxy = results.xyxy[0].cpu().numpy()

        predictions = []
        for box in xyxy:
            x1,y1,x2,y2,conf,cls = box
            x1,y1,x2,y2 = map(int, [x1,y1,x2,y2])
            crop = img.crop((x1,y1,x2,y2))
            t = self.transform(crop).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.clf(t)
                probs = torch.softmax(logits, dim=1)
                p, idx = probs.max(1)
                label = self.classes[idx.item()] if self.classes else str(idx.item())
            predictions.append({'label': label, 'det_conf': float(conf), 'clf_conf': float(p.item())})

        if len(predictions) == 0:
            # fallback classify on full image
            t = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.clf(t)
                probs = torch.softmax(logits, dim=1)
                p, idx = probs.max(1)
                label = self.classes[idx.item()] if self.classes else str(idx.item())
            predictions.append({'label': label, 'det_conf': 0.0, 'clf_conf': float(p.item())})

        # produce same shape as old predictor
        items = [p['label'] for p in predictions]
        confidence = max([p['clf_conf'] for p in predictions]) if predictions else 0.0
        return {'items': items, 'confidence': float(confidence), 'detailed': predictions}
