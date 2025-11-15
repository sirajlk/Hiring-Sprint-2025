"""
Automated API Tests for Car Damage Detection System
Tests cover all major endpoints and use cases
Run with: pytest test_endpoints.py -v
"""

import pytest
import json
import io
import os
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np
from main import app, inspection_sessions


client = TestClient(app)


class TestInspectionWorkflow:
    """Test the complete inspection workflow: start -> detect -> switch -> complete"""

    def test_start_inspection(self):
        """Test starting a new inspection session"""
        response = client.post("/api/inspection/start")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["message"] == "Inspection started - in pickup phase"
        assert len(data["session_id"]) > 0

    def test_session_exists_after_start(self):
        """Verify session is stored after start"""
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]
        assert session_id in inspection_sessions
        assert inspection_sessions[session_id]["phase"] == "pickup"

    def test_switch_to_return_phase(self):
        """Test switching from pickup to return phase"""
        # Start inspection
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Switch to return
        response = client.post(f"/api/inspection/{session_id}/switch-to-return")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Switched to return phase"
        assert inspection_sessions[session_id]["phase"] == "return"

    def test_switch_nonexistent_session(self):
        """Test switching phase on non-existent session"""
        response = client.post("/api/inspection/invalid-session-id/switch-to-return")
        assert response.status_code == 404
        assert "Session not found" in response.text

    def test_detect_without_session(self):
        """Test detection on non-existent session returns 404"""
        # Create a dummy image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        response = client.post(
            "/api/inspection/invalid-session-id/detect",
            files={"file": ("test.png", img_bytes, "image/png")}
        )
        assert response.status_code == 404
        assert "Session not found" in response.text


class TestRootEndpoint:
    """Test the API root endpoint"""

    def test_api_root(self):
        """Test GET /api returns API info"""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "2.0"
        assert "endpoints" in data


class TestDetectionEndpoint:
    """Test detection functionality"""

    def create_dummy_image(self, width=640, height=640):
        """Create a dummy image for testing"""
        img = Image.new("RGB", (width, height), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def test_detect_with_valid_image(self):
        """Test detection with a valid image in a session"""
        # Start session
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Send image for detection
        img_bytes = self.create_dummy_image()
        response = client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test.png", img_bytes, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["phase"] == "pickup"
        assert "detections_count" in data
        assert "current_detection" in data

    def test_detect_returns_detection_results(self):
        """Test that detection returns proper structure"""
        # Start session
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Send image for detection
        img_bytes = self.create_dummy_image()
        response = client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test.png", img_bytes, "image/png")}
        )

        data = response.json()
        current_detection = data["current_detection"]
        
        # Verify detection result structure
        assert "boxes" in current_detection
        assert "confidences" in current_detection
        assert "classes" in current_detection
        assert "annotated_image" in current_detection
        assert "repair_costs" in current_detection
        
        # Verify structure consistency
        assert len(current_detection["boxes"]) == len(current_detection["classes"])
        assert len(current_detection["confidences"]) == len(current_detection["classes"])


class TestCompletionWorkflow:
    """Test the inspection completion and comparison logic"""

    def create_dummy_image(self):
        """Helper to create dummy image"""
        img = Image.new("RGB", (640, 640), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def test_complete_inspection(self):
        """Test completing an inspection with pickup and return phases"""
        # Start session
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Upload pickup images (at least one)
        img_bytes = self.create_dummy_image()
        client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test1.png", img_bytes, "image/png")}
        )

        # Switch to return phase
        client.post(f"/api/inspection/{session_id}/switch-to-return")

        # Upload return images
        img_bytes = self.create_dummy_image()
        client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test2.png", img_bytes, "image/png")}
        )

        # Complete inspection
        response = client.post(f"/api/inspection/{session_id}/complete")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "session_id" in data
        assert "inspection_summary" in data
        assert "new_damages_detected" in data
        assert "return_detections_with_boxes" in data

        # Verify session is deleted
        assert session_id not in inspection_sessions

    def test_complete_inspection_summary_structure(self):
        """Test that completion response has proper structure"""
        # Start and complete a simple inspection
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        img_bytes = self.create_dummy_image()
        client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test1.png", img_bytes, "image/png")}
        )
        client.post(f"/api/inspection/{session_id}/switch-to-return")

        img_bytes = self.create_dummy_image()
        client.post(
            f"/api/inspection/{session_id}/detect",
            files={"file": ("test2.png", img_bytes, "image/png")}
        )

        response = client.post(f"/api/inspection/{session_id}/complete")
        data = response.json()

        # Verify inspection summary
        summary = data["inspection_summary"]
        assert "pickup_phase" in summary
        assert "return_phase" in summary
        assert "images_uploaded" in summary["pickup_phase"]
        assert "total_damages" in summary["pickup_phase"]
        assert "damages_by_type" in summary["pickup_phase"]

        # Verify new damages detected structure
        new_damages = data["new_damages_detected"]
        assert "total_new_damages" in new_damages
        assert "damages_breakdown" in new_damages
        assert "estimated_repair_cost" in new_damages
        
        cost = new_damages["estimated_repair_cost"]
        assert "min" in cost
        assert "max" in cost
        assert "average" in cost


class TestSessionManagement:
    """Test session management and state handling"""

    def test_multiple_sessions_independent(self):
        """Test that multiple sessions don't interfere with each other"""
        # Start two sessions
        response1 = client.post("/api/inspection/start")
        session_id1 = response1.json()["session_id"]

        response2 = client.post("/api/inspection/start")
        session_id2 = response2.json()["session_id"]

        # Verify they're different
        assert session_id1 != session_id2
        assert session_id1 in inspection_sessions
        assert session_id2 in inspection_sessions


class TestErrorHandling:
    """Test error cases and edge cases"""

    def test_detect_with_missing_file(self):
        """Test detection when file is missing"""
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Try to detect without sending a file
        response = client.post(f"/api/inspection/{session_id}/detect")
        assert response.status_code == 422  # FastAPI validation error

    def test_complete_empty_session(self):
        """Test completing a session with no detections"""
        response = client.post("/api/inspection/start")
        session_id = response.json()["session_id"]

        # Try to complete without any detections
        response = client.post(f"/api/inspection/{session_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["new_damages_detected"]["total_new_damages"] == 0


# Health check and integration tests
class TestIntegration:
    """Integration tests"""

    def test_api_endpoint_exists(self):
        """Test that API root endpoint is accessible"""
        response = client.get("/api")
        assert response.status_code == 200


if __name__ == "__main__":
    # Run tests: pytest test_endpoints.py -v
    pytest.main([__file__, "-v"])
