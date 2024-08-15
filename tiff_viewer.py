import tkinter as tk
from tkinter import ttk, filedialog
from tktooltip import ToolTip
from PIL import Image, ImageTk

from tiff_processor import TiffProcessor

class TiffViewer(tk.Tk):
	def __init__(self):
		super().__init__()

		self.processor = TiffProcessor()

		self.title("TIFF Preprocessor")
		self.geometry("800x1000")
		self.blocks = dict()
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

		# Pointers for image container and instance
		self.image_label = None
		self.image_tk = None
		self.selected_frame_idx = 0

		# Slider for selecting frame
		self.slider = tk.Scale(self, from_=0, to=0, orient=tk.HORIZONTAL, resolution=1, command=self.update_image)
		self.slider.pack(fill=tk.X, padx=10, pady=10)

		# File open button
		self.open_button = tk.Button(self, text="Open file", command=self.open_file)
		self.open_button.pack(pady=10)

		def update0(x):
			self.intensity_threshold=float(x)
			self.update_image(self.selected_frame_idx)
		self.slider_block(name="mask_intensity_threshold", parent=self, command=update0, max_=255)

		def update1(x):
			self.mask_kernel_size=int(float(x))
			self.update_image(self.selected_frame_idx)
		self.slider_block(name="mask_opening_kernel_size", parent=self, command=update1, max_=21)

		def update2(x):
			self.img_kernel_size=int(float(x))
			self.update_image(self.selected_frame_idx)
		self.slider_block(name="img_closing_kernel_size", parent=self, command=update2, max_=21)


	# HACK
	def slider_block(self, name, parent, command, max_, min_=0, resolution=1):
		block = tk.Scale(parent, from_=min_, to=max_, orient=tk.VERTICAL, resolution=resolution, command=command)
		block.pack(side=tk.LEFT, padx=10)
		ToolTip(block, msg=name, delay=0.5)
		self.blocks[name] = block

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
		self.selected_frame_idx = frame_idx
		frame = self.processor.get_img(frame_idx, self.intensity_threshold, self.mask_kernel_size, self.img_kernel_size)
		image = Image.fromarray(frame)
		self.image_tk = ImageTk.PhotoImage(image)

		if self.image_label:
			self.canvas.delete(self.image_label)

		self.image_label = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
		self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

	def apply_processor(self):
		if self.image_label:
			frame = self.processor.get_img(self.selected_frame_idx, self.intensity_threshold, self.mask_kernel_size, self.img_kernel_size)
			image = Image.fromarray(frame)
			self.image_tk = ImageTk.PhotoImage(image)
			self.image_label.config(image=self.image_tk)
			self.image_label.image = self.image_tk

if __name__ == "__main__":
	app = TiffViewer()
	app.mainloop()