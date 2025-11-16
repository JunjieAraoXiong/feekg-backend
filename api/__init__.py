"""
FE-EKG REST API

Flask-based REST API for serving graph data and visualizations
"""

from .app import create_app

__all__ = ['create_app']
