# Singleton getter for AdvancedImageEncoder
_encoder_instance = None
def get_encoder_service():
    global _encoder_instance
    if _encoder_instance is None:
        _encoder_instance = AdvancedImageEncoder()
    return _encoder_instance

# Advanced CLIP-powered Encoder Service for AI-driven, multi-modal recognition and description
import io
import torch
from PIL import Image
import clip

class CLIPImageEncoder:
    def __init__(self, model_name="ViT-B/32", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.preprocess = clip.load(model_name, device=self.device)

    def encode_image(self, image_bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
        return image_features.cpu().numpy().flatten().tolist()

    def describe_image(self, image_bytes):
        # Zero-shot description using CLIP and prompt engineering
        # This is a placeholder for a more advanced Gemini-powered description
        # In production, this should call Gemini with a prompt including CLIP's top matches
        labels = [
            "a photo of a shoe",
            "a photo of a handbag",
            "a photo of a dress",
            "a photo of a shirt",
            "a photo of a jacket",
            "a photo of a watch",
            "a photo of a hat",
            "a photo of a pair of pants",
            "a photo of a pair of sunglasses",
            "a photo of a wallet",
            "a photo of a belt",
            "a photo of a scarf",
            "a photo of a ring",
            "a photo of a necklace",
            "a photo of a bracelet",
            "a photo of a pair of earrings",
            "a photo of a t-shirt",
            "a photo of a coat",
            "a photo of a skirt",
            "a photo of a sweater",
        ]
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        text_inputs = clip.tokenize(labels).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            text_features = self.model.encode_text(text_inputs)
            logits_per_image, _ = self.model(image_input, text_inputs)
            probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]
        best_idx = int(probs.argmax())
        best_label = labels[best_idx]
        confidence = float(probs[best_idx])
        return {
            "description": best_label,
            "confidence": confidence,
            "top_labels": [
                {"label": label, "confidence": float(prob)}
                for label, prob in sorted(zip(labels, probs), key=lambda x: -x[1])[:5]
            ],
        }

class AdvancedImageEncoder:
    def __init__(self):
        self.clip_encoder = CLIPImageEncoder()

    def encode(self, image_bytes):
        return self.clip_encoder.encode_image(image_bytes)

    def describe(self, image_bytes):
        # In production, this should call Gemini with a prompt that fuses CLIP, Google Vision, AWS Rekognition, etc.
        # For now, use CLIP zero-shot as a placeholder
        return self.clip_encoder.describe_image(image_bytes)
