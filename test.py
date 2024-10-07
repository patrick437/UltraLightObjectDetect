import cv2
import torch
from ultralytics import YOLO
import time
from picamera2 import Picamera2

# Initialize YOLOv8 model
model = YOLO("yolov8n.pt")  # Load YOLOv8 model

# Initialize Picamera2
camera = Picamera2()
camera_config = camera.create_still_configuration(main={"size": (640, 480)})  # You can configure the resolution
camera.configure(camera_config)
camera.start()

time.sleep(2)  # Give the camera time to warm up

# Get camera properties (from config or manually set them)
frame_width = 640
frame_height = 480
fps = 30  # This can be estimated based on PiCamera2 settings or manually adjusted

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

# Initialize variables for FPS calculation
prev_time = 0
fps_list = []

# Capture loop
while True:
    # Capture a frame from the PiCamera2
    frame = camera.capture_array()

    if frame is not None:
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Calculate and display the frame rate
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        fps_list.append(fps)
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Write the frame to the output video
        out.write(annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
out.release()
cv2.destroyAllWindows()

# Print average FPS
print(f"Average FPS: {sum(fps_list) / len(fps_list):.2f}")
