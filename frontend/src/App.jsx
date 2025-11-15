import React, { useState } from "react";
import axios from "axios";

const API_BASE = "https://hiring-sprint-2025.onrender.com/";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [phase, setPhase] = useState(null);
  const [pickupImages, setPickupImages] = useState([]);
  const [returnImages, setReturnImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inspectionReport, setInspectionReport] = useState(null);
  const [currentDetection, setCurrentDetection] = useState(null);

  const startInspection = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/inspection/start`);
      setSessionId(res.data.session_id);
      setPhase("pickup");
      setPickupImages([]);
      setReturnImages([]);
      setInspectionReport(null);
    } catch (error) {
      alert("Error starting inspection: " + error.message);
    }
    setLoading(false);
  };

  const handleImageUpload = async (e, isReturn) => {
    const files = e.target.files;
    if (!files || !sessionId) return;

    setLoading(true);
    try {
      for (let file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await axios.post(
          `${API_BASE}/api/inspection/${sessionId}/detect`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        const imageData = {
          file_name: file.name,
          detection: res.data.current_detection,
        };

        if (isReturn) {
          setReturnImages([...returnImages, imageData]);
        } else {
          setPickupImages([...pickupImages, imageData]);
        }

        setCurrentDetection(res.data.current_detection);
      }
    } catch (error) {
      alert("Error uploading image: " + error.message);
    }
    setLoading(false);
  };

  const switchToReturn = async () => {
    setLoading(true);
    try {
      await axios.post(
        `${API_BASE}/api/inspection/${sessionId}/switch-to-return`
      );
      setPhase("return");
      setReturnImages([]);
    } catch (error) {
      alert("Error switching phase: " + error.message);
    }
    setLoading(false);
  };

  const completeInspection = async () => {
    setLoading(true);
    try {
      const res = await axios.post(
        `${API_BASE}/api/inspection/${sessionId}/complete`
      );
      setInspectionReport(res.data);
      setSessionId(null);
      setPhase(null);
    } catch (error) {
      alert("Error completing inspection: " + error.message);
    }
    setLoading(false);
  };

  // Home/Initial state
  if (!sessionId && !inspectionReport) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🚗 Vehicle Inspection
          </h1>
          <p className="text-gray-600 mb-6">
            Capture vehicle condition at pickup and return to identify new
            damages
          </p>
          <button
            onClick={startInspection}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
          >
            {loading ? "Starting..." : "Start Inspection"}
          </button>
        </div>
      </div>
    );
  }

  // Inspection phases
  if (sessionId && phase) {
    const isPickup = phase === "pickup";
    const images = isPickup ? pickupImages : returnImages;

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  {isPickup ? "📸 Pickup Phase" : "📸 Return Phase"}
                </h1>
                <p className="text-gray-600 text-sm mt-1">
                  Session: {sessionId.substring(0, 8)}...
                </p>
              </div>
              <div className="text-right">
                <p className="text-lg font-semibold text-blue-600">
                  {images.length} image{images.length !== 1 ? "s" : ""} uploaded
                </p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Upload Vehicle Images
            </h2>
            <label className="flex items-center justify-center w-full px-4 py-6 bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg cursor-pointer hover:bg-blue-100 transition">
              <div className="text-center">
                <svg
                  className="w-8 h-8 mx-auto text-blue-600 mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                <p className="text-gray-700 font-medium">
                  Click to upload images
                </p>
                <p className="text-gray-500 text-sm">or drag and drop</p>
              </div>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => handleImageUpload(e, !isPickup)}
                disabled={loading}
                className="hidden"
              />
            </label>
          </div>

          {/* Uploaded Images Gallery */}
          {images.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Uploaded Images
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {images.map((img, idx) => (
                  <div
                    key={idx}
                    className="border rounded-lg overflow-hidden bg-gray-100"
                  >
                    <div className="aspect-video bg-gray-200 flex items-center justify-center overflow-hidden">
                      {img.detection.annotated_image && (
                        <img
                          src={img.detection.annotated_image}
                          alt={`Upload ${idx}`}
                          className="w-full h-full object-contain"
                        />
                      )}
                    </div>
                    <div className="p-3 bg-white">
                      <p className="font-medium text-sm text-gray-800 truncate">
                        {img.file_name}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {img.detection.classes.map((cls, i) => (
                          <span
                            key={i}
                            className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded"
                          >
                            {cls}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Detection Preview */}
          {currentDetection && currentDetection.classes.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-orange-500">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Detected Damages
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {currentDetection.classes.map((cls, idx) => (
                  <div
                    key={idx}
                    className="bg-orange-50 border border-orange-200 rounded p-4 text-center"
                  >
                    <p className="text-orange-700 font-semibold text-sm">
                      {cls}
                    </p>
                    <p className="text-orange-600 text-xs mt-1">
                      Confidence: {currentDetection.confidences[idx].toFixed(1)}
                      %
                    </p>
                    <p className="text-gray-800 font-bold mt-2">
                      ${currentDetection.repair_costs[idx].min}-$
                      {currentDetection.repair_costs[idx].max}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            {isPickup && images.length > 0 && (
              <button
                onClick={switchToReturn}
                disabled={loading}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
              >
                {loading ? "Processing..." : "Move to Return Phase"}
              </button>
            )}
            {!isPickup && images.length > 0 && (
              <button
                onClick={completeInspection}
                disabled={loading}
                className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
              >
                {loading ? "Processing..." : "Complete Inspection"}
              </button>
            )}
            <button
              onClick={() => window.location.reload()}
              className="px-6 bg-gray-400 hover:bg-gray-500 text-white font-bold py-3 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Report view
  if (inspectionReport) {
    const newDamages = inspectionReport.new_damages_detected;
    const summary = inspectionReport.inspection_summary;

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-green-500">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              ✅ Inspection Complete
            </h1>
            <p className="text-gray-600">Review the comparison results below</p>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Pickup Images</p>
              <p className="text-3xl font-bold text-blue-600">
                {summary.pickup_phase.images_uploaded}
              </p>
              <p className="text-gray-500 text-xs mt-1">
                {summary.pickup_phase.total_damages} total damages
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Return Images</p>
              <p className="text-3xl font-bold text-blue-600">
                {summary.return_phase.images_uploaded}
              </p>
              <p className="text-gray-500 text-xs mt-1">
                {summary.return_phase.total_damages} total damages
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
              <p className="text-gray-600 text-sm font-medium">NEW Damages</p>
              <p className="text-3xl font-bold text-red-600">
                {newDamages.total_new_damages}
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Found during inspection
              </p>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Estimated Repair Costs
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded p-4">
                <p className="text-gray-600 text-sm">Minimum Cost</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${newDamages.estimated_repair_cost.min}
                </p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded p-4">
                <p className="text-gray-600 text-sm">Average Cost</p>
                <p className="text-2xl font-bold text-purple-600">
                  ${newDamages.estimated_repair_cost.average}
                </p>
              </div>
              <div className="bg-red-50 border border-red-200 rounded p-4">
                <p className="text-gray-600 text-sm">Maximum Cost</p>
                <p className="text-2xl font-bold text-red-600">
                  ${newDamages.estimated_repair_cost.max}
                </p>
              </div>
            </div>
          </div>

          {/* Damage Breakdown */}
          {newDamages.damages_breakdown.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                New Damages Breakdown
              </h2>
              <div className="space-y-3">
                {newDamages.damages_breakdown.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center p-4 bg-orange-50 border border-orange-200 rounded"
                  >
                    <div>
                      <p className="font-semibold text-gray-800">
                        {item.damage_type}
                      </p>
                      <p className="text-sm text-gray-600">
                        Quantity: {item.count}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        ${item.cost_per_unit.min} - ${item.cost_per_unit.max}{" "}
                        each
                      </p>
                      <p className="font-bold text-lg text-orange-600">
                        ${item.cost_per_unit.min * item.count} - $
                        {item.cost_per_unit.max * item.count}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Return Images with Detections */}
          {inspectionReport.return_detections_with_boxes.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Return Phase Images with Detected Damages
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {inspectionReport.return_detections_with_boxes.map(
                  (det, idx) => (
                    <div
                      key={idx}
                      className="border rounded-lg overflow-hidden bg-gray-100"
                    >
                      <div className="aspect-video bg-gray-200 flex items-center justify-center">
                        {det.annotated_image && (
                          <img
                            src={det.annotated_image}
                            alt={`Return ${idx}`}
                            className="w-full h-full object-contain"
                          />
                        )}
                      </div>
                      <div className="p-3 bg-white">
                        <p className="font-medium text-sm text-gray-800 mb-2">
                          Damages found:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {det.classes.map((cls, i) => (
                            <span
                              key={i}
                              className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded"
                            >
                              {cls} ({det.confidences[i].toFixed(0)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {/* No New Damages */}
          {newDamages.total_new_damages === 0 && (
            <div className="bg-green-50 border-2 border-green-500 rounded-lg p-8 text-center">
              <p className="text-3xl mb-2">🎉</p>
              <h3 className="text-xl font-bold text-green-700 mb-2">
                No New Damages Detected!
              </h3>
              <p className="text-green-600">
                The vehicle is in the same condition as pickup. No charges
                applicable.
              </p>
            </div>
          )}

          {/* Action Button */}
          <div className="flex justify-center mt-8">
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition"
            >
              Start New Inspection
            </button>
          </div>
        </div>
      </div>
    );
  }
}
