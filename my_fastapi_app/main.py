import io
import os
import uvicorn
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
from typing import List, Dict, Optional
from numpy import ndarray
from typing import Tuple
from PIL import Image
import base64
from fastapi import Response
import json
from datetime import datetime
import uuid
  
  




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
   score: float=0.005,
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
     # For each class above threshold, add a detection
     for class_id, class_score in enumerate(classes_score):
        if class_score > score:
         label = self.classes[int(class_id)]
         confs.append(conf)
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
   
   # Thinner box (thickness=1) to reduce clutter
   cv2.rectangle(annotated_image, (left, top), (left + width, top + height), color, 1)
   
   # Smaller label text to save space
   label = f"{classes[idx]}"
   font_scale = 0.35
   font_thickness = 1
   (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
   
   # Draw label background with minimal padding
   cv2.rectangle(annotated_image, (left, top - text_height - 4), (left + text_width + 2, top), color, -1)
   cv2.putText(annotated_image, label, (left + 1, top - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
  
  return annotated_image

 def __call__(self,
   image: ndarray, 
   width: int=640, 
   height: int=640, 
   score: float=0.005,
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
   # Use higher quality JPEG (95% quality) for better image fidelity
   _, buffer = cv2.imencode('.jpg', annotated_rgb, [cv2.IMWRITE_JPEG_QUALITY, 95])
   img_base64 = base64.b64encode(buffer).decode('utf-8')
   results['annotated_image'] = f"data:image/jpeg;base64,{img_base64}"
  
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

# In-memory store for inspection sessions
inspection_sessions: Dict[str, Dict] = {}

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
        "version": "2.0",
        "endpoints": {
            "/api/inspection/start": "POST - Start a new inspection session (pickup phase)",
            "/api/inspection/{session_id}/detect": "POST - Detect damages in uploaded image",
            "/api/inspection/{session_id}/complete": "POST - Complete inspection and compare pickup vs return",
            "/api/detection": "POST - Legacy single image detection (deprecated)",
        }
    }

@app.post('/api/inspection/start')
def start_inspection():
    """Start a new inspection session (pickup phase)"""
    session_id = str(uuid.uuid4())
    inspection_sessions[session_id] = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'pickup_detections': [],
        'return_detections': [],
        'phase': 'pickup'
    }
    return {'session_id': session_id, 'message': 'Inspection started - in pickup phase'}

@app.post('/api/inspection/{session_id}/detect')
def detect_damage_in_session(session_id: str, file: bytes = File(...)):
    """
    Detect damages in uploaded image and store in session.
    When called during 'pickup' phase, stores as pickup damage.
    When called during 'return' phase, stores as return damage.
    """
    if session_id not in inspection_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = inspection_sessions[session_id]
    
    # Detect damages in the image
    image = Image.open(io.BytesIO(file)).convert("RGB")
    image = np.array(image)
    image = image[:,:,::-1].copy()
    results = detection(image, return_annotated=True)
    
    # Add repair costs
    repair_costs = []
    for damage_type in results.get('classes', []):
        cost = REPAIR_COSTS.get(damage_type.lower(), {'min': 100, 'max': 500})
        repair_costs.append(cost)
    
    results['repair_costs'] = repair_costs
    
    # Store in appropriate phase
    if session['phase'] == 'pickup':
        session['pickup_detections'].append(results)
    else:
        session['return_detections'].append(results)
    
    return {
        'session_id': session_id,
        'phase': session['phase'],
        'detections_count': len(session['pickup_detections']) if session['phase'] == 'pickup' else len(session['return_detections']),
        'current_detection': results
    }

@app.post('/api/inspection/{session_id}/switch-to-return')
def switch_to_return_phase(session_id: str):
    """Switch inspection from pickup phase to return phase"""
    if session_id not in inspection_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = inspection_sessions[session_id]
    session['phase'] = 'return'
    
    return {
        'session_id': session_id,
        'message': 'Switched to return phase',
        'pickup_images_count': len(session['pickup_detections'])
    }

@app.post('/api/inspection/{session_id}/complete')
def complete_inspection(session_id: str):
    """
    Complete the inspection and compare pickup vs return damages.
    Returns only NEW damages (damages in return that weren't in pickup).
    """
    if session_id not in inspection_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = inspection_sessions[session_id]
    
    # Extract all damage types from pickup
    pickup_damages = []
    for detection_result in session['pickup_detections']:
        pickup_damages.extend(detection_result.get('classes', []))
    
    # Extract all damage types from return
    return_damages = []
    return_detections_with_boxes = []
    for detection_result in session['return_detections']:
        return_damages.extend(detection_result.get('classes', []))
        return_detections_with_boxes.append(detection_result)
    
    # Find NEW damages: damages in return that weren't in pickup
    # Count occurrences to handle multiple same damages
    pickup_damage_counts = {}
    for dmg in pickup_damages:
        pickup_damage_counts[dmg] = pickup_damage_counts.get(dmg, 0) + 1
    
    return_damage_counts = {}
    for dmg in return_damages:
        return_damage_counts[dmg] = return_damage_counts.get(dmg, 0) + 1
    
    # Calculate new damages
    new_damages = []
    new_damage_counts = {}
    for damage_type, count in return_damage_counts.items():
        pickup_count = pickup_damage_counts.get(damage_type, 0)
        if count > pickup_count:
            new_count = count - pickup_count
            new_damages.extend([damage_type] * new_count)
            new_damage_counts[damage_type] = new_count
    
    # Calculate costs for new damages
    total_min_cost = 0
    total_max_cost = 0
    new_damages_breakdown = []
    
    for damage_type, count in new_damage_counts.items():
        cost = REPAIR_COSTS.get(damage_type.lower(), {'min': 100, 'max': 500})
        total_min_cost += cost['min'] * count
        total_max_cost += cost['max'] * count
        new_damages_breakdown.append({
            'damage_type': damage_type,
            'count': count,
            'cost_per_unit': cost
        })
    
    # Prepare response
    response = {
        'session_id': session_id,
        'inspection_summary': {
            'pickup_phase': {
                'images_uploaded': len(session['pickup_detections']),
                'total_damages': len(pickup_damages),
                'damages_by_type': pickup_damage_counts
            },
            'return_phase': {
                'images_uploaded': len(session['return_detections']),
                'total_damages': len(return_damages),
                'damages_by_type': return_damage_counts
            }
        },
        'new_damages_detected': {
            'total_new_damages': len(new_damages),
            'damages_breakdown': new_damages_breakdown,
            'estimated_repair_cost': {
                'min': total_min_cost,
                'max': total_max_cost,
                'average': (total_min_cost + total_max_cost) // 2
            }
        },
        'return_detections_with_boxes': return_detections_with_boxes
    }
    
    # Cleanup session
    del inspection_sessions[session_id]
    
    return response




if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)




