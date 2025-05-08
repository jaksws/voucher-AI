import torch

class VoucherDetector:
    def __init__(self, model_path='models/yolo_voucher.pt'):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
        self.model.eval()

    def detect_roi(self, img):
        """الكشف عن منطقة السند باستخدام YOLOv5"""
        results = self.model(img)
        boxes = results.xyxy[0].cpu().numpy()
        valid_boxes = [box for box in boxes if box[4] > 0.8]
        if valid_boxes:
            x1, y1, x2, y2, _, _ = valid_boxes[0]
            return img[int(y1):int(y2), int(x1):int(x2)]
        return img
