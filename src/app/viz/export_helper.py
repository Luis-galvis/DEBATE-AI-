"""
Utilidades de Exportación de Gráficos y Recursos de Video.
Exporta figuras en PNG (300 DPI), SVG, HTML interactivo independiente y empaqueta en ZIP.
"""

import os
import io
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go

from src.config import OUTPUTS_DIR

def export_plotly_figure(
    fig: go.Figure,
    filename_base: str,
    output_dir: Optional[Path] = None,
    dark_mode: bool = True,
    width: int = 1920,
    height: int = 1080,
    scale: float = 3.0
) -> Dict[str, Path]:
    """
    Exporta una figura Plotly a PNG de alta resolución (300 DPI equivalente), SVG y HTML.
    """
    target_dir = output_dir or OUTPUTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    export_fig = go.Figure(fig)
    
    if dark_mode:
        export_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1A202C",
            plot_bgcolor="#2D3748",
            font=dict(color="#F7FAFC", size=14, family="Inter, sans-serif"),
        )
    else:
        export_fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F7FAFC",
            font=dict(color="#1A202C", size=14, family="Inter, sans-serif"),
        )
        
    paths = {}
    
    # 1. Exportar HTML interactivo independiente
    html_path = target_dir / f"{filename_base}.html"
    export_fig.write_html(str(html_path), include_plotlyjs="cdn")
    paths["html"] = html_path
    
    # 2. Exportar PNG y SVG mediante kaleido si está disponible
    try:
        png_path = target_dir / f"{filename_base}.png"
        export_fig.write_image(str(png_path), width=width, height=height, scale=scale)
        paths["png"] = png_path
        
        svg_path = target_dir / f"{filename_base}.svg"
        export_fig.write_image(str(svg_path), width=width, height=height)
        paths["svg"] = svg_path
    except Exception:
        pass
        
    return paths

def create_video_assets_zip() -> bytes:
    """Crea un archivo ZIP en memoria con todas las figuras, reportes y guiones listos para video."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(OUTPUTS_DIR):
            for file in files:
                if file.endswith((".png", ".svg", ".pdf", ".md", ".json")):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(OUTPUTS_DIR)
                    zip_file.write(file_path, arcname=str(rel_path))
                    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
