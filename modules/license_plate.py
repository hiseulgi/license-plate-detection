import cv2
import numpy as np
import imutils
import easyocr
# this needs to run only once to load the model into memorys
reader = easyocr.Reader(['en'])


class LicensePlateDetector():
    def __init__(self, image_path, auto_canny=0, binary=0, debug=False):
        self.image = cv2.imread(image_path)
        self.image = imutils.resize(self.image, height=500, width=500)

        self.auto_canny = auto_canny
        self.binary = binary
        self.debug = debug

    def debug_imshow(self, title, image):
        if self.debug:
            debug_file_path = f"result/debug-{title}.jpg"
            cv2.imwrite(debug_file_path, image)

    def find_plate(self, keep=30):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        gray = cv2.bilateralFilter(gray, 3, 105, 105)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if (self.auto_canny):
            edge = imutils.auto_canny(gray)
        else:
            edge = cv2.Canny(gray, 170, 200)
        self.debug_imshow("1_canny", edge)

        contours, _ = cv2.findContours(
            edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        temp_image = self.image.copy()
        cv2.drawContours(temp_image, contours, -1, (0, 255, 0), 2)
        self.debug_imshow("2_contour", temp_image)

        sorted_contours = sorted(
            contours, key=cv2.contourArea, reverse=True)[:keep]

        plate_contour = None
        ok = 0

        for c in sorted_contours:
            contour_perimeter = cv2.arcLength(c, True)
            epilson = 0.018 * contour_perimeter
            approx = cv2.approxPolyDP(c, epilson, True)

            if len(approx) == 4:
                plate_contour = approx
                ok = 1
                break

        if not ok:
            return ok, None, None

        temp_image = self.image.copy()
        cv2.drawContours(temp_image, [plate_contour], -1, (0, 255, 0), 2)
        self.debug_imshow("3_license_contour", temp_image)

        x, y, w, h = cv2.boundingRect(plate_contour)
        roi = gray[y:y+h, x:x+w]

        return ok, roi, plate_contour

    def plate_ocr(self, roi):
        if (self.binary):
            _, binary_roi = cv2.threshold(
                roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            closed_roi = cv2.morphologyEx(binary_roi, cv2.MORPH_CLOSE, kernel)

            roi = cv2.morphologyEx(closed_roi, cv2.MORPH_OPEN, kernel)

        self.debug_imshow("4_final_roi", roi)

        try:
            result = reader.readtext(roi)
            if result:  # Check if there's any result
                license_plate_text = result[0][-2]
                license_plate_text = ' '.join([elem[1] for elem in result])
                ok = 1
            else:
                license_plate_text = "Plate not detected"
                ok = 0
        except Exception as e:
            license_plate_text = "Error: " + str(e)
            ok = 0

        return ok, license_plate_text

    def draw_result(self, plate_contour, license_plate_text):
        final_img = self.image.copy()

        x, y, w, h = cv2.boundingRect(plate_contour)
        x1, y1, x2, y2 = x, y, x + w, y + h

        cv2.rectangle(final_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(final_img, license_plate_text, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imwrite("result/result.jpg", final_img)
