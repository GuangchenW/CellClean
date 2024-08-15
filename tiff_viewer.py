import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from tiff_processor import TiffProcessor

class TiffViewer(tk.Tk):
	def __init__(self):
		super().__init__()

		self.processor = TiffProcessor()

		self.title("TIFF Preprocessor")
		self.geometry("800x600")
		self.make_view()

	def make_view(self):
		# Canvas (main viewport)
		self.canvas = tk.Canvas(self, bg="gray")
		self.canvas.pack(fill=tk.BOTH, expand=True)
		self.canvas.x_start = 0
		self.canvas.y_start = 0
		
		# Functionality for dragging viewport 
		def on_mouse_down(event):
			self.canvas.scan_mark(event.x, event.y)
		def on_mouse_drag(event):
			self.canvas.scan_dragto(event.x, event.y, gain=1)
		self.canvas.bind("<ButtonPress-1>", on_mouse_down)
		self.canvas.bind("<B1-Motion>", on_mouse_drag)

		# Scroll bar for controlling viewport position
		self.h_scroll = tk.Scrollbar(self.canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
		self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
		self.v_scroll = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview)
		self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

		# Connect canvas to scrollbars
		self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

		self.image_label = None
		self.image_tk = None

		self.slider = ttk.Scale(self, from_=0, to=0, orient=tk.HORIZONTAL, command=self.update_image)
		self.slider.pack(fill=tk.X, padx=10, pady=10)

		self.open_button = tk.Button(self, text="Open file", command=self.open_file)
		self.open_button.pack(pady=10)

	def open_file(self):
		file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tiff *.tif")])

		if file_path:
			self.processor.load_img(file_path)
			self.slider.config(to=self.processor.num_frames-1)
			self.slider.set(0)

			self.update_image(0)

	def update_image(self, frame_idx):
		if not self.processor.num_frames > 0:
			return

		frame_idx = int(float(frame_idx))
		frame = self.processor.get_img(frame_idx=frame_idx)
		image = Image.fromarray(frame)
		self.image_tk = ImageTk.PhotoImage(image)

		if self.image_label:
			self.canvas.delete(self.image_label)

		self.image_label = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
		self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))


if __name__ == "__main__":
	app = TiffViewer()
	app.mainloop()
