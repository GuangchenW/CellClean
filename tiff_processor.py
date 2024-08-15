import numpy as np
import cv2

class TiffProcessor:
    def __init__(self):
        self.img = []
        self.num_frames = 0
        pass

    def load_img(self, file_path):
        """
        Loads a tiff image. Assuming valid path and correct file type.
        :param file_path: Path to tiff image.
        """
        self.img = []
        _,self.img = cv2.imreadmulti(file_path, self.img, cv2.IMREAD_UNCHANGED)
        self.num_frames = len(self.img)
        #print(f'dtype: {self.img.dtype}, shape: {self.img.shape}, min: {np.min(self.img)}, max: {np.max(self.img)}')

    def get_img(self, frame_idx, threshold, ksize1, ksize2):
        return self.process_img(self.img[frame_idx], threshold, ksize1, ksize2)

    def process_img(self, img, threshold, ksize1, ksize2):
        _,mask = cv2.threshold(img,threshold,255,cv2.THRESH_TOZERO)
        inverted_mask = cv2.bitwise_not(mask)

        e_element = cv2.getStructuringElement(self.morph_shape(0), (2*ksize1+1,2*ksize1+1),(ksize1,ksize1))
        d_element = cv2.getStructuringElement(self.morph_shape(2), (2*ksize2+1,2*ksize2+1),(ksize2,ksize2))

        inverted_mask = cv2.dilate(inverted_mask, d_element)
        inverted_mask = cv2.erode(inverted_mask, e_element)

        inverted_mask = cv2.normalize(inverted_mask,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_32F)
        result = img.astype(np.float32)
        for i in range(3):
            result = cv2.multiply(result,inverted_mask)
        result = cv2.normalize(result,None,alpha=0,beta=204,norm_type=cv2.NORM_MINMAX,dtype=cv2.CV_8U)
        result = cv2.erode(result, e_element)
        result = cv2.dilate(result, d_element)
        return result

    def erosion(self, src, element):
        result = cv2.erode(src, element)
        return result

    def dilation(self, src, element):
        result = cv2.dilate(src, element)
        return result

    def morph_shape(self, val):
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