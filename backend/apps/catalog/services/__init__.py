"""Catalog service exports.

Keep service implementations in focused modules so `apps.catalog.services`
remains a stable import path without duplicating business logic.
"""
from .catalog_service import ProductService, SearchService

__all__ = ['SearchService', 'ProductService']
