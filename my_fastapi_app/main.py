import io
import os
import uvicorn
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
from typing import List
from numpy import ndarray
from typing import Tuple
from PIL import Image
import base64
from fastapi import Response
  
  




class Detection:
 def __init__(self, 
      model_path: str, 
   classes: List[str]
  ):
  self.model_path = model_path
  self.classes = classes
  self.model = self.__load_model()
  self.colors = [
   (255, 87, 51), (51, 255, 87), (87, 51, 255), (255, 195, 0),
   (0, 195, 255), (195, 0, 255), (255, 0, 195), (0, 255, 195)
  ]

 def __load_model(self) -> cv2.dnn_Net:
  net = cv2.dnn.readNet(self.model_path)
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
  return net

 def __extract_output(self, 
      preds: ndarray, 
   image_shape: Tuple[int, int], 
   input_shape: Tuple[int, int],
   score: float=0.1,
   nms: float=0.0, 
   confidence: float=0.0
  ) -> dict:
  class_ids, confs, boxes = list(), list(), list()

  image_height, image_width = image_shape
  input_height, input_width = input_shape
  x_factor = image_width / input_width
  y_factor = image_height / input_height
  
  rows = preds[0].shape[0]
  for i in range(rows):
   row = preds[0][i]
   conf = row[4]
   
   classes_score = row[4:]
   _,_,_, max_idx = cv2.minMaxLoc(classes_score)
   class_id = max_idx[1]
   if (classes_score[class_id] > score):
    confs.append(conf)
    label = self.classes[int(class_id)]
    class_ids.append(label)
    
    x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
    left = int((x - 0.5 * w) * x_factor)
    top = int((y - 0.5 * h) * y_factor)
    width = int(w * x_factor)
    height = int(h * y_factor)
    box = np.array([left, top, width, height])
    boxes.append(box)

  r_class_ids, r_confs, r_boxes = list(), list(), list()
  indexes = cv2.dnn.NMSBoxes(boxes, confs, confidence, nms)
  
  if len(indexes) > 0:
   for i in indexes:
    r_class_ids.append(class_ids[i])
    r_confs.append(confs[i]*100)
    r_boxes.append(boxes[i].tolist())

  return {
    'boxes': [ [int(x) for x in box] for box in r_boxes ],
    'confidences': [ float(conf) for conf in r_confs ],
    'classes': [ str(c) for c in r_class_ids ]
  }

 def __draw_boxes(self, image: ndarray, detections: dict) -> ndarray:
  annotated_image = image.copy()
  boxes = detections['boxes']
  confidences = detections['confidences']
  classes = detections['classes']
  
  for idx, box in enumerate(boxes):
   left, top, width, height = box
   color = self.colors[idx % len(self.colors)]
   
   cv2.rectangle(annotated_image, (left, top), (left + width, top + height), color, 2)
   
   label = f"{classes[idx]}: {confidences[idx]:.1f}%"
   (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
   
   cv2.rectangle(annotated_image, (left, top - text_height - 10), (left + text_width, top), color, -1)
   cv2.putText(annotated_image, label, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
  
  return annotated_image

 def __call__(self,
   image: ndarray, 
   width: int=640, 
   height: int=640, 
   score: float=0.1,
   nms: float=0.0, 
   confidence: float=0.0,
   return_annotated: bool=False
  ) -> dict:
  
  blob = cv2.dnn.blobFromImage(
     image, 1/255.0, (width, height), 
     swapRB=True, crop=False
    )
  self.model.setInput(blob)
  preds = self.model.forward()
  preds = preds.transpose((0, 2, 1))

  results = self.__extract_output(
   preds=preds,
   image_shape=image.shape[:2],
   input_shape=(height, width),
   score=score,
   nms=nms,
   confidence=confidence
  )
  
  if return_annotated:
   annotated_image = self.__draw_boxes(image, results)
   annotated_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
   _, buffer = cv2.imencode('.png', annotated_rgb)
   img_base64 = base64.b64encode(buffer).decode('utf-8')
   results['annotated_image'] = f"data:image/png;base64,{img_base64}"
  
  return results 

detection = Detection(
   model_path=os.path.join(os.path.dirname(__file__), 'best.onnx'), 
   classes=['damaged door', 'damaged window', 'damaged headlight', 'damaged mirror', 'dent', 'damaged hood', 'damaged bumper', 'damaged wind shield'] 
)


REPAIR_COSTS = {
    'damaged door': {'min': 300, 'max': 1500},
    'damaged window': {'min': 200, 'max': 400},
    'damaged headlight': {'min': 200, 'max': 780},
    'damaged mirror': {'min': 140, 'max': 330},
    'dent': {'min': 150, 'max': 600},
    'damaged hood': {'min': 300, 'max': 1500},
    'damaged bumper': {'min': 325, 'max': 1000},
    'damaged wind shield': {'min': 200, 'max': 500}
}

app = FastAPI(title="Car Damage Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def read_root():
    return {
        "message": "Car Damage Detection API",
        "version": "1.0",
        "endpoints": {
            "/api/detection": "POST - Upload image for damage detection",
        }
    }

@app.post('/api/detection')
def post_detection(file: bytes = File(...)):
   image = Image.open(io.BytesIO(file)).convert("RGB")
   image = np.array(image)
   image = image[:,:,::-1].copy()
   results = detection(image, return_annotated=True)
   
   repair_costs = []
   for damage_type in results.get('classes', []):
       cost = REPAIR_COSTS.get(damage_type.lower(), {'min': 100, 'max': 500})
       repair_costs.append(cost)
   
   results['repair_costs'] = repair_costs
   return results




if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)




