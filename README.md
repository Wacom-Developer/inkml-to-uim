Sample implementation InkML to UIM conversion
=============================================

This is a sample implementation of the conversion of InkML to UIM. 
The implementation is based on the [InkML 1.0 specification](http://www.w3.org/TR/InkML/). 
The implementation is written in Python and uses the [lxml](http://lxml.de/) library for parsing InkML files.

The implementation is based on the following assumptions:
- The InkML file contains a single trace group.
- The trace group contains a single trace.
- The trace contains a sequence of points.

## Wacom Ontology Definition Language (WODL)

At a fundamental level, digital ink can be used producing content, such as text, math, diagrams, sketches etc.

The Wacom Ontology Description Language (WODL) provides a standardized, JSON-based way of annotating ink with a specialized schema definition.

The specification of WODL language is available [here](https://developer-docs.wacom.com/docs/specifications/wodl/).
Some of the most common schema definitions are:
- (Segmentation Schema)[https://developer-docs.wacom.com/docs/specifications/schemas/segmentation/]
- (Math Structures Schema)[https://developer-docs.wacom.com/docs/specifications/schemas/math-structures/]
- (Named Entity Recognition Schema)[https://developer-docs.wacom.com/docs/specifications/schemas/ner/]

## Installation

To install the dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

In the following examples, we will demonstrate how to convert an InkML file from well-known datasets to UIM.

### IAM On-Line Handwriting Database

The implementation supports the [IAM On-Line Handwriting Database](https://fki.tic.heia-fr.ch/databases/iam-on-line-handwriting-database) as a sample dataset for testing the conversion of InkML to UIM.
Its annotations can be converted to Wacom Ontology Definition Language (WODL) segmentation schema, by configuring the InkMLParser as follows:

```python
from pathlib import Path
from typing import Dict, Any, List

from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import SegmentationSchema, IS

from inkml.helpers import build_tree
from inkml.parser import InkMLParser

if __name__ == '__main__':
    parser: InkMLParser = InkMLParser()
    parser.set_typedef_pred(IS)
    parser.register_type('type', 'Document', SegmentationSchema.ROOT)
    parser.register_type('type', 'Formula', SegmentationSchema.MATH_BLOCK)
    parser.register_type('type', 'Arrow', SegmentationSchema.CONNECTOR)
    parser.register_type('type', 'Table', SegmentationSchema.TABLE)
    parser.register_type('type', 'Structure', SegmentationSchema.BORDER)
    parser.register_type('type', 'Diagram', SegmentationSchema.DIAGRAM)
    parser.register_type('type', 'Drawing', SegmentationSchema.DRAWING)
    parser.register_type('type', 'Correction', SegmentationSchema.CORRECTION)
    parser.register_type('type', 'Symbol', '<T>')
    parser.register_type('type', 'Marking', SegmentationSchema.MARKING)
    parser.register_type('type', 'Marking_Bracket', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Encircling', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'encircling')])
    parser.register_type('type', 'Marking_Angle', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Underline', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE,
                                    "underlining")])
    parser.register_type('type', 'Marking_Sideline', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Connection', SegmentationSchema.CONNECTOR)

    parser.register_type('type', 'Textblock', SegmentationSchema.TEXT_REGION)
    parser.register_type('type', 'Textline', SegmentationSchema.TEXT_LINE)
    parser.register_type('type', 'Word', SegmentationSchema.WORD)

    parser.register_type('type', 'Garbage', SegmentationSchema.GARBAGE)
    parser.register_type('type', 'List', SegmentationSchema.LIST)
    parser.register_value('transcription', SegmentationSchema.HAS_CONTENT)

    parser.cropping_ink = False
    parser.cropping_offset = 10
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'inkml' / 'iamondb.inkml')

    structures: List[Dict[str, Any]] = uim_schema_semantics_from(ink_model, "custom")
    build_tree(structures)
    with Path("iamondb.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))
```

The implementation is provided as a sample and may require additional configuration and testing to work with other datasets.
With the `register_type` method, the parser can be configured to map the annotation types to the segmentation schema defined in the WODL.
The `register_value` method can be used to map the annotation values to the content of the segmentation schema.
Note, that this mapping may fully comply with the WODL schema, but it is a sample implementation and may require additional configuration or post-processing.

The sample document from the IAM On-Line Handwriting Database can't be uploaded to the repository due to the license restrictions.

### Kondate

The implementation supports the [Kondate](https://web.tuat.ac.jp/~nakagawa/database/en/kondate_about.html) dataset as a sample dataset for testing the conversion of InkML to UIM.

```python
import uuid
from pathlib import Path

from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel
from uim.model.inkdata.brush import BrushPolygonUri, VectorBrush
from uim.model.semantics.schema import SegmentationSchema, CommonViews

from inkml.parser import InkMLParser

if __name__ == '__main__':
    parser: InkMLParser = InkMLParser()
    # Add a brush specified with shape Uris
    bpu_1: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", min_scale=0.)
    bpu_2: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=0.5", min_scale=4.)
    poly_uris: list = [
        bpu_1, bpu_2
    ]
    vector_brush_1: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyEllipticBrush",
        poly_uris)
    parser.register_brush(brush_uri='default', brush=vector_brush_1)
    parser.use_brush = 'default'
    device_id: str = uuid.uuid4().hex
    parser.update_default_context(sample_rate=80, serial_number=device_id, manufacturer="Test Manufacturer",
                                  model="Test Model")
    parser.content_view = CommonViews.HWR_VIEW.value
    parser.cropping_ink = True
    parser.default_annotation_type = SegmentationSchema.UNLABELED
    parser.default_xy_resolution = 10
    parser.default_position_precision = 3
    parser.default_value_resolution = 42
    # Kondate database is not using namespace
    parser.default_namespace = ''
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'inkml' / 'kondate.inkml')
    with Path("kondate.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))
```

The sample document from the Kondate dataset can't be uploaded to the repository due to the license restrictions.

## IOT Paper Format 

The format encodes the ink as InkML, but additionally it encodes a template image as base64.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<paper xmlns:inkml="http://www.w3.org/2003/InkML"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2003/InkML">
    <resource>
        <templateImage Content-Type="image/bmp">
            <!-- Base64 encoded template -->
        </templateImage>
    </resource>
    <inkml:ink>
        <!-- Ink content encoded as InkML -->
    </inkml:ink>
</paper>
```

This sample implementation provides a way to convert the IOT Paper Format to UIM and extract the template image.

```python
from pathlib import Path
from typing import List

from PIL import Image

from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.helpers.serialize import json_encode, serialize_raw_sensor_data_csv
from uim.model.ink import InkModel
from uim.model.inkinput.inputdata import InkSensorType, Unit

from inkml.iot.parser import IOTPaperParser

if __name__ == '__main__':
        paper_file: Path = Path(__file__).parent / '..' / 'ink' / 'iot' / 'HelloInk.paper'
    parser: IOTPaperParser = IOTPaperParser()

    parser.cropping_ink = False
    parser.cropping_offset = 10
    ink_model: InkModel = parser.parse(paper_file)
    img: Image = parser.parse_template(paper_file)
    with Path("iot.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))
    img.save('template.png')
    layout: List[InkSensorType] = [
        InkSensorType.TIMESTAMP, InkSensorType.X, InkSensorType.Y, InkSensorType.Z,
        InkSensorType.PRESSURE, InkSensorType.ALTITUDE,
        InkSensorType.AZIMUTH
    ]
    # In the Universal Ink Model, the sensor data is in SI units:
    # - timestamp: seconds
    # - x, y, z: meters
    # - pressure: N
    serialize_raw_sensor_data_csv(ink_model, Path('sensor_data.csv'), layout)
    # If you want to convert the data to different units, you can use the following code:
    serialize_raw_sensor_data_csv(ink_model, Path('sensor_data_unit.csv'), layout,
                                    {
                                        InkSensorType.X: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.Y: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.Z: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.TIMESTAMP: Unit.MS  # Convert seconds to milliseconds
                                     })
    # Convert the model to JSON
    with open('ink.json', 'w') as f:
        # json_encode is a helper function to convert the model to JSON
        f.write(json_encode(ink_model))
```

## NOTICE

This implementation is a sample implementation and does not cover all possible cases of InkML files.
There is no guarantee that the implementation will work for all InkML files.
Additional testing and validation may be required to ensure the correctness of the implementation.
Finally, the implementation is provided as-is and without any warranty or support.