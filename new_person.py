import cv2
import os

def create_directory(directory_name):
    new_directory = os.path.join('data-new', directory_name)
    #global new_directory
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
        print(f"Directory {new_directory} created successfully!")
    else:
        print(f"{new_directory} already created")


def capture_images(directory_name, num_images):
    # Create the directory to store the images
    create_directory(directory_name)
    new_directory=f"data-new/{directory_name}"

    # Open the webcam
    cap = cv2.VideoCapture(0)

    image_count = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the frame in a window
        cv2.imshow('Webcam', frame)

        key=cv2.waitKey(1)
        if key== ord('s'):
            image_count += 1
            image_filename = os.path.join(new_directory, f"image_{image_count}.jpg")
            cv2.imwrite(image_filename, frame)
            print(f"Image {image_count} captured and saved!")

        if image_count > num_images:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


