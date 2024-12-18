# BS Project - ML Side

This is the **Machine Learning (ML)** module of the BS project.

## Notes:
    ⚠ Note: The live video feed functionality is not 100% ready yet and may still be buggy.
For demonstration purposes, the system uses two preconfigured license plate images to showcase the detection and OCR capabilities.

## Models Used
- **Haar Cascade**: Used for object detection, particularly for vehicle license plate detection.

## Libraries Used
- **OpenCV**: Handles computer vision operations like image processing and object detection.
- **pytesseract**: Performs Optical Character Recognition (OCR) to extract text from images.
- **requests**: Manages HTTP operations for communication with external APIs or services.

---

## Installation

### Using `uv`
If you are using `uv` as your package manager:
```bash
uv install
```

### Using `pip`
```bash
pip install -r requirements.txt
```

---

## Running in Demonstration Mode
This will run the system with a preconfigured setup for showcasing object detection and OCR functionality.
```bash
./presentation_run.sh
```
