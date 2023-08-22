import cv2
import imutils


class LicensePlateDetector():
    def __init__(self, image_path, auto_canny=0, debug=True):
        '''
        Initialization of object
        '''
        self.image = cv2.imread(image_path)
        self.image = imutils.resize(self.image, height=500, width=500)
        self.gray = None

        self.auto_canny = auto_canny
        self.debug = debug

    def debug_imshow(self, title, image):
        '''
        Save image for debugging process
        '''
        if self.debug:
            debug_file_path = f"result/debug-{title}.jpg"
            cv2.imwrite(debug_file_path, image)

    def find_contour(self, keep=30):
        '''
        Find contours on image
        '''
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        self.gray = cv2.bilateralFilter(self.gray, 3, 105, 105)
        self.gray = cv2.GaussianBlur(self.gray, (5, 5), 0)

        # edge detection using canny based on args
        if (self.auto_canny):
            edge = imutils.auto_canny(self.gray)
        else:
            edge = cv2.Canny(self.gray, 170, 200)
        self.debug_imshow("1_canny", edge)

        # find contour based on edged image
        contours, _ = cv2.findContours(
            edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        temp_image = self.image.copy()
        cv2.drawContours(temp_image, contours, -1, (0, 255, 0), 2)
        self.debug_imshow("2_contour", temp_image)

        sorted_contours = sorted(
            contours, key=cv2.contourArea, reverse=True)[:keep]

        return sorted_contours

    def find_plate_by_corner(self, contours):
        '''
        Find plate by finding 4 corner on contours input
        '''
        plate_contour = None
        ok = 0

        for contour in contours:
            contour_perimeter = cv2.arcLength(contour, True)
            epilson = 0.018 * contour_perimeter
            approx = cv2.approxPolyDP(contour, epilson, True)

            if len(approx) == 4:
                plate_contour = approx
                ok = 1
                break

        if not ok:
            return ok, None

        temp_image = self.image.copy()
        cv2.drawContours(temp_image, [plate_contour], -1, (0, 255, 0), 2)
        self.debug_imshow("3a_license_contour", temp_image)

        return ok, plate_contour

    def find_plate_by_ratio(self, contours):
        '''
        Find plate by aspect ratio and highest area on contours input
        '''
        # find plate contour method 2
        # using aspect ratio and contour area to find it
        potential_plate_contours = []
        ok = 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            area = cv2.contourArea(contour)

            if aspect_ratio > 2 and aspect_ratio < 4.5 and area > 1000:
                potential_plate_contours.append(contour)

        if potential_plate_contours:
            plate_contour = max(
                potential_plate_contours, key=cv2.contourArea)
            ok = 1

        if not ok:
            return ok, None

        if plate_contour is not None:
            temp_image = self.image.copy()
            x, y, w, h = cv2.boundingRect(plate_contour)
            cv2.rectangle(temp_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            self.debug_imshow("3b_license_contour", temp_image)

        return ok, plate_contour
