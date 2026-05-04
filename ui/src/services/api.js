import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "https://acm-i365.onrender.com/api";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s — model inference can be slow
});

/**
 * Run the full prediction pipeline (segmentation + disease + variety).
 * @param {File} imageFile - The image file to analyze.
 * @returns {Promise<Object>} Prediction results.
 */
export async function predictFull(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}
/**
 * Run the explicit paddy prediction pipeline.
 * @param {File} imageFile - The image file to analyze.
 * @returns {Promise<Object>} Prediction results.
 */
export async function predictPaddy(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict/paddy", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Run the explicit grain prediction pipeline.
 * @param {File} imageFile - The image file to analyze.
 * @returns {Promise<Object>} Prediction results.
 */
export async function predictGrain(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict/grain", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Run segmentation only.
 */
export async function predictSegment(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict/segment", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Run disease detection only.
 */
export async function predictDisease(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict/disease", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Run variety classification only.
 */
export async function predictVariety(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  const response = await api.post("/predict/variety", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Health check.
 */
export async function healthCheck() {
  const response = await api.get("/health");
  return response.data;
}

/**
 * Get 7-day weather forecast and spraying insights based on location.
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Weather data
 */
export async function getWeatherForecast(lat, lon) {
  const response = await api.get(`/weather/forecast`, {
    params: { lat, lon }
  });
  return response.data;
}

/**
 * Send a message to the AI chatbot.
 * @param {Array} messages - List of message objects {role, text}
 * @param {Object} pipelineResults - Optional previous inference data
 */
export async function sendChatMessage(messages, pipelineResults = null) {
  const response = await api.post("/chat", {
    messages,
    pipeline_results: pipelineResults
  });
  return response.data;
}

export default api;
