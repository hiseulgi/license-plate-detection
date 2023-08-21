import argparse
from modules.license_plate import LicensePlateDetector


def main():
    parser = argparse.ArgumentParser(
        description="License Plate Detection and OCR")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("-a", "--auto_canny", type=int, default=0,
                        help="Use auto Canny edge detection (1) or not (0)")
    parser.add_argument("-b", "--binary", type=int, default=0,
                        help="Use ROI Thresholding (binarization) on OCR process (1) or not (0)")
    parser.add_argument("-d", "--debug", type=int, default=0,
                        help="Show debug image per process (1) or not (0)")
    args = parser.parse_args()

    lp = LicensePlateDetector(
        args.image_path, auto_canny=args.auto_canny, binary=args.binary, debug=args.debug)

    ok, roi, plate_contour = lp.find_plate()
    if not ok:
        print("Licensed Plate Contour Not Found")
        return

    ok, license_plate_text = lp.plate_ocr(roi)

    if ok:
        print("License Plate Detected:", license_plate_text)
    else:
        print("Error or Plate Not Detected")

    lp.draw_result(plate_contour, license_plate_text)
    print("Result image saved as result.jpg")


if __name__ == "__main__":
    main()
