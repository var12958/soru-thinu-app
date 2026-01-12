"""
Fixed Simple Classifier Predictor (EfficientNet only)
- Loads EfficientNet classifier checkpoint
- Classifies entire image without detection
- Implements confidence threshold for unknown food detection
"""
from pathlib import Path
import torch
from PIL import Image
import timm
import torchvision.transforms as T

class FixedSimpleClassifierPredictor:
    def __init__(self, clf_ckpt: str, img_size: int = 384, confidence_threshold: float = 0.6):
        self.clf_ckpt = clf_ckpt
        self.img_size = img_size
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load classifier
        print('Loading classifier checkpoint...')
        ckpt = torch.load(clf_ckpt, map_location='cpu')
        self.classes = ckpt.get('classes', None)
        
        if not self.classes:
            # Default Indian food classes if not found in checkpoint
            self.classes = [
                "chapati", "paneer butter masala", "dal", "rice", "biryani",
                "samosa", "dosa", "idli", "curry", "naan"
            ]
            print("Warning: No classes found in checkpoint. Using default classes.")
        
        self.clf = timm.create_model('efficientnet_b4', pretrained=False, num_classes=len(self.classes))
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
            max_prob, idx = probs.max(1)
            
            confidence = float(max_prob.item())
            
            # Apply confidence threshold
            if confidence < self.confidence_threshold:
                return {
                    'items': ['Unknown food'], 
                    'confidence': confidence,
                    'class': 'Unknown food',
                    'is_unknown': True
                }
            
            label = self.classes[idx.item()]
            
            return {
                'items': [label], 
                'confidence': confidence,
                'class': label,
                'is_unknown': False
            }