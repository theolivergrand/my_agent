"""
UI Analysis Agent
Core functionality for analyzing UI elements in images
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Google Cloud Vision imports (optional)
try:
    from google.cloud import vision
    HAS_VISION_API = True
except ImportError:
    HAS_VISION_API = False
    logging.warning("Google Cloud Vision API not available")

from .constants import MOBILE_GAMING_UI_TAXONOMY, ANALYSIS_CONFIG, UI_COLORS
from .config import GOOGLE_CLOUD_CONFIG, ANALYSIS_SETTINGS

class UIAnalysisAgent:
    """
    AI Agent for analyzing UI elements in images
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vision_client = None
        self._initialize_vision_client()
        
    def _initialize_vision_client(self):
        """Initialize Google Cloud Vision client if available"""
        if HAS_VISION_API and GOOGLE_CLOUD_CONFIG.get('credentials_path'):
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                self.logger.info("Google Cloud Vision API initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Vision API: {e}")
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image for UI elements
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'image_path': image_path,
            'text_elements': [],
            'ui_elements': [],
            'colors': [],
            'metadata': {}
        }
        
        try:
            # Load image
            image = Image.open(image_path)
            results['metadata'] = {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode
            }
            
            # Analyze with Vision API if available
            if self.vision_client:
                vision_results = self._analyze_with_vision_api(image_path)
                results['text_elements'] = vision_results.get('text_elements', [])
                results['detected_objects'] = vision_results.get('objects', [])
            
            # Analyze colors
            results['colors'] = self._analyze_colors(image)
            
            # Find potential UI elements using basic computer vision
            results['ui_elements'] = self._find_ui_elements(image)
            
            self.logger.info(f"Analysis completed for {image_path}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {e}")
            results['error'] = str(e)
            
        return results
    
    def _analyze_with_vision_api(self, image_path: str) -> Dict[str, Any]:
        """Analyze image using Google Cloud Vision API"""
        results = {'text_elements': [], 'objects': []}
        
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Text detection
            text_response = self.vision_client.text_detection(image=image)
            for text in text_response.text_annotations:
                if text.description.strip():
                    bounds = text.bounding_poly.vertices
                    results['text_elements'].append({
                        'text': text.description,
                        'bounds': [(v.x, v.y) for v in bounds],
                        'confidence': getattr(text, 'confidence', 0.9)
                    })
            
            # Object detection
            object_response = self.vision_client.object_localization(image=image)
            for obj in object_response.localized_object_annotations:
                bounds = obj.bounding_poly.normalized_vertices
                results['objects'].append({
                    'name': obj.name,
                    'confidence': obj.score,
                    'bounds': [(v.x, v.y) for v in bounds]
                })
                
        except Exception as e:
            self.logger.warning(f"Vision API analysis failed: {e}")
            
        return results
    
    def _analyze_colors(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Extract dominant colors from image"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for performance
            image_small = image.resize((100, 100))
            
            # Get pixel data
            pixels = np.array(image_small).reshape(-1, 3)
            
            # Simple color analysis - get most common colors
            from collections import Counter
            color_counts = Counter(map(tuple, pixels))
            
            colors = []
            for color, count in color_counts.most_common(5):
                colors.append({
                    'rgb': color,
                    'hex': '#{:02x}{:02x}{:02x}'.format(*color),
                    'frequency': count / len(pixels)
                })
            
            return colors
            
        except Exception as e:
            self.logger.warning(f"Color analysis failed: {e}")
            return []
    
    def _find_ui_elements(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Find potential UI elements using basic image processing"""
        elements = []
        
        try:
            # Convert to grayscale for edge detection
            gray = image.convert('L')
            
            # Simple edge detection simulation
            # In a real implementation, you'd use OpenCV or similar
            width, height = gray.size
            
            # Find rectangular regions (simplified)
            # This is a placeholder - real implementation would use contour detection
            sample_regions = [
                {'x': 50, 'y': 50, 'width': 100, 'height': 40, 'type': 'button'},
                {'x': 200, 'y': 100, 'width': 150, 'height': 30, 'type': 'text_field'},
                {'x': 100, 'y': 200, 'width': 80, 'height': 80, 'type': 'icon'},
            ]
            
            for region in sample_regions:
                if (region['x'] + region['width'] <= width and 
                    region['y'] + region['height'] <= height):
                    elements.append({
                        'bounds': [
                            (region['x'], region['y']),
                            (region['x'] + region['width'], region['y']),
                            (region['x'] + region['width'], region['y'] + region['height']),
                            (region['x'], region['y'] + region['height'])
                        ],
                        'type': region['type'],
                        'confidence': 0.6,
                        'area': region['width'] * region['height']
                    })
            
        except Exception as e:
            self.logger.warning(f"UI element detection failed: {e}")
            
        return elements
    
    def create_annotated_image(self, image_path: str, analysis_results: Dict[str, Any], 
                             output_path: str) -> str:
        """
        Create an annotated version of the image with detected elements highlighted
        
        Args:
            image_path: Original image path
            analysis_results: Results from analyze_image()
            output_path: Where to save the annotated image
            
        Returns:
            Path to the annotated image
        """
        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Draw text elements
            for text_elem in analysis_results.get('text_elements', []):
                bounds = text_elem['bounds']
                if bounds:
                    draw.polygon(bounds, outline=UI_COLORS['text'], width=2)
                    if len(bounds) > 0:
                        draw.text(bounds[0], text_elem.get('text', '')[:20], 
                                fill=UI_COLORS['text'], font=font)
            
            # Draw UI elements
            for ui_elem in analysis_results.get('ui_elements', []):
                bounds = ui_elem['bounds']
                if bounds:
                    color = UI_COLORS.get(ui_elem.get('type', 'buttons'), UI_COLORS['buttons'])
                    draw.polygon(bounds, outline=color, width=3)
                    if len(bounds) > 0:
                        draw.text(bounds[0], ui_elem.get('type', 'element'), 
                                fill=color, font=font)
            
            # Add legend
            self._add_legend(draw, font, image.width, image.height)
            
            image.save(output_path)
            self.logger.info(f"Annotated image saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create annotated image: {e}")
            return image_path
    
    def _add_legend(self, draw: ImageDraw.Draw, font, width: int, height: int):
        """Add a legend to the annotated image"""
        legend_items = [
            ("Text", UI_COLORS['text']),
            ("Buttons", UI_COLORS['buttons']),
            ("Containers", UI_COLORS['containers'])
        ]
        
        legend_x = width - 150
        legend_y = 10
        
        for i, (label, color) in enumerate(legend_items):
            y_pos = legend_y + i * 20
            draw.rectangle([legend_x, y_pos, legend_x + 15, y_pos + 15], 
                         outline=color, width=2)
            draw.text((legend_x + 20, y_pos), label, fill=color, font=font)
    
    def save_analysis_data(self, analysis_results: Dict[str, Any], 
                          output_dir: str) -> str:
        """
        Save analysis results to JSON file
        
        Args:
            analysis_results: Results from analyze_image()
            output_dir: Directory to save the data
            
        Returns:
            Path to the saved JSON file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ui_analysis_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analysis data saved to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis data: {e}")
            return ""
    
    def get_taxonomy(self) -> Dict[str, List[str]]:
        """Get the UI element taxonomy"""
        return MOBILE_GAMING_UI_TAXONOMY
    
    def classify_element(self, element_description: str) -> str:
        """
        Classify a UI element based on its description
        
        Args:
            element_description: Description of the element
            
        Returns:
            Category name from taxonomy
        """
        description_lower = element_description.lower()
        
        for category, elements in MOBILE_GAMING_UI_TAXONOMY.items():
            for element in elements:
                if element.replace('_', ' ') in description_lower:
                    return category
        
        return 'interactive'  # Default category