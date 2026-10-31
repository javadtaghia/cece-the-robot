"""Display the robot-mounted Gazebo camera; does not connect to a real camera."""
import queue
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image as PILImage, ImageTk
from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image

frames = queue.Queue(maxsize=1)

def on_image(msg):
    if not msg.width or not msg.height or not msg.data:
        return
    frame = (msg.width, msg.height, msg.step, bytes(msg.data))
    try:
        frames.get_nowait()
    except queue.Empty:
        pass
    try:
        frames.put_nowait(frame)
    except queue.Full:
        pass

def main():
    root = tk.Tk()
    root.title("Cece - Gazebo robot camera")
    root.geometry("680x570")
    ttk.Label(root, text="Cece's simulated camera", font=("Segoe UI", 16, "bold")).pack(pady=8)
    display = ttk.Label(root, anchor="center")
    display.pack(expand=True, fill="both", padx=10)
    status = tk.StringVar(value="Waiting for Gazebo camera images...")
    ttk.Label(root, textvariable=status).pack(pady=8)
    node = Node()
    node.subscribe(Image, "/cece/camera/image", on_image)
    last_frame = 0.0
    def update():
        nonlocal last_frame
        try:
            width, height, step, data = frames.get_nowait()
            image = PILImage.frombytes("RGB", (width, height), data, "raw", "RGB", step)
            image = image.resize((640, 480), PILImage.Resampling.NEAREST)
            display.image = ImageTk.PhotoImage(image)
            display.configure(image=display.image)
            last_frame = time.monotonic()
            status.set("Live from the Gazebo camera (simulated)")
        except queue.Empty:
            if last_frame and time.monotonic() - last_frame > 3:
                status.set("Camera feed stopped — check that Gazebo is running.")
        except Exception as exc:
            status.set("Cannot display camera image: " + str(exc))
        root.after(100, update)
    root.after(100, update)
    root.mainloop()

if __name__ == "__main__":
    main()
