import cv2
import torch
from ultralytics import YOLO
import time

# Initialize YOLOv8 model
model = YOLO("yolov8n.pt")  # or use the specific model you've downloaded

# Initialize webcam
cap = cv2.VideoCapture(0)

# Get the video properties for saving
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

# Initialize variables for FPS calculation
prev_time = 0
fps_list = []

while cap.isOpened():
    # Read a frame from the webcam
    success, frame = cap.read()

    if success:
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
cap.release()
out.release()
cv2.destroyAllWindows()

# Print average FPS
print(f"Average FPS: {sum(fps_list) / len(fps_list):.2f}")