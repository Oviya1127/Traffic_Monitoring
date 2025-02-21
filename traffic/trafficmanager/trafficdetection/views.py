from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from .models import DetectedObject, Violation, DriverBehavior
import cv2
import numpy as np
import os
import datetime
from django.conf import settings
from django.core.files.storage import default_storage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_CFG = os.path.abspath(os.path.join(BASE_DIR, "..", "yolo", "yolov4-tiny.cfg"))
MODEL_WEIGHTS = os.path.abspath(os.path.join(BASE_DIR, "..", "yolo", "yolov4-tiny.weights"))
CLASS_NAMES = os.path.abspath(os.path.join(BASE_DIR, "..", "yolo", "coco.names"))
  

def handle_uploaded_file(file): 
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file.name) 
    with open(file_path, 'wb+') as destination: 
        for chunk in file.chunks(): 
            destination.write(chunk) 
        return file_path

def detect_objects(image_path): 
    net = cv2.dnn.readNet(settings.YOLO_WEIGHTS, settings.YOLO_CFG) 
    with open(settings.YOLO_CLASSES, 'r') as f: 
        classes = f.read().strip().split("\n")
    frame = cv2.imread(image_path)
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    detections = net.forward([net.getLayerNames()[i - 1] for i in net.getUnconnectedOutLayers()])
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                label = classes[class_id]
                x, y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                detected_object = DetectedObject.objects.create(
                object_type=label,
                confidence=float(confidence),
                location=f"{x},{y},{w},{h}",
                image=os.path.relpath(image_path, settings.MEDIA_ROOT) )
                print(f"Detected: {label} - {confidence:.2f}")
def upload_view(request): 
    if request.method == 'POST' and request.FILES.get('file'): 
        uploaded_file = request.FILES['file'] 
        file_path = handle_uploaded_file(uploaded_file)
        if uploaded_file.content_type.startswith('image'):
            detect_objects(file_path)
        elif uploaded_file.content_type.startswith('video'):
            process_video(file_path)
        return JsonResponse({'message': 'File uploaded and processed successfully!'}, status=200)
    return render(request, 'upload.html')
def process_video(video_path):
    cap = cv2.VideoCapture(video_path) 
    frame_count = 0 
    while cap.isOpened():
        ret, frame = cap.read() 
        if not ret: 
            break 
        if frame_count % 30 == 0: 
             frame_path = os.path.join(settings.MEDIA_ROOT, 'temp', f"frame_{frame_count}.jpg")
             cv2.imwrite(frame_path, frame)
             detect_objects(frame_path)
        frame_count += 1
    cap.release()

# Load YOLO model
net = cv2.dnn.readNet(MODEL_WEIGHTS, MODEL_CFG)
with open(CLASS_NAMES, "r") as f:
    classes = f.read().strip().split("\n")

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Video processing class
class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None

        # Process frame: Detect, classify, and save objects
        processed_frame = process_frame(frame)

        _, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()

# Detect, classify, and save objects to database in a single function
def process_frame(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)

    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                label = classes[class_id]
                center_x, center_y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                x, y = int(center_x - w / 2), int(center_y - h / 2)

                # Save detected object
                filename = f"detections/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                path = os.path.join(settings.MEDIA_ROOT, filename)
                cv2.imwrite(path, frame)

                DetectedObject.objects.create(
                    object_type=label,
                    confidence=float(confidence),
                    location=f"{x},{y},{w},{h}",
                    image=filename
                )

                # Draw detection on frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

# Stream video
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Dashboard View
def dashboard(request):
    total_detections = DetectedObject.objects.count()
    total_violations = Violation.objects.count()
    total_driver_incidents = DriverBehavior.objects.count()

    recent_detections = DetectedObject.objects.order_by('-timestamp')[:5]
    recent_violations = Violation.objects.order_by('-timestamp')[:5]
    recent_behaviors = DriverBehavior.objects.order_by('-timestamp')[:5]

    context = {
        'total_detections': total_detections,
        'total_violations': total_violations,
        'total_driver_incidents': total_driver_incidents,
        'recent_detections': recent_detections,
        'recent_violations': recent_violations,
        'recent_behaviors': recent_behaviors,
    }

    return render(request, 'trafficdetection/dashboard.html', context)

def ui(request):
        return render(request, 'trafficdetection/uploadpage.html')
def ot(request):
        return render(request, 'trafficdetection/objecttracking.html')


# Traffic Violations
def violations(request):
    violations = Violation.objects.all().order_by('-timestamp')
    driver_behaviors = DriverBehavior.objects.all().order_by('-timestamp')
    
    return render(request, 'trafficdetection/violations.html', {
        'violations': violations,
        'driver_behaviors': driver_behaviors
    })

# Driver Behavior Incidents
def driver_behavior(request):
    behaviors = DriverBehavior.objects.all().order_by('-timestamp')
    return render(request, 'trafficdetection/driver_behavior.html', {'behaviors': behaviors})

# Alerts API (For Real-Time Updates)
def alerts(request):
    latest_violations = Violation.objects.order_by('-timestamp')[:5]
    latest_behaviors = DriverBehavior.objects.order_by('-timestamp')[:5]

    return JsonResponse({
        'violations': list(latest_violations.values('violation_type', 'timestamp')),
        'behaviors': list(latest_behaviors.values('behavior_type', 'timestamp'))
    }, safe=False)

def ot(request):
    detected_objects = DetectedObject.objects.all().order_by('-timestamp') 
    return render(request, 'trafficdetection/objecttracking.html', {'detected_objects': detected_objects})
