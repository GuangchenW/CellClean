import numpy as np
import cv2
import argparse

img = None

title_erosion_window = "Erosion"
max_elem = 2
max_kernel_size = 21
trackbar_erosion_element_shape = "Erosion shape"
trackbar_erosion_kernel_size = "Erosion size"
trackbar_dilation_element_shape = "Dilation shape"
trackbar_dilation_kernel_size = "Dilation size"
show_orig = 1

def main(path):
    global img
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    print(f'dtype: {img.dtype}, shape: {img.shape}, min: {np.min(img)}, max: {np.max(img)}')

    cv2.namedWindow(title_erosion_window)
    cv2.createTrackbar(trackbar_erosion_element_shape, title_erosion_window, 0, max_elem, process_img)
    cv2.createTrackbar(trackbar_erosion_kernel_size, title_erosion_window, 0, max_kernel_size, process_img)
    cv2.createTrackbar(trackbar_dilation_element_shape, title_erosion_window, 0, max_elem, process_img)
    cv2.createTrackbar(trackbar_dilation_kernel_size, title_erosion_window, 0, max_kernel_size, process_img)
    cv2.createTrackbar("Show original", title_erosion_window, 1, 2, show_original)

    process_img(0)
    cv2.waitKey()

def show_original(val):
    global show_orig
    show_orig = val
    process_img(0)

def process_img(val):
    result = img
    if show_orig == 0:
        cv2.imshow(title_erosion_window, result)
        return

    # TODO: Add trackbar for threshold
    _,mask = cv2.threshold(result,60,255,cv2.THRESH_TOZERO)
    inverted_mask = cv2.bitwise_not(mask)
    inverted_mask = dilation(inverted_mask)
    inverted_mask = erosion(inverted_mask)

    if show_orig == 1:
        cv2.imshow(title_erosion_window, inverted_mask)
    elif show_orig == 2:
        inverted_mask = cv2.normalize(inverted_mask,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_32F)
        result = img.astype(np.float32)
        for i in range(3):
            result = cv2.multiply(result,inverted_mask)
        result = cv2.normalize(result,None,alpha=0,beta=204,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_8U)
        result = erosion(result)
        result = dilation(result)
        cv2.imshow(title_erosion_window, result)

def erosion(src):
    erosion_size = cv2.getTrackbarPos(trackbar_erosion_kernel_size, title_erosion_window)
    erosion_shape = morph_shape(cv2.getTrackbarPos(trackbar_erosion_element_shape, title_erosion_window))

    element = cv2.getStructuringElement(erosion_shape, (2*erosion_size+1,2*erosion_size+1),
        (erosion_size,erosion_size))

    result = cv2.erode(src, element)
    return result

def dilation(src):
    dilation_size = cv2.getTrackbarPos(trackbar_dilation_kernel_size, title_erosion_window)
    dilation_shape = morph_shape(cv2.getTrackbarPos(trackbar_dilation_element_shape, title_erosion_window))

    element = cv2.getStructuringElement(dilation_shape, (2*dilation_size+1,2*dilation_size+1),
        (dilation_size,dilation_size))

    result = cv2.dilate(src, element)
    return result

def morph_shape(val):
    match val:
        case 0:
            return cv2.MORPH_RECT
        case 1:
            return cv2.MORPH_CROSS
        case 2:
            return cv2.MORPH_ELLIPSE
        case _:
            return cv2.MORPH_ELLIPSE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code for Eroding.")
    parser.add_argument("--path", help="Path to input image.", default = "images/Updated_4_Channel_4.ome.tiff")
    args = parser.parse_args()

    main(args.path)