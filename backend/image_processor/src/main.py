import json
import os
import io
import logging
from PIL import Image
from src.aws import AWSContext
from src.processor import ImageProcessor, DitherAlgorithm

logger = logging.getLogger()
logger.setLevel(logging.INFO)

aws_ctx = AWSContext()
processor = ImageProcessor()

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    table_presentations = os.environ.get("PRESENTATIONS_TABLE", "Presentations")
    table_layouts = os.environ.get("LAYOUTS_TABLE", "Layouts")
    artifacts_bucket = os.environ.get("ARTIFACTS_BUCKET", "poster-artifacts")
    
    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            presentation_id = body.get('presentation_id')
            
            if not presentation_id:
                logger.error("No presentation_id in SQS message")
                continue
                
            logger.info(f"Processing presentation: {presentation_id}")
            aws_ctx.update_presentation_status(table_presentations, presentation_id, "PROCESSING")
            
            # 1. Fetch Presentation
            presentation = aws_ctx.get_presentation(table_presentations, presentation_id)
            if not presentation:
                raise ValueError(f"Presentation {presentation_id} not found")
                
            # 2. Fetch Layout
            layout_id = presentation.get('layout_id')
            layout = aws_ctx.get_layout(table_layouts, layout_id)
            if not layout:
                raise ValueError(f"Layout {layout_id} not found")
                
            # 3. Fetch Image
            raw_bucket = presentation.get('s3_bucket')
            raw_key = presentation.get('s3_key')
            img_bytes = aws_ctx.download_image(raw_bucket, raw_key)
            img = Image.open(io.BytesIO(img_bytes))
            
            # Apply cropping/scaling if specified in presentation
            crop_box = presentation.get('crop_box')
            if crop_box:
                # expecting a dict like {'left': x, 'top': y, 'right': w, 'bottom': h}
                box = (crop_box['left'], crop_box['top'], crop_box['right'], crop_box['bottom'])
                img = processor.crop_image(img, box)
                
            # Apply algorithm
            alg_str = presentation.get('dither_algorithm', 'ATKINSON').upper()
            alg = DitherAlgorithm.ATKINSON if alg_str == 'ATKINSON' else DitherAlgorithm.FLOYD_STEINBERG
            
            dithered = processor.dither(img, alg)
            
            # Slice the image
            slices = processor.slice_image(dithered, layout)
            
            # Upload slices and manifests
            base_prefix = f"presentations/{presentation_id}"
            
            for disp_id, disp_img in slices.items():
                # Save as BMP for easy consumption by ESP32/Inkplate
                bmp_io = io.BytesIO()
                disp_img.save(bmp_io, format='BMP')
                
                img_key = f"{base_prefix}/{disp_id}.bmp"
                aws_ctx.upload_display_image(artifacts_bucket, img_key, bmp_io.getvalue())
                
                # Create and upload manifest per display
                manifest = {
                    "presentation_id": presentation_id,
                    "display_id": disp_id,
                    "image_url": f"/{img_key}",  # Relative to CloudFront root
                    "timestamp": context.aws_request_id if hasattr(context, 'aws_request_id') else "local"
                }
                
                manifest_key = f"{base_prefix}/{disp_id}/manifest.json"
                aws_ctx.upload_manifest(artifacts_bucket, manifest_key, manifest)
                
            aws_ctx.update_presentation_status(table_presentations, presentation_id, "COMPLETED", base_prefix)
            logger.info(f"Successfully processed {presentation_id}")
            
        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            if 'presentation_id' in locals():
                aws_ctx.update_presentation_status(table_presentations, presentation_id, "FAILED")
            continue
