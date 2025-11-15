#!/usr/bin/env python3
"""
Model Evaluation Script - Tests accuracy on all test images
Runs detection on all test images and generates a report with statistics
"""

import os
import sys
import cv2
import json
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# Add my_fastapi_app to path so we can import Detection class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'my_fastapi_app'))

from main import detection, REPAIR_COSTS

def evaluate_model():
    """Evaluate model on all test images"""
    
    test_images_dir = Path(__file__).parent / "test_images" / "test"
    
    if not test_images_dir.exists():
        print("❌ test_images/test folder not found!")
        return False
    
    # Get all test images
    test_images = sorted(list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.jpeg")))
    
    if not test_images:
        print("❌ No test images found!")
        return False
    
    print(f"🧪 Evaluating model on {len(test_images)} test images...\n")
    
    # Statistics
    stats = {
        'total_images': len(test_images),
        'images_with_detections': 0,
        'images_without_detections': 0,
        'total_detections': 0,
        'damages_by_type': defaultdict(int),
        'total_repair_cost_estimated': 0,
        'detections_per_image': []
    }
    
    failed_images = []
    
    # Process each image
    for img_path in tqdm(test_images, desc="Processing"):
        try:
            # Read image
            image = cv2.imread(str(img_path))
            if image is None:
                failed_images.append(img_path.name)
                continue
            
            # Run detection
            results = detection(image, return_annotated=False)  # Don't encode image, just get data
            
            num_detections = len(results.get('classes', []))
            
            if num_detections > 0:
                stats['images_with_detections'] += 1
                stats['total_detections'] += num_detections
                
                # Track damages
                for damage_type in results.get('classes', []):
                    stats['damages_by_type'][damage_type] += 1
                
                # Track repair costs
                for repair_cost in results.get('repair_costs', []):
                    stats['total_repair_cost_estimated'] += (repair_cost['min'] + repair_cost['max']) / 2
                
                stats['detections_per_image'].append({
                    'image': img_path.name,
                    'detections': num_detections,
                    'classes': results.get('classes', []),
                    'confidences': [f"{c:.1f}%" for c in results.get('confidences', [])]
                })
            else:
                stats['images_without_detections'] += 1
        
        except Exception as e:
            failed_images.append(f"{img_path.name} (error: {str(e)[:30]})")
    
    # Print results
    print("\n" + "="*60)
    print("🎯 MODEL EVALUATION RESULTS")
    print("="*60)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total images tested: {stats['total_images']}")
    print(f"   Images with detections: {stats['images_with_detections']} ({stats['images_with_detections']*100//stats['total_images']}%)")
    print(f"   Images without detections: {stats['images_without_detections']} ({stats['images_without_detections']*100//stats['total_images']}%)")
    print(f"   Failed to process: {len(failed_images)}")
    
    print(f"\n🔍 Detection Statistics:")
    print(f"   Total detections: {stats['total_detections']}")
    avg_per_image = stats['total_detections'] / stats['total_images'] if stats['total_images'] > 0 else 0
    print(f"   Average detections per image: {avg_per_image:.2f}")
    
    print(f"\n💰 Damage Breakdown:")
    for damage_type, count in sorted(stats['damages_by_type'].items(), key=lambda x: x[1], reverse=True):
        percentage = count * 100 // stats['total_detections'] if stats['total_detections'] > 0 else 0
        print(f"   {damage_type}: {count} ({percentage}%)")
    
    print(f"\n💵 Cost Estimation:")
    print(f"   Average repair cost per detection: ${stats['total_repair_cost_estimated']/stats['total_detections']:.2f}" if stats['total_detections'] > 0 else "   No detections")
    print(f"   Total estimated cost (all detections): ${stats['total_repair_cost_estimated']:.2f}")
    
    # Show sample detections
    if stats['detections_per_image']:
        print(f"\n📸 Sample Detections (first 10):")
        for det in stats['detections_per_image'][:10]:
            print(f"   {det['image']}: {det['detections']} damages")
            for cls, conf in zip(det['classes'], det['confidences']):
                print(f"      - {cls} ({conf})")
    
    # Warnings
    if stats['images_without_detections'] > stats['total_images'] * 0.5:
        print(f"\n⚠️  WARNING: More than 50% of images have no detections!")
        print(f"   Consider lowering the detection threshold or retraining the model.")
    
    if failed_images:
        print(f"\n❌ Failed images ({len(failed_images)}):")
        for img in failed_images[:5]:
            print(f"   - {img}")
        if len(failed_images) > 5:
            print(f"   ... and {len(failed_images) - 5} more")
    
    # Save detailed report
    report_path = Path(__file__).parent / "model_evaluation_report.json"
    with open(report_path, 'w') as f:
        # Convert defaultdict to dict for JSON serialization
        stats['damages_by_type'] = dict(stats['damages_by_type'])
        json.dump(stats, f, indent=2)
    
    print(f"\n✅ Detailed report saved to: {report_path}")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = evaluate_model()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Evaluation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
