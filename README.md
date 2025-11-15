# 🚗 Vehicle Damage Detection - Hackathon Solution

## Quick Start (48-hour build)

## Very Important Note 
when trying to check for damages get a damaged car with either one of these i wasnt able to teach it about all damages but i tried teaching it the important ones

'damaged door', 'damaged window', 'damaged headlight', 'damaged mirror', 'dent', 'damaged hood', 'damaged bumper', 'damaged wind shield'

so these are the types of damages it can understand but ofcourse i couldnt make it perfect as sometimes it give wrong ones but ofcourse if i had more time i wouldve teached it more and made a better way 


### Prerequisites

- Python 3.8+
- Node.js 16+
- The trained model: `my_fastapi_app/best.onnx`

### Backend Setup

```powershell
cd my_fastapi_app
pip install -r ../requirements.txt
python main.py
```

The API will run at `http://localhost:8000`

**API Endpoints:**

- `POST /api/inspection/start` - Start new inspection session
- `POST /api/inspection/{session_id}/detect` - Upload image and detect damages
- `POST /api/inspection/{session_id}/switch-to-return` - Switch from pickup to return phase
- `POST /api/inspection/{session_id}/complete` - Complete inspection and get results

### Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

## How It Works

### 1. **Pickup Phase**

- User uploads multiple vehicle images from different angles
- AI detects all damages on each image
- System stores damage list for later comparison

### 2. **Return Phase**

- User uploads multiple vehicle images (same angles)
- AI detects all damages again

### 3. **Smart Comparison**

- **AI-powered**: Compares damage TYPES and COUNTS
- Example:
  - Pickup: `[dent, dent, broken_light]`
  - Return: `[dent, dent, dent, broken_light, broken_door]`
  - **New damages**: `[dent (1 extra), broken_door]`
  - **Charge**: For only the NEW damages

### 4. **Report Generation**

- Shows side-by-side comparison
- Lists only NEW damages found
- Calculates repair costs for new damages only
- Displays annotated images with bounding boxes

## Key Features

✅ **Multiple Damages Per Image** - Detects all damage types, not just one  
✅ **Smart Comparison** - Finds only NEW damages using AI  
✅ **No Pre-existing Damage Charges** - Existing damages aren't charged again  
✅ **Beautiful UI** - React + Tailwind CSS with real-time preview  
✅ **Full API Integration** - RESTful endpoints for car rental platforms  
✅ **Session-based** - Supports multiple concurrent inspections

## Testing

### Manual Test Flow

1. **Start backend**: `cd my_fastapi_app && python main.py`
2. **Start frontend**: `cd frontend && npm run dev`
3. Open browser: `http://localhost:5173`
4. Click "Start Inspection"
5. Upload 2-3 pickup images (vehicle from different angles)
6. Click "Move to Return Phase"
7. Upload 2-3 return images (same angles, with some new damages)
8. Click "Complete Inspection"
9. View the report with NEW damages only

## Comparison Algorithm

The smart comparison works by counting damage occurrences:

```python
# Pickup damages: [dent, dent, broken_light]
pickup_counts = {'dent': 2, 'broken_light': 1}

# Return damages: [dent, dent, dent, broken_light, broken_door]
return_counts = {'dent': 3, 'broken_light': 1, 'broken_door': 1}

# NEW damages = return - pickup
new_damages = {
  'dent': 1,              # 3 - 2 = 1 new dent
  'broken_door': 1        # 1 - 0 = 1 new broken_door
}
# 'broken_light' not counted (same count)
```

## Files Modified

- **Backend**: `my_fastapi_app/main.py` - Added session management & smart comparison
- **Frontend**: `frontend/src/App.jsx` - Complete React UI with Tailwind
- **Config**: `frontend/package.json`, `tailwind.config.js`, `postcss.config.js` - Tailwind setup

## Deployment Ready

The solution is modular and can be integrated into a larger car rental SaaS:

- RESTful API with session IDs for multi-user support
- CORS enabled for frontend integration
- Modular Detection class for easy reuse
- Session-based flow for concurrent inspections

---

**Built for hackathon speed. Ready for production use.** ⚡
