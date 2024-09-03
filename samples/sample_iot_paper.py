# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from pathlib import Path
from typing import List

from PIL import Image
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel
from uim.model.inkdata.strokes import InkStrokeAttributeType
from uim.model.helpers.serialize import serialize_sensor_data_csv, json_encode

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
    layout: List[InkStrokeAttributeType] = [
        InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y, InkStrokeAttributeType.SENSOR_TIMESTAMP,
        InkStrokeAttributeType.SENSOR_PRESSURE, InkStrokeAttributeType.SENSOR_ALTITUDE,
        InkStrokeAttributeType.SENSOR_AZIMUTH
    ]
    # Serialize the model to CSV
    serialize_sensor_data_csv(ink_model, Path('sensor_data.csv'), layout=layout)
    # Convert the model to JSON
    with open('ink.json', 'w') as f:
        # json_encode is a helper function to convert the model to JSON
        f.write(json_encode(ink_model))
