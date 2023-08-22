import argparse
import os
from modules.license_plate import LicensePlateDetector


def main():
    parser = argparse.ArgumentParser(
        description="License Plate Detection and OCR")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("-a", "--auto_canny", type=int, default=0,
                        help="Use auto Canny edge detection (1) or not (0)")
    args = parser.parse_args()

    lp = LicensePlateDetector(
        args.image_path, auto_canny=args.auto_canny)

    sorted_contours = lp.find_contour()

    # find plate method 1 by corner
    ok, _ = lp.find_plate_by_corner(sorted_contours)
    print("Method 1: by 4 Corner")

    if not ok:
        print("[FAILED]")
        print("Licensed Plate Contour Not Found")
    else:
        print("[SUCCESS]")
        print("Licensed Plate Contour Found")
    print()

    # find plate method 2 by aspect ratio and area
    ok, _ = lp.find_plate_by_ratio(sorted_contours)
    print("Method 2: by Aspect Ratio and Area")

    if not ok:
        print("[FAILED]")
        print("Licensed Plate Contour Not Found")
    else:
        print("[SUCCESS]")
        print("Licensed Plate Contour Found")
    print()


def clear_folder():
    folder_path = "result"

    files = os.listdir(folder_path)

    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


if __name__ == "__main__":
    print("License Plate Detection\n")
    clear_folder()
    main()

    print("End of Program.")
    print()
