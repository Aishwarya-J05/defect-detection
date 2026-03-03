import os
import xml.etree.ElementTree as ET

# Define your classes
classes = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

def convert_xml_to_yolo(xml_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for xml_file in os.listdir(xml_folder):
        if not xml_file.endswith('.xml'):
            continue

        tree = ET.parse(os.path.join(xml_folder, xml_file))
        root = tree.getroot()

        w = int(root.find('size/width').text)
        h = int(root.find('size/height').text)

        txt_filename = xml_file.replace('.xml', '.txt')

        with open(os.path.join(output_folder, txt_filename), 'w') as f:
            for obj in root.findall('object'):
                cls = obj.find('name').text.lower()
                if cls not in classes:
                    continue
                label = classes.index(cls)

                bbox = obj.find('bndbox')
                xmin = int(bbox.find('xmin').text)
                ymin = int(bbox.find('ymin').text)
                xmax = int(bbox.find('xmax').text)
                ymax = int(bbox.find('ymax').text)

                cx = (xmin + xmax) / 2 / w
                cy = (ymin + ymax) / 2 / h
                nw = (xmax - xmin) / w
                nh = (ymax - ymin) / h

                f.write(f"{label} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

    print(f"Done converting {xml_folder} ✅")

# Run
convert_xml_to_yolo('data/steel/annotations/train/annotations', 'data/steel/labels/train')
convert_xml_to_yolo('data/steel/annotations/val/annotations', 'data/steel/labels/val')
